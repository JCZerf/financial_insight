import asyncio
import logging
import time
from typing import Any

from playwright.async_api import Page, async_playwright

try:
    from bot.logging_utils import audit_event
except ModuleNotFoundError:
    from logging_utils import audit_event

logger = logging.getLogger(__name__)
FUNDAMENTUS_BASE_URL = "https://www.fundamentus.com.br/"


def _build_detail_url(item: dict[str, Any]) -> str:
    explicit_url = item.get("detalhe_url")
    if isinstance(explicit_url, str) and explicit_url.strip():
        return explicit_url

    papel = str(item.get("Papel", "")).strip() or str(item.get("papel", "")).strip()
    return f"{FUNDAMENTUS_BASE_URL}detalhes.php?papel={papel}"


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
    papel = str(item.get("Papel", "")).strip() or str(item.get("papel", "")).strip()
    detail_url = _build_detail_url(item)
    started = time.perf_counter()

    logger.info("Abrindo nova aba para detalhe: %s (%s)", papel, detail_url)
    audit_event(
        "detail_extraction_started",
        {"row_index": idx, "papel": papel, "url": detail_url},
    )

    page = await context.new_page()
    try:
        await page.goto(detail_url, wait_until="domcontentloaded", timeout=timeout_ms)
        await page.wait_for_selector(".conteudo table.w728", timeout=timeout_ms)
        labels = await _extract_label_values(page)

        elapsed_ms = int((time.perf_counter() - started) * 1000)
        logger.info("Detalhe extraido: %s em %sms", papel, elapsed_ms)
        audit_event(
            "detail_extraction_finished",
            {
                "row_index": idx,
                "papel": papel,
                "url": detail_url,
                "duration_ms": elapsed_ms,
                "labels_found": len(labels),
                "status": "success",
            },
        )
        return {
            "papel": papel,
            "detalhe_url": detail_url,
            "raw_labels": labels,
            "status_coleta": "success",
        }
    except Exception as exc:
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        logger.exception("Falha ao extrair detalhe de %s", papel)
        audit_event(
            "detail_extraction_finished",
            {
                "row_index": idx,
                "papel": papel,
                "url": detail_url,
                "duration_ms": elapsed_ms,
                "status": "error",
                "error": str(exc),
            },
        )
        return {
            "papel": papel,
            "detalhe_url": detail_url,
            "raw_labels": {},
            "status_coleta": "error",
            "erro": str(exc),
        }
    finally:
        await page.close()


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

    semaphore = asyncio.Semaphore(concurrency)

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=headless)
        context = await browser.new_context(
            locale="pt-BR",
            timezone_id="America/Sao_Paulo",
        )

        async def run_guarded(item: dict[str, Any], idx: int) -> dict[str, Any]:
            async with semaphore:
                return await _extract_one_detail(context, item, idx, timeout_ms)

        tasks = [run_guarded(item, idx) for idx, item in enumerate(items)]
        results = await asyncio.gather(*tasks)

        await context.close()
        await browser.close()

    logger.info("Extracao de detalhes finalizada. Total processado: %s", len(results))
    audit_event(
        "detail_batch_finished",
        {
            "total": len(results),
            "success": sum(1 for item in results if item.get("status_coleta") == "success"),
            "error": sum(1 for item in results if item.get("status_coleta") == "error"),
        },
    )
    return results
