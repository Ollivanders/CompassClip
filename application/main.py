import shutil
from export.contract import ContractExport
from log_utils import logging_basic_config

from dirs import DATA_DIR
from export.blocks import BlockExport

logging_basic_config()


if DATA_DIR.exists():
    shutil.rmtree(DATA_DIR)
DATA_DIR.mkdir(parents=True, exist_ok=True)


def main(chain, start_block, end_block):
    job = ContractExport(
        chain=chain,
        start_block=start_block,
        end_block=end_block,
    )
    job.run()

    job = BlockExport(
        chain=chain,
        start_block=start_block,
        end_block=end_block,
    )
    job.run()


if __name__ == "__main__":
    main("eth", 21044559, 21044559 + 50)
