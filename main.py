import shutil
from log_utils import logging_basic_config
from ethereumetl.providers.auto import get_provider_from_uri
from ethereumetl.thread_local_proxy import ThreadLocalProxy

from dirs import DATA_DIR
from export_job import BlockExport
from utils import get_provider_uri

logging_basic_config()


if DATA_DIR.exists():
    shutil.rmtree(DATA_DIR)
DATA_DIR.mkdir(parents=True, exist_ok=True)


def main(chain, start_block, end_block):
    job = BlockExport(
        start_block=start_block,
        end_block=end_block,
        chain=chain,
    )
    job.run()


if __name__ == "__main__":
    main("eth", 21044559, 21044559 + 50)
