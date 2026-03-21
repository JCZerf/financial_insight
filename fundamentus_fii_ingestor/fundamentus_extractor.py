import logging
from collections.abc import Awaitable, Callable
from typing import Any

try:
    from fundamentus_fii_ingestor.browser_factory import BrowserFactory
    from fundamentus_fii_ingestor.logging_utils import audit_event
except ModuleNotFoundError:
    from browser_factory import BrowserFactory
    from logging_utils import audit_event

FUNDAMENTUS_FII_URL = "https://www.fundamentus.com.br/fii_resultado.php"
FUNDAMENTUS_BASE_URL = "https://www.fundamentus.com.br/"
GENERAL_PAGE_REFERER = "https://www.google.com.br/"
logger = logging.getLogger(__name__)


async def _extract_headers(page: Any) -> list[str]:
    logger.info("Extraindo cabecalhos da tabela de FIIs.")
    headers = page.locator("#tabelaResultado thead th")
    total = await headers.count()

    extracted: list[str] = []
    for i in range(total):
        text = (await headers.nth(i).inner_text()).strip()
        if not text:
            continue
        if text.lower() == "endereço":
            continue
        extracted.append(text)

    logger.info("Cabecalhos extraidos: %s", extracted)
    audit_event(
        "headers_extracted",
        {
            "total_headers": len(extracted),
            "headers": extracted,
        },
    )
    return extracted


async def extract_fii_table_raw(
    headless: bool = True,
    timeout_ms: int = 30_000,
    page: Any | None = None,
    limit: int | None = None,
    on_row_extracted: Callable[[dict[str, str], int], Awaitable[None] | None] | None = None,
) -> list[dict[str, str]]:
    """Extrai a tabela de FIIs no formato bruto (strings)."""
    if page is not None:
        return await _extract_from_page(page, timeout_ms=timeout_ms, limit=limit, on_row_extracted=on_row_extracted)

    logger.info("Iniciando browser Playwright para extracao do Fundamentus.")
    async with BrowserFactory(headless=headless, timeout_ms=timeout_ms) as browser_factory:
        managed_page = await browser_factory.new_page()
        data = await _extract_from_page(
            managed_page,
            timeout_ms=timeout_ms,
            limit=limit,
            on_row_extracted=on_row_extracted,
        )
        logger.info("Browser encerrado apos extracao.")
        audit_event("raw_extraction_finished", {"total_rows": len(data)})
        return data


async def _extract_from_page(
    page: Any,
    *,
    timeout_ms: int,
    limit: int | None,
    on_row_extracted: Callable[[dict[str, str], int], Awaitable[None] | None] | None,
) -> list[dict[str, str]]:
    await page.goto(
        FUNDAMENTUS_FII_URL,
        wait_until="domcontentloaded",
        timeout=timeout_ms,
        referer=GENERAL_PAGE_REFERER,
    )
    logger.info("Pagina carregada: %s", FUNDAMENTUS_FII_URL)
    audit_event("page_loaded", {"url": FUNDAMENTUS_FII_URL})
    await page.wait_for_selector("#tabelaResultado tbody tr", timeout=timeout_ms)
    logger.info("Tabela de resultado localizada na pagina.")

    headers = await _extract_headers(page)
    rows = page.locator("#tabelaResultado tbody tr")
    row_count = await rows.count()
    logger.info("Iniciando extracao de linhas. Total encontrado: %s", row_count)
    audit_event("rows_found", {"total_rows": row_count})

    results: list[dict[str, str]] = []
    for i in range(row_count):
        if limit is not None and limit > 0 and len(results) >= limit:
            break

        row = rows.nth(i)
        cells = row.locator("td")
        cell_count = await cells.count()

        values: list[str] = []
        for j in range(cell_count):
            value = (await cells.nth(j).inner_text()).strip()
            values.append(value)

        if len(values) > len(headers):
            values = values[: len(headers)]

        paper_link = row.locator("td:nth-child(1) a")
        if await paper_link.count():
            link = paper_link.first
            values[0] = (await link.inner_text()).strip()
            href = await link.get_attribute("href")
        else:
            href = None

        row_data = {
            header: values[idx] if idx < len(values) else ""
            for idx, header in enumerate(headers)
        }
        if href:
            row_data["detail_url"] = f"{FUNDAMENTUS_BASE_URL}{href.lstrip('/')}"

        results.append(row_data)
        audit_event(
            "raw_row_extracted",
            {
                "row_index": i,
                "ticker": row_data.get("Papel", ""),
                "row": row_data,
            },
        )

        if on_row_extracted is not None:
            maybe_awaitable = on_row_extracted(row_data, i)
            if maybe_awaitable is not None:
                await maybe_awaitable

    logger.info("Extracao bruta concluida. Linhas extraidas: %s", len(results))
    return results
