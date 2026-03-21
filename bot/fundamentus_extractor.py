import logging
from typing import Any

from playwright.async_api import async_playwright

try:
    from bot.logging_utils import audit_event
except ModuleNotFoundError:
    from logging_utils import audit_event

FUNDAMENTUS_FII_URL = "https://www.fundamentus.com.br/fii_resultado.php"
FUNDAMENTUS_BASE_URL = "https://www.fundamentus.com.br/"
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


async def _extract_rows(page: Any, headers: list[str]) -> list[dict[str, str]]:
    rows = page.locator("#tabelaResultado tbody tr")
    row_count = await rows.count()
    logger.info("Iniciando extracao de linhas. Total encontrado: %s", row_count)
    audit_event("rows_found", {"total_rows": row_count})

    results: list[dict[str, str]] = []
    for i in range(row_count):
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
            row_data["detalhe_url"] = f"{FUNDAMENTUS_BASE_URL}{href.lstrip('/')}"
        results.append(row_data)
        audit_event(
            "raw_row_extracted",
            {
                "row_index": i,
                "papel": row_data.get("Papel", ""),
                "row": row_data,
            },
        )

    logger.info("Extracao bruta concluida. Linhas extraidas: %s", len(results))
    return results


async def extract_fii_table_raw(
    headless: bool = True,
    timeout_ms: int = 30_000,
) -> list[dict[str, str]]:
    """Extrai a tabela de FIIs no formato bruto (strings)."""
    logger.info("Iniciando browser Playwright para extracao do Fundamentus.")
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=headless)
        context = await browser.new_context(
            locale="pt-BR",
            timezone_id="America/Sao_Paulo",
        )
        page = await context.new_page()

        await page.goto(
            FUNDAMENTUS_FII_URL,
            wait_until="domcontentloaded",
            timeout=timeout_ms,
        )
        logger.info("Pagina carregada: %s", FUNDAMENTUS_FII_URL)
        audit_event("page_loaded", {"url": FUNDAMENTUS_FII_URL})
        await page.wait_for_selector("#tabelaResultado tbody tr", timeout=timeout_ms)
        logger.info("Tabela de resultado localizada na pagina.")

        headers = await _extract_headers(page)
        data = await _extract_rows(page, headers)

        await context.close()
        await browser.close()
        logger.info("Browser encerrado apos extracao.")
        audit_event("raw_extraction_finished", {"total_rows": len(data)})
        return data
