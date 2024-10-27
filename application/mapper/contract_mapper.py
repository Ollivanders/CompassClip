class ContractMapper:
    def rpc_result_to_contract(self, contract_address, rpc_result):
        contract = EthContract()
        contract.address = contract_address
        contract.bytecode = rpc_result

        return contract

    def to_dict(self, contract):
        return {
            "type": "contract",
            "address": contract.address,
            "bytecode": contract.bytecode,
            "function_sighashes": contract.function_sighashes,
            "is_erc20": contract.is_erc20,
            "is_erc721": contract.is_erc721,
            "block_number": contract.block_number,
        }


class EthContract:
    def __init__(self):
        self.address = None
        self.bytecode = None
        self.function_sighashes = []
        self.is_erc20 = False
        self.is_erc721 = False
        self.block_number = None
