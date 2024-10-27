import json
import shutil

from constants import BLOCK_COUNT
from mapper.util import hex_to_dec
from execute.rpc_wrappers import get_latest_block_number
from utils import get_provider_uri
from dirs import DATA_DIR
from execute.blocks import BlockExport
from execute.contract import ContractExport
from log import basic_log

from ethereumetl.providers.auto import get_provider_from_uri
from ethereumetl.thread_local_proxy import ThreadLocalProxy

basic_log()


def refresh_data_dir():
    if DATA_DIR.exists():
        shutil.rmtree(DATA_DIR)
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_latest(chain):
    uri = get_provider_uri(chain)
    provider = ThreadLocalProxy(lambda: get_provider_from_uri(uri, batch=True))
    response = provider.make_batch_request(json.dumps(get_latest_block_number()))
    number = hex_to_dec(response["result"])
    if number is None:
        raise ValueError("Latest block cannot be null")
    return number


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
    latest = get_latest("eth")
    main("eth", latest - BLOCK_COUNT, latest)

    # interesting
    # main("eth", 21044559, 21044559 + BLOCK_COUNT)
