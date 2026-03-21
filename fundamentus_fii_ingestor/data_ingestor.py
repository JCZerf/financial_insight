import asyncio

try:
    from fundamentus_fii_ingestor.pipeline import run_ingestion
except ModuleNotFoundError:
    from pipeline import run_ingestion


async def main() -> None:
    await run_ingestion()


if __name__ == "__main__":
    asyncio.run(main())
