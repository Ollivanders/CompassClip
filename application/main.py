import json
import logging
import shutil

from storage.writer import PartitionedWriter, read_source
from constants import BLOCK_COUNT, DEFAULT_TIMEOUT
from thread_proxy import ThreadLocalProxy
from provider import BatchHTTPProvider
from mapper.util import hex_to_dec
from execute.rpc_wrappers import get_latest_block_number
from utils import get_provider_uri
from dirs import DATA_DIR, transaction_file, transaction_partition_dir
from execute.blocks import BlockExport
from execute.contract import ContractExport
from log import basic_log


basic_log()

logger = logging.getLogger("Main")


def refresh_data_dir():
    if DATA_DIR.exists():
        shutil.rmtree(DATA_DIR)
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_latest(chain):
    uri = get_provider_uri(chain)
    provider = ThreadLocalProxy(
        lambda: BatchHTTPProvider(uri, request_kwargs={"timeout": DEFAULT_TIMEOUT})
    )
    response = provider.make_batch_request(json.dumps(get_latest_block_number()))
    number = hex_to_dec(response["result"])
    if number is None:
        raise ValueError("Latest block cannot be null")
    return number


def init_transaction_partition(chain):
    logger.info("Starting transaction partition")
    # partition transactions
    writer = PartitionedWriter(transaction_partition_dir(chain, "hash"), "hash")
    writer.write_split(read_source(transaction_file(chain)))
    logger.info("Finished transaction partition ✅")


def chain_export(chain, start_block, end_block):
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


def main(chain, start_block, end_block):
    refresh_data_dir()
    chain_export(chain, start_block, end_block)
    init_transaction_partition(chain)


if __name__ == "__main__":
    latest = get_latest("eth")
    print(latest)
    main("eth", latest - BLOCK_COUNT, latest)

    # interesting
    # main("eth", 21044559, 21044559 + BLOCK_COUNT)
