from dataclasses import dataclass, asdict
from typing import Dict, List, Any
from mapper.util import hex_to_dec, to_normalized_address


@dataclass
class EthTx:
    hash: str
    nonce: int
    block_hash: str
    block_number: int
    block_timestamp: int
    transaction_index: int
    from_address: str
    to_address: str
    value: int
    gas: int
    gas_price: int
    input: str
    max_fee_per_gas: int
    max_priority_fee_per_gas: int
    transaction_type: int
    max_fee_per_blob_gas: int
    blob_versioned_hashes: List[str] = None
    access_list: List[Any] = None

    type: str = "transaction"

    def __post_init__(self):
        if self.blob_versioned_hashes is None:
            self.blob_versioned_hashes = []
        if self.access_list is None:
            self.access_list = []

    @classmethod
    def from_json(cls, json_dict: Dict[str, Any], **kwargs):
        return cls(
            hash=json_dict.get("hash"),
            nonce=hex_to_dec(json_dict.get("nonce")),
            block_hash=json_dict.get("blockHash"),
            block_number=hex_to_dec(json_dict.get("blockNumber")),
            block_timestamp=kwargs.get("block_timestamp"),
            transaction_index=hex_to_dec(json_dict.get("transactionIndex")),
            from_address=to_normalized_address(json_dict.get("from")),
            to_address=to_normalized_address(json_dict.get("to")),
            value=hex_to_dec(json_dict.get("value")),
            gas=hex_to_dec(json_dict.get("gas")),
            gas_price=hex_to_dec(json_dict.get("gasPrice")),
            input=json_dict.get("input"),
            transaction_type=hex_to_dec(json_dict.get("type")),
            max_fee_per_gas=hex_to_dec(json_dict.get("maxFeePerGas")),
            max_fee_per_blob_gas=hex_to_dec(json_dict.get("maxFeePerBlobGas")),
            max_priority_fee_per_gas=hex_to_dec(json_dict.get("maxPriorityFeePerGas")),
            access_list=json_dict.get("accessList", []),
            blob_versioned_hashes=json_dict.get("blobVersionedHashes", []),
        )

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result["type"] = "transaction"
        return result
