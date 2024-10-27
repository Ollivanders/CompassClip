from mapper.util import hex_to_dec, to_normalized_address


from dataclasses import dataclass, asdict
from typing import List, Any, Dict
from mapper.transaction_mapper import EthTx


@dataclass
class EthBlock:
    number: int | None = None
    hash: str | None = None
    parent_hash: str | None = None
    nonce: str | None = None
    sha3_uncles: str | None = None
    logs_bloom: str | None = None
    transactions_root: str | None = None
    state_root: str | None = None
    receipts_root: str | None = None
    miner: str | None = None
    difficulty: int | None = None
    total_difficulty: int | None = None
    size: int | None = None
    extra_data: str | None = None
    gas_limit: int | None = None
    gas_used: int | None = None
    timestamp: int | None = None
    withdrawals_root: str | None = None
    blob_gas_used: int | None = None
    excess_blob_gas: int | None = None
    transactions: List[EthTx] = []
    withdrawals: List[Dict[str, Any]] = []
    transaction_count: int = 0
    base_fee_per_gas: int = 0

    type: str = "block"

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
            base_fee_per_gas=hex_to_dec(json_dict.get("baseFeePerGas")),  # type: ignore
            withdrawals_root=json_dict.get("withdrawalsRoot"),
            blob_gas_used=hex_to_dec(json_dict.get("blobGasUsed")),
            excess_blob_gas=hex_to_dec(json_dict.get("excessBlobGas")),
            transactions=transactions,
            withdrawals=withdrawals,
            transaction_count=transaction_count,
        )

    def to_dict(self) -> Dict[str, Any]:
        result = {k: v for k, v in asdict(self).items() if k != "transactions"}
        return result
