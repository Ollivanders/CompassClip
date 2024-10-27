from mapper.util import hex_to_dec, to_normalized_address


from dataclasses import dataclass, asdict
from typing import List, Any, Dict
from mapper.transaction_mapper import EthTx


@dataclass
class EthBlock:
    number: int
    hash: str
    parent_hash: str
    nonce: str
    sha3_uncles: str
    logs_bloom: str
    transactions_root: str
    state_root: str
    receipts_root: str
    miner: str
    difficulty: int
    total_difficulty: int
    size: int
    extra_data: str
    gas_limit: int
    gas_used: int
    timestamp: int
    withdrawals_root: str
    blob_gas_used: int
    excess_blob_gas: int
    transactions: List[EthTx] = None
    withdrawals: List[Dict[str, Any]] = None
    transaction_count: int = 0
    base_fee_per_gas: int = 0

    def __post_init__(self):
        if self.transactions is None:
            self.transactions = []
        if self.withdrawals is None:
            self.withdrawals = []

    @classmethod
    def from_json(cls, json_dict: Dict[str, Any]) -> "EthBlock":
        # Parse withdrawals if present
        withdrawals = []
        if "withdrawals" in json_dict:
            withdrawals = [
                {
                    "index": hex_to_dec(withdrawal.get("index")),
                    "validator_index": hex_to_dec(withdrawal.get("validatorIndex")),
                    "address": withdrawal.get("address"),
                    "amount": hex_to_dec(withdrawal.get("amount")),
                }
                for withdrawal in json_dict["withdrawals"]
            ]

        # Calculate timestamp first as it's needed for transactions
        timestamp = hex_to_dec(json_dict.get("timestamp"))

        # Parse transactions if present
        transactions = []
        transaction_count = 0
        if "transactions" in json_dict:
            transactions = [
                EthTx.from_json(tx, block_timestamp=timestamp)
                for tx in json_dict["transactions"]
                if isinstance(tx, dict)
            ]
            transaction_count = len(json_dict["transactions"])

        return cls(
            number=hex_to_dec(json_dict.get("number")),
            hash=json_dict.get("hash"),
            parent_hash=json_dict.get("parentHash"),
            nonce=json_dict.get("nonce"),
            sha3_uncles=json_dict.get("sha3Uncles"),
            logs_bloom=json_dict.get("logsBloom"),
            transactions_root=json_dict.get("transactionsRoot"),
            state_root=json_dict.get("stateRoot"),
            receipts_root=json_dict.get("receiptsRoot"),
            miner=to_normalized_address(json_dict.get("miner")),
            difficulty=hex_to_dec(json_dict.get("difficulty")),
            total_difficulty=hex_to_dec(json_dict.get("totalDifficulty")),
            size=hex_to_dec(json_dict.get("size")),
            extra_data=json_dict.get("extraData"),
            gas_limit=hex_to_dec(json_dict.get("gasLimit")),
            gas_used=hex_to_dec(json_dict.get("gasUsed")),
            timestamp=timestamp,
            base_fee_per_gas=hex_to_dec(json_dict.get("baseFeePerGas")),
            withdrawals_root=json_dict.get("withdrawalsRoot"),
            blob_gas_used=hex_to_dec(json_dict.get("blobGasUsed")),
            excess_blob_gas=hex_to_dec(json_dict.get("excessBlobGas")),
            transactions=transactions,
            withdrawals=withdrawals,
            transaction_count=transaction_count,
        )

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result["type"] = "block"
        return result


class EthBlockOld:
    def __init__(self):
        self.number = None
        self.hash = None
        self.parent_hash = None
        self.nonce = None
        self.sha3_uncles = None
        self.logs_bloom = None
        self.transactions_root = None
        self.state_root = None
        self.receipts_root = None
        self.miner = None
        self.difficulty = None
        self.total_difficulty = None
        self.size = None
        self.extra_data = None
        self.gas_limit = None
        self.gas_used = None
        self.timestamp = None
        self.withdrawals_root = None

        self.transactions = []
        self.transaction_count = 0
        self.base_fee_per_gas = 0
        self.withdrawals = []

        self.blob_gas_used = None
        self.excess_blob_gas = None


# class BlockMapper:
#     def __init__(self):
#         self.transaction_mapper = TransactionMapper()

#     def json_dict_to_block(self, json_dict):
#         block = EthBlock()
#         block.number = hex_to_dec(json_dict.get("number"))  # type: ignore
#         block.hash = json_dict.get("hash")
#         block.parent_hash = json_dict.get("parentHash")
#         block.nonce = json_dict.get("nonce")
#         block.sha3_uncles = json_dict.get("sha3Uncles")
#         block.logs_bloom = json_dict.get("logsBloom")
#         block.transactions_root = json_dict.get("transactionsRoot")
#         block.state_root = json_dict.get("stateRoot")
#         block.receipts_root = json_dict.get("receiptsRoot")
#         block.miner = to_normalized_address(json_dict.get("miner"))  # type: ignore
#         block.difficulty = hex_to_dec(json_dict.get("difficulty"))  # type: ignore
#         block.total_difficulty = hex_to_dec(json_dict.get("totalDifficulty"))  # type: ignore
#         block.size = hex_to_dec(json_dict.get("size"))  # type: ignore
#         block.extra_data = json_dict.get("extraData")
#         block.gas_limit = hex_to_dec(json_dict.get("gasLimit"))  # type: ignore
#         block.gas_used = hex_to_dec(json_dict.get("gasUsed"))  # type: ignore
#         block.timestamp = hex_to_dec(json_dict.get("timestamp"))  # type: ignore
#         block.base_fee_per_gas = hex_to_dec(json_dict.get("baseFeePerGas"))  # type: ignore
#         block.withdrawals_root = json_dict.get("withdrawalsRoot")
#         block.blob_gas_used = hex_to_dec(json_dict.get("blobGasUsed"))  # type: ignore
#         block.excess_blob_gas = hex_to_dec(json_dict.get("excessBlobGas"))  # type: ignore

#         if "transactions" in json_dict:
#             block.transactions = [
#                 EthTx.from_json(tx, block_timestamp=block.timestamp)
#                 for tx in json_dict["transactions"]
#                 if isinstance(tx, dict)
#             ]

#             block.transaction_count = len(json_dict["transactions"])

#         if "withdrawals" in json_dict:
#             block.withdrawals = self.parse_withdrawals(json_dict["withdrawals"])

#         return block

#     def parse_withdrawals(self, withdrawals):
#         return [
#             {
#                 "index": hex_to_dec(withdrawal["index"]),
#                 "validator_index": hex_to_dec(withdrawal["validatorIndex"]),
#                 "address": withdrawal["address"],
#                 "amount": hex_to_dec(withdrawal["amount"]),
#             }
#             for withdrawal in withdrawals
#         ]

#     def to_dict(self, block):
#         return {
#             "type": "block",
#             "number": block.number,
#             "hash": block.hash,
#             "parent_hash": block.parent_hash,
#             "nonce": block.nonce,
#             "sha3_uncles": block.sha3_uncles,
#             "logs_bloom": block.logs_bloom,
#             "transactions_root": block.transactions_root,
#             "state_root": block.state_root,
#             "receipts_root": block.receipts_root,
#             "miner": block.miner,
#             "difficulty": block.difficulty,
#             "total_difficulty": block.total_difficulty,
#             "size": block.size,
#             "extra_data": block.extra_data,
#             "gas_limit": block.gas_limit,
#             "gas_used": block.gas_used,
#             "timestamp": block.timestamp,
#             "transaction_count": block.transaction_count,
#             "base_fee_per_gas": block.base_fee_per_gas,
#             "withdrawals_root": block.withdrawals_root,
#             "withdrawals": block.withdrawals,
#             "blob_gas_used": block.blob_gas_used,
#             "excess_blob_gas": block.excess_blob_gas,
#         }
