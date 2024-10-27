from ethereumetl.domain.block import EthBlock
from ethereumetl.utils import hex_to_dec, to_normalized_address

from mapper.transaction_mapper import TransactionMapper


class BlockMapper(object):
    fields = [
        "number",
        "hash",
        "parent_hash",
        "nonce",
        "sha3_uncles",
        "logs_bloom",
        "transactions_root",
        "state_root",
        "receipts_root",
        "miner",
        "difficulty",
        "total_difficulty",
        "size",
        "extra_data",
        "gas_limit",
        "gas_used",
        "timestamp",
        "transaction_count",
        "base_fee_per_gas",
        "withdrawals_root",
        "withdrawals",
        "blob_gas_used",
        "excess_blob_gas",
    ]

    def __init__(self, transaction_mapper=None):
        if transaction_mapper is None:
            self.transaction_mapper = TransactionMapper()
        else:
            self.transaction_mapper = transaction_mapper

    def json_dict_to_block(self, json_dict):
        block = EthBlock()
        block.number = hex_to_dec(json_dict.get("number"))  # type: ignore
        block.hash = json_dict.get("hash")
        block.parent_hash = json_dict.get("parentHash")
        block.nonce = json_dict.get("nonce")
        block.sha3_uncles = json_dict.get("sha3Uncles")
        block.logs_bloom = json_dict.get("logsBloom")
        block.transactions_root = json_dict.get("transactionsRoot")
        block.state_root = json_dict.get("stateRoot")
        block.receipts_root = json_dict.get("receiptsRoot")
        block.miner = to_normalized_address(json_dict.get("miner"))  # type: ignore
        block.difficulty = hex_to_dec(json_dict.get("difficulty"))  # type: ignore
        block.total_difficulty = hex_to_dec(json_dict.get("totalDifficulty"))  # type: ignore
        block.size = hex_to_dec(json_dict.get("size"))  # type: ignore
        block.extra_data = json_dict.get("extraData")
        block.gas_limit = hex_to_dec(json_dict.get("gasLimit"))  # type: ignore
        block.gas_used = hex_to_dec(json_dict.get("gasUsed"))  # type: ignore
        block.timestamp = hex_to_dec(json_dict.get("timestamp"))  # type: ignore
        block.base_fee_per_gas = hex_to_dec(json_dict.get("baseFeePerGas"))  # type: ignore
        block.withdrawals_root = json_dict.get("withdrawalsRoot")
        block.blob_gas_used = hex_to_dec(json_dict.get("blobGasUsed"))  # type: ignore
        block.excess_blob_gas = hex_to_dec(json_dict.get("excessBlobGas"))  # type: ignore

        if "transactions" in json_dict:
            block.transactions = [
                self.transaction_mapper.json_dict_to_transaction(
                    tx, block_timestamp=block.timestamp
                )
                for tx in json_dict["transactions"]
                if isinstance(tx, dict)
            ]

            block.transaction_count = len(json_dict["transactions"])

        if "withdrawals" in json_dict:
            block.withdrawals = self.parse_withdrawals(json_dict["withdrawals"])

        return block

    def parse_withdrawals(self, withdrawals):
        return [
            {
                "index": hex_to_dec(withdrawal["index"]),
                "validator_index": hex_to_dec(withdrawal["validatorIndex"]),
                "address": withdrawal["address"],
                "amount": hex_to_dec(withdrawal["amount"]),
            }
            for withdrawal in withdrawals
        ]

    def block_to_dict(self, block):
        return {
            "type": "block",
            "number": block.number,
            "hash": block.hash,
            "parent_hash": block.parent_hash,
            "nonce": block.nonce,
            "sha3_uncles": block.sha3_uncles,
            "logs_bloom": block.logs_bloom,
            "transactions_root": block.transactions_root,
            "state_root": block.state_root,
            "receipts_root": block.receipts_root,
            "miner": block.miner,
            "difficulty": block.difficulty,
            "total_difficulty": block.total_difficulty,
            "size": block.size,
            "extra_data": block.extra_data,
            "gas_limit": block.gas_limit,
            "gas_used": block.gas_used,
            "timestamp": block.timestamp,
            "transaction_count": block.transaction_count,
            "base_fee_per_gas": block.base_fee_per_gas,
            "withdrawals_root": block.withdrawals_root,
            "withdrawals": block.withdrawals,
            "blob_gas_used": block.blob_gas_used,
            "excess_blob_gas": block.excess_blob_gas,
        }
