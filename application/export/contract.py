import json

from blockchainetl.jobs.exporters.composite_item_exporter import CompositeItemExporter
from output import CONTRACT_FIELDS
from constants import CONTRACT_ADDRESSES
from ethereumetl.jobs.exporters.contracts_item_exporter import contracts_item_exporter
from ethereumetl.json_rpc_requests import generate_get_code_json_rpc
from ethereumetl.mappers.contract_mapper import EthContractMapper
from ethereumetl.service.eth_contract_service import EthContractService
from ethereumetl.utils import rpc_response_to_result
from export.base import BaseExport
from utils import get_data_path


class ContractExport(BaseExport):
    def __init__(self, chain, start_block, end_block):
        super().__init__(chain, start_block, end_block)
        self.contract_service = EthContractService()
        self.contract_mapper = EthContractMapper()

        self.item_exporter = CompositeItemExporter(
            filename_mapping={"contract": get_data_path(self.chain, "contracts")},
            field_mapping={"contract": CONTRACT_FIELDS},
        )

    def _export(self):
        self.batch_work_executor.execute(
            list(CONTRACT_ADDRESSES), self._export_contracts
        )

    def _export_contracts(self, contract_addresses):
        contracts_code_rpc = list(generate_get_code_json_rpc(contract_addresses))
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
            self.item_exporter.export_item(
                self.contract_mapper.contract_to_dict(contract)
            )

    def _get_contract(self, contract_address, rpc_result):
        contract = self.contract_mapper.rpc_result_to_contract(
            contract_address,
            rpc_result,
        )
        bytecode = contract.bytecode
        function_sighashes = self.contract_service.get_function_sighashes(bytecode)

        contract.function_sighashes = function_sighashes
        contract.is_erc20 = self.contract_service.is_erc20_contract(function_sighashes)
        contract.is_erc721 = self.contract_service.is_erc721_contract(
            function_sighashes
        )

        return contract

    def _end(self):
        self.batch_work_executor.shutdown()
        self.item_exporter.close()