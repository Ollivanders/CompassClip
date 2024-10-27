import json
import logging

from execute.blocks import BlockExport
from constants import BLOCK_COUNT, DEFAULT_TIMEOUT
from dirs import transaction_file, transaction_partition_dir, contract_file, contract_partition_dir
from execute.contract import ContractExport
from execute.rpc_wrappers import get_latest_block_number
from log import basic_log
from mapper.util import hex_to_dec
from output.partition_writer import PartitionedWriter, read_source
from provider import BatchHTTPProvider
from thread_proxy import ThreadLocalProxy
from utils import get_provider_uri, refresh_data_dir
from utils import get_provider_uri
from output.data_functions import contract_partition_key, contract_equality

basic_log()

logger = logging.getLogger("Main")


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

    def partition_func(record):
        return record["hash"]

    def equality_func(record_a, record_b):
        return record_a["hash"] == record_b["hash"]

    writer = PartitionedWriter(transaction_partition_dir(chain, "hash"), partition_func, equality_func)
    writer.write_split(read_source(transaction_file(chain)))
    logger.info("Finished transaction partition ✅")


def init_contract_partition(chain):
    logger.info("Starting contract partition")

    writer = PartitionedWriter(contract_partition_dir(chain, "contract"), contract_partition_key, contract_equality)
    writer.write_split(read_source(contract_file(chain)))
    logger.info("Finished contract partition ✅")


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
    # refresh_data_dir()
    # chain_export(chain, start_block, end_block)
    init_transaction_partition(chain)
    init_contract_partition(chain)


if __name__ == "__main__":
    latest = get_latest("eth")
    start = latest - BLOCK_COUNT
    logger.info(f"Getting from block number {start} - {latest}")
    main("eth", start, latest)

    # interesting
    # main("eth", 21044559, 21044559 + BLOCK_COUNT)
