import argparse
import asyncio

try:
    from bot.data_ingestor import run_ingestion
except ModuleNotFoundError:
    from data_ingestor import run_ingestion


def str_to_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes", "y"}:
        return True
    if normalized in {"false", "0", "no", "n"}:
        return False
    raise argparse.ArgumentTypeError("Use true or false.")


def parse_args() -> argparse.Namespace:
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
        default=8,
        help="Parallel detail workers. Default: 8",
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
