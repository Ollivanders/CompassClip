from ethereumetl.domain.transaction import EthTransaction
from ethereumetl.utils import hex_to_dec, to_normalized_address


class TransactionMapper(object):
    fields = [
        "hash",
        "nonce",
        "block_hash",
        "block_number",
        "transaction_index",
        "from_address",
        "to_address",
        "value",
        "gas",
        "gas_price",
        "input",
        "block_timestamp",
        "max_fee_per_gas",
        "max_priority_fee_per_gas",
        "transaction_type",
        "max_fee_per_blob_gas",
        "blob_versioned_hashes",
        "access_list",
    ]

    def json_dict_to_transaction(self, json_dict, **kwargs):
        transaction = EthTransaction()
        transaction.hash = json_dict.get("hash")
        transaction.nonce = hex_to_dec(json_dict.get("nonce"))  # type: ignore
        transaction.block_hash = json_dict.get("blockHash")
        transaction.block_number = hex_to_dec(json_dict.get("blockNumber"))  # type: ignore
        transaction.block_timestamp = kwargs.get("block_timestamp")  # type: ignore
        transaction.transaction_index = hex_to_dec(json_dict.get("transactionIndex"))  # type: ignore
        transaction.from_address = to_normalized_address(json_dict.get("from"))  # type: ignore
        transaction.to_address = to_normalized_address(json_dict.get("to"))  # type: ignore
        transaction.value = hex_to_dec(json_dict.get("value"))  # type: ignore
        transaction.gas = hex_to_dec(json_dict.get("gas"))  # type: ignore
        transaction.gas_price = hex_to_dec(json_dict.get("gasPrice"))  # type: ignore
        transaction.input = json_dict.get("input")
        transaction.max_fee_per_gas = hex_to_dec(json_dict.get("maxFeePerGas"))  # type: ignore
        transaction.max_priority_fee_per_gas = hex_to_dec(  # type: ignore
            json_dict.get("maxPriorityFeePerGas")
        )
        transaction.transaction_type = hex_to_dec(json_dict.get("type"))  # type: ignore
        transaction.max_fee_per_blob_gas = hex_to_dec(json_dict.get("maxFeePerBlobGas"))  # type: ignore

        transaction.access_list = json_dict.get("accessList", [])  # type: ignore

        if "blobVersionedHashes" in json_dict and isinstance(
            json_dict["blobVersionedHashes"], list
        ):
            transaction.blob_versioned_hashes = json_dict["blobVersionedHashes"]

        return transaction

    def to_dict(self, transaction):
        return {
            "type": "transaction",
            "hash": transaction.hash,
            "nonce": transaction.nonce,
            "block_hash": transaction.block_hash,
            "block_number": transaction.block_number,
            "block_timestamp": transaction.block_timestamp,
            "transaction_index": transaction.transaction_index,
            "from_address": transaction.from_address,
            "to_address": transaction.to_address,
            "value": transaction.value,
            "gas": transaction.gas,
            "gas_price": transaction.gas_price,
            "input": transaction.input,
            "max_fee_per_gas": transaction.max_fee_per_gas,
            "max_priority_fee_per_gas": transaction.max_priority_fee_per_gas,
            "transaction_type": transaction.transaction_type,
            "max_fee_per_blob_gas": transaction.max_fee_per_blob_gas,
            "blob_versioned_hashes": transaction.blob_versioned_hashes,
            "access_list": transaction.access_list,
        }
