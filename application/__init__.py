from flask import Flask, Response, request
from flask_jsonrpc import JSONRPC
from .storage.reader import PartitionedReader
import json

app = Flask(__name__)
jsonrpc = JSONRPC(app, "/api", enable_web_browsable_api=True)

@jsonrpc.method("eth_getCode")
def get_code(address: str, blockNumber: str) -> str:
    return "STUB METHOD FOR eth_getCode"

@jsonrpc.method("eth_getTransactionByHash")
def get_transaction_by_hash(hash: str) -> str:
    reader = PartitionedReader("application/sampledata/eth/partitioned/", "hash", 4)
    return json.dumps(reader.get_records(hash))
