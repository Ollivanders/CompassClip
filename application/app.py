from flask import Flask, render_template
from flask_jsonrpc import JSONRPC

from dirs import block_partition_dir, contract_partition_dir, transaction_partition_dir
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


def get_reader_blocks(chain, partition):
    return PartitionedReader(
        block_partition_dir(chain, partition),
        lambda x: "0",
        lambda x, y: x["number"] == y["number"],
    )


def get_reader_blocks_hash(chain, partition):
    return PartitionedReader(
        block_partition_dir(chain, partition),
        lambda x: "0",
        lambda x, y: x["hash"] == y["hash"],
    )


@jsonrpc.method("eth_getCode")
def get_code(chain, address: str, blockNumber: str) -> list:
    reader = get_reader_contract(chain, "contract")
    records = reader.get_records({"address": address, "block_number": int(blockNumber)})
    return records[0] if len(records) > 0 else None


@jsonrpc.method("eth_getTransactionByHash")
def get_transaction_by_hash(chain, hash: str) -> dict:
    reader = get_reader_transaction(chain, "hash")
    records = reader.get_records({"hash": hash})
    return records[0] if len(records) > 0 else None


@jsonrpc.method("eth_getBlockByNumber")
def get_block_by_number(chain, number: str) -> dict:
    reader = get_reader_blocks(chain, "block")
    records = reader.get_records({"number": int(number)})
    return records[0] if len(records) > 0 else None

@jsonrpc.method("eth_getBlockByHash")
def get_block_by_hash(chain, hash: str) -> dict:
    reader = get_reader_blocks_hash(chain, "block")
    records = reader.get_records({"hash": hash})
    return records[0] if len(records) > 0 else None


@jsonrpc.method("eth_getBlockTransactionCountByNumber")
def get_block_transaction_count_by_number(chain, number: str) -> dict:
    reader = get_reader_blocks(chain, "block")
    block = reader.get_records({"number": int(number)})[0]
    print(block)
    return {
        "used_transaction_count": block.get("used_transaction_count"),
        "transaction_count": block.get("transaction_count"),
    }


if __name__ == "__main__":
    app.run(debug=True)
