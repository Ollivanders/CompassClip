import json

from mapper.contract_mapper import EthContract
from output.contract_exporter import ContractFileExporter
from execute.util import rpc_response_to_result
from execute.rpc_wrappers import generate_get_code_json_rpc
from constants import CONTRACT_ADDRESSES


from execute.base import BaseExecute


class ContractExport(BaseExecute):
    def __init__(self, chain, start_block, end_block):
        super().__init__(chain, start_block, end_block)

        # self.contract_service = EthContractService()
        self.exporter = ContractFileExporter(self.chain)

    def _export(self):
        self.batch_work_executor.execute(
            list(CONTRACT_ADDRESSES), self._export_contracts
        )

    def _export_contracts(self, contract_addresses):
        for block_number in range(self.start_block, self.end_block + 1):
            contracts_code_rpc = list(
                generate_get_code_json_rpc(contract_addresses, block=block_number)
            )
            response_batch = self.batch_web3_provider.make_batch_request(
                json.dumps(contracts_code_rpc)
            )

            contracts = []
            for response in response_batch:
                # request id is the index of the contract address in contract_addresses list
                request_id = response["id"]
                result = rpc_response_to_result(response)

                contract_address = contract_addresses[request_id]
                contract = self._get_contract(contract_address, result)
                contracts.append(contract)

            for contract in contracts:
                self.exporter.export_item(contract.to_dict())

    def _get_contract(self, contract_address, rpc_result):
        return EthContract.from_rpc(contract_address, rpc_result)

    def _end(self):
        self.batch_work_executor.shutdown()
