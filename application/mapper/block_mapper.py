from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from mapper.transaction_mapper import EthTx
from mapper.util import hex_to_dec, to_normalized_address


@dataclass
class EthBlock:
    number: Optional[int] = None
    hash: Optional[str] = None
    parent_hash: Optional[str] = None
    nonce: Optional[str] = None
    sha3_uncles: Optional[str] = None
    logs_bloom: Optional[str] = None
    transactions_root: Optional[str] = None
    state_root: Optional[str] = None
    receipts_root: Optional[str] = None
    miner: Optional[str] = None
    difficulty: Optional[int] = None
    total_difficulty: Optional[int] = None
    size: Optional[int] = None
    extra_data: Optional[str] = None
    gas_limit: Optional[int] = None
    gas_used: Optional[int] = None
    timestamp: Optional[int] = None
    withdrawals_root: Optional[str] = None
    blob_gas_used: Optional[int] = None
    excess_blob_gas: Optional[int] = None
    transactions: Optional[List[EthTx]] = None
    withdrawals: Optional[List[Dict[str, Any]]] = None
    transaction_count: Optional[int] = 0
    base_fee_per_gas: Optional[int] = 0

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
