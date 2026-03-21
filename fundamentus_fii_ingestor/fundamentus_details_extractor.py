import asyncio
import logging
import time
from typing import Any

from playwright.async_api import Page

try:
    from fundamentus_fii_ingestor.logging_utils import audit_event
except ModuleNotFoundError:
    from logging_utils import audit_event

logger = logging.getLogger(__name__)
FUNDAMENTUS_BASE_URL = "https://www.fundamentus.com.br/"
DETAIL_PAGE_REFERER = "https://www.fundamentus.com.br/fii_resultado.php"


def _build_detail_url(item: dict[str, Any]) -> str:
    explicit_url = item.get("detail_url") or item.get("detalhe_url")
    if isinstance(explicit_url, str) and explicit_url.strip():
        return explicit_url

    ticker = str(item.get("Papel", "")).strip() or str(item.get("ticker", "")).strip()
    return f"{FUNDAMENTUS_BASE_URL}detalhes.php?papel={ticker}"


async def _extract_label_values(page: Page) -> dict[str, list[str]]:
    pairs: dict[str, list[str]] = {}
    rows = page.locator(".conteudo table.w728 tr")
    total_rows = await rows.count()

    for i in range(total_rows):
        row = rows.nth(i)
        cells = row.locator("td")
        total_cells = await cells.count()
        idx = 0

        while idx < total_cells:
            cell = cells.nth(idx)
            class_name = (await cell.get_attribute("class")) or ""
            if "label" not in class_name:
                idx += 1
                continue

            label_text = (await cell.inner_text()).strip()
            if not label_text:
                idx += 1
                continue

            value_text = ""
            next_idx = idx + 1
            if next_idx < total_cells:
                next_cell = cells.nth(next_idx)
                next_class = (await next_cell.get_attribute("class")) or ""
                if "data" in next_class:
                    value_text = (await next_cell.inner_text()).strip()
                    idx += 2
                else:
                    idx += 1
            else:
                idx += 1

            if label_text not in pairs:
                pairs[label_text] = []
            pairs[label_text].append(value_text)

    return pairs


async def _extract_one_detail(
    context: Any,
    item: dict[str, Any],
    idx: int,
    timeout_ms: int,
) -> dict[str, Any]:
    ticker = str(item.get("Papel", "")).strip() or str(item.get("ticker", "")).strip()
    detail_url = _build_detail_url(item)
    started = time.perf_counter()

    logger.info("Abrindo nova aba para detalhe: %s (%s)", ticker, detail_url)
    audit_event(
        "detail_extraction_started",
        {"row_index": idx, "ticker": ticker, "url": detail_url},
    )

    page = await context.new_page()
    try:
        await page.goto(
            detail_url,
            wait_until="domcontentloaded",
            timeout=timeout_ms,
            referer=DETAIL_PAGE_REFERER,
        )
        await page.wait_for_selector(".conteudo table.w728", timeout=timeout_ms)
        labels = await _extract_label_values(page)

        elapsed_ms = int((time.perf_counter() - started) * 1000)
        logger.info("Detalhe extraido: %s em %sms", ticker, elapsed_ms)
        audit_event(
            "detail_extraction_finished",
            {
                "row_index": idx,
                "ticker": ticker,
                "url": detail_url,
                "duration_ms": elapsed_ms,
                "labels_found": len(labels),
                "status": "success",
            },
        )
        return {
            "ticker": ticker,
            "detail_url": detail_url,
            "raw_labels": labels,
            "collection_status": "success",
        }
    except Exception as exc:
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        logger.exception("Falha ao extrair detalhe de %s", ticker)
        audit_event(
            "detail_extraction_finished",
            {
                "row_index": idx,
                "ticker": ticker,
                "url": detail_url,
                "duration_ms": elapsed_ms,
                "status": "error",
                "error": str(exc),
            },
        )
        return {
            "ticker": ticker,
            "detail_url": detail_url,
            "raw_labels": {},
            "collection_status": "error",
            "error": str(exc),
        }
    finally:
        await page.close()


async def extract_one_detail(
    context: Any,
    item: dict[str, Any],
    idx: int,
    timeout_ms: int = 30_000,
) -> dict[str, Any]:
    """Extrai um único detalhe reutilizando um context já aberto."""
    return await _extract_one_detail(context, item, idx, timeout_ms)


async def extract_fii_details_from_context_in_parallel(
    context: Any,
    items: list[dict[str, Any]],
    timeout_ms: int = 30_000,
    concurrency: int = 8,
) -> list[dict[str, Any]]:
    """Extrai detalhes em paralelo reaproveitando o mesmo browser context."""
    logger.info(
        "Iniciando extracao de detalhes em paralelo (contexto compartilhado). Total: %s | concorrencia: %s",
        len(items),
        concurrency,
    )
    semaphore = asyncio.Semaphore(concurrency)

    async def run_guarded(item: dict[str, Any], idx: int) -> dict[str, Any]:
        async with semaphore:
            return await _extract_one_detail(context, item, idx, timeout_ms)

    tasks = [run_guarded(item, idx) for idx, item in enumerate(items)]
    results = await asyncio.gather(*tasks)
    logger.info("Extracao de detalhes finalizada. Total processado: %s", len(results))
    audit_event(
        "detail_batch_finished",
        {
            "total": len(results),
            "success": sum(1 for item in results if item.get("collection_status") == "success"),
            "error": sum(1 for item in results if item.get("collection_status") == "error"),
        },
    )
    return results


async def extract_fii_details_in_parallel(
    items: list[dict[str, Any]],
    headless: bool = True,
    timeout_ms: int = 30_000,
    concurrency: int = 8,
) -> list[dict[str, Any]]:
    logger.info(
        "Iniciando extracao de detalhes em paralelo. Total: %s | concorrencia: %s",
        len(items),
        concurrency,
    )
    try:
        from fundamentus_fii_ingestor.browser_factory import BrowserFactory
    except ModuleNotFoundError:
        from browser_factory import BrowserFactory

    async with BrowserFactory(headless=headless, timeout_ms=timeout_ms) as browser_factory:
        context = await browser_factory.start()
        return await extract_fii_details_from_context_in_parallel(
            context=context,
            items=items,
            timeout_ms=timeout_ms,
            concurrency=concurrency,
        )
