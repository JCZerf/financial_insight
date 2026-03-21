import argparse
import asyncio

try:
    from fundamentus_fii_ingestor.config import DEFAULT_MAX_DETAIL_TABS, env_int
    from fundamentus_fii_ingestor.pipeline import run_ingestion
except ModuleNotFoundError:
    from config import DEFAULT_MAX_DETAIL_TABS, env_int
    from pipeline import run_ingestion


def str_to_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes", "y"}:
        return True
    if normalized in {"false", "0", "no", "n"}:
        return False
    raise argparse.ArgumentTypeError("Use true or false.")


def parse_args() -> argparse.Namespace:
    default_concurrency = env_int("BOT_MAX_DETAIL_TABS", DEFAULT_MAX_DETAIL_TABS)
    parser = argparse.ArgumentParser(
        description="Financial Insight FII ingestor runner",
    )
    parser.add_argument(
        "--detailed",
        type=str_to_bool,
        default=True,
        help="Collect detailed pages too (true/false). Default: true",
    )
    parser.add_argument(
        "--details-only",
        action="store_true",
        help="Collect only details snapshot (skips general snapshot).",
    )
    parser.add_argument(
        "--headless",
        type=str_to_bool,
        default=True,
        help="Run browser in headless mode (true/false). Default: true",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=default_concurrency,
        help=f"Parallel detail workers / max open detail tabs. Default: BOT_MAX_DETAIL_TABS or {default_concurrency}",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Limit how many tickers will be processed (0 = no limit).",
    )
    return parser.parse_args()


async def async_main() -> None:
    args = parse_args()
    await run_ingestion(
        detailed=args.detailed,
        details_only=args.details_only,
        headless=args.headless,
        concurrency=args.concurrency,
        limit=args.limit if args.limit > 0 else None,
    )


if __name__ == "__main__":
    asyncio.run(async_main())
