import shutil

from file_exporter import FileExporter
from constants import BLOCK_COUNT
from dirs import DATA_DIR
from execute.blocks import BlockExport
from execute.contract import ContractExport
from log_utils import logging_basic_config

logging_basic_config()


def refresh_data_dir():
    if DATA_DIR.exists():
        shutil.rmtree(DATA_DIR)
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def main(chain, start_block, end_block):
    refresh_data_dir()
    jobs = [
        BlockExport(
            chain=chain,
            start_block=start_block,
            end_block=end_block,
        ),
        ContractExport(
            chain=chain,
            start_block=start_block,
            end_block=end_block,
        ),
    ]
    for job in jobs:
        job.run()


if __name__ == "__main__":
    main("eth", 21044559, 21044559 + BLOCK_COUNT)
