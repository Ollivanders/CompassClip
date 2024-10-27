from dirs import transaction_partition_dir
from flask import Flask
from flask_jsonrpc import JSONRPC
from .partition_read import PartitionedReader

app = Flask(__name__)
jsonrpc = JSONRPC(app, "/api", enable_web_browsable_api=True)

TRANSACTION_READER = PartitionedReader(transaction_partition_dir("eth", "hash"), "hash")


def get_reader(chain, partition):
    return PartitionedReader(transaction_partition_dir(chain, partition), partition)


chain = "eth"


@jsonrpc.method("eth_getCode")
def get_code(address: str, blockNumber: str) -> list:
    reader = get_reader(chain, "hash")
    return reader.get_records(address)


@jsonrpc.method("eth_getTransactionByHash")
def get_transaction_by_hash(hash: str) -> list:
    reader = get_reader(chain, "hash")
    return reader.get_records(hash)
