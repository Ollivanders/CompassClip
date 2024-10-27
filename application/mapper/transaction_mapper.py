from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from mapper.util import hex_to_dec, to_normalized_address


@dataclass
class EthTx:
    hash: Optional[str] = None
    nonce: Optional[int] = None
    block_hash: Optional[str] = None
    block_number: Optional[int] = None
    block_timestamp: Optional[int] = None
    transaction_index: Optional[int] = None
    from_address: Optional[str] = None
    to_address: Optional[str] = None
    value: Optional[int] = None
    gas: Optional[int] = None
    gas_price: Optional[int] = None
    input: Optional[str] = None
    max_fee_per_gas: Optional[int] = None
    max_priority_fee_per_gas: Optional[int] = None
    transaction_type: Optional[int] = None
    max_fee_per_blob_gas: Optional[int] = None
    blob_versioned_hashes: Optional[List[str]] = None
    access_list: Optional[List[Any]] = None
    type: str = "transaction"

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
