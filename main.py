from pathlib import Path
import shutil
from ethereumetl.jobs.exporters.blocks_and_transactions_item_exporter import (
    blocks_and_transactions_item_exporter,
)
from blockchainetl.logging_utils import logging_basic_config
from ethereumetl.providers.auto import get_provider_from_uri
from ethereumetl.thread_local_proxy import ThreadLocalProxy

from export_job import BlockExport

logging_basic_config()

CHAIN_PROVIDER_URI = {
    "ethereum": "https://rpc.ankr.com/eth",
}
BATCH_SIZE = 1

THIS_DIR = Path(__file__).resolve().parent
DATA_DIR = THIS_DIR / "data"
if DATA_DIR.exists():
    shutil.rmtree(DATA_DIR)
DATA_DIR.mkdir(parents=True, exist_ok=True)


def main(
    start_block,
    end_block,
):
    job = BlockExport(
        start_block=start_block,
        end_block=end_block,
        batch_size=min(BATCH_SIZE, end_block - start_block),
        batch_web3_provider=ThreadLocalProxy(
            lambda: get_provider_from_uri(CHAIN_PROVIDER_URI["ethereum"], batch=True)
        ),
        max_workers=5,
        item_exporter=blocks_and_transactions_item_exporter(
            DATA_DIR / "blocks.json",
            DATA_DIR / "transactions.json",
        ),
        export_blocks=True,
        export_transactions=True,
    )
    job.run()


if __name__ == "__main__":
    main(21044559, 21044559 + 50)
