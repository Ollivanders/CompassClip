from .dirs import transaction_partition_dir, contract_partition_dir
from flask import Flask
from flask_jsonrpc import JSONRPC
from .partition_read import PartitionedReader
from .output.data_functions import contract_partition_key, contract_equality

app = Flask(__name__)
jsonrpc = JSONRPC(app, "/api", enable_web_browsable_api=True)

# TRANSACTION_READER = PartitionedReader(transaction_partition_dir("eth", "hash"), "hash")


def get_reader_transaction(chain, partition):
    return PartitionedReader(transaction_partition_dir(chain, partition), lambda x: x["hash"], lambda x, y: x["hash"] == y["hash"])

def get_reader_contract(chain, partition):
    return PartitionedReader(contract_partition_dir(chain, partition), contract_partition_key, contract_equality)


chain = "eth"


@jsonrpc.method("eth_getCode")
def get_code(address: str, blockNumber: str) -> list:
    reader = get_reader_contract(chain, "contract")
    return reader.get_records({"address": address, "block_number": int(blockNumber)})


@jsonrpc.method("eth_getTransactionByHash")
def get_transaction_by_hash(hash: str) -> list:
    reader = get_reader_transaction(chain, "hash")
    return reader.get_records({"hash": hash})
