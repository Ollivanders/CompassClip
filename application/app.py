from flask import Flask, render_template
from flask_jsonrpc import JSONRPC

from dirs import contract_partition_dir, transaction_partition_dir
from output.data_functions import contract_equality, contract_partition_key
from partition_read import PartitionedReader

app = Flask(__name__)
jsonrpc = JSONRPC(app, "/api", enable_web_browsable_api=True)


@app.route("/")
def index():
    return render_template("index.html")


def get_reader_transaction(chain, partition):
    return PartitionedReader(
        transaction_partition_dir(chain, partition),
        lambda x: x["hash"],
        lambda x, y: x["hash"] == y["hash"],
    )


def get_reader_contract(chain, partition):
    return PartitionedReader(
        contract_partition_dir(chain, partition),
        contract_partition_key,
        contract_equality,
    )


@jsonrpc.method("eth_getCode")
def get_code(chain, address: str, blockNumber: str) -> list:
    reader = get_reader_contract(chain, "contract")
    return reader.get_records({"address": address, "block_number": int(blockNumber)})


@jsonrpc.method("eth_getTransactionByHash")
def get_transaction_by_hash(chain, hash: str) -> list:
    reader = get_reader_transaction(chain, "hash")
    return reader.get_records({"hash": hash})


@jsonrpc.method("eth_getBlockByNumber")
def get_block_by_number(chain, number: str) -> list:
    reader = get_reader_transaction(chain, "block")
    return reader.get_records({"block": number})


if __name__ == "__main__":
    app.run(debug=True)
