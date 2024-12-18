from dataclasses import dataclass, asdict
from typing import List, Optional


@dataclass
class EthContract:
    address: str
    bytecode: str
    block_number: int
    function_sighashes: Optional[List[str]] = None
    is_erc20: bool = False
    is_erc721: bool = False
    type: str = "contract"

    def __post_init__(self):
        if self.function_sighashes is None:
            self.function_sighashes = []

    @classmethod
    def from_rpc(
        cls,
        contract_address: str,
        rpc_result: str,
        block_number: int,
    ) -> "EthContract":
        return cls(
            address=contract_address, bytecode=rpc_result, block_number=block_number
        )

    def to_dict(self) -> dict:
        return asdict(self)

    # TODO: implement without import etl
    # from ethereumetl.service.eth_contract_service import EthContractService
    def expand_contract_service():
        ...
        # bytecode = contract.bytecode
        # function_sighashes = self.contract_service.get_function_sighashes(bytecode)

        # contract.function_sighashes = function_sighashes
        # contract.is_erc20 = self.contract_service.is_erc20_contract(function_sighashes)
        # contract.is_erc721 = self.contract_service.is_erc721_contract(
        #     function_sighashes
        # )
