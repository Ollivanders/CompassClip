from flask import Flask
from flask_jsonrpc import JSONRPC
from .storage.reader import PartitionedReader

app = Flask(__name__)
jsonrpc = JSONRPC(app, "/api", enable_web_browsable_api=True)


@jsonrpc.method("eth_getCode")
def get_code(address: str, blockNumber: str) -> list:
    reader = PartitionedReader(
        "application/sampledata/eth/partitioned-contracts/", "address"
    )
    return reader.get_records(address)


@jsonrpc.method("eth_getTransactionByHash")
def get_transaction_by_hash(hash: str) -> list:
    reader = PartitionedReader("application/sampledata/eth/partitioned/", "hash")
    return reader.get_records(hash)
