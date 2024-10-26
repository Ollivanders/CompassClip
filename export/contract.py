from ethereumetl.jobs.export_blocks_job import ExportBlocksJob
from ethereumetl.json_rpc_requests import generate_get_block_by_number_json_rpc
from ethereumetl.utils import rpc_response_batch_to_results
from blockchainetl.jobs.base_job import BaseJob
import json


from ethereumetl.executors.batch_work_executor import BatchWorkExecutor
from blockchainetl.jobs.base_job import BaseJob
from ethereumetl.json_rpc_requests import generate_get_block_by_number_json_rpc
from ethereumetl.mappers.block_mapper import EthBlockMapper
from ethereumetl.mappers.transaction_mapper import EthTransactionMapper
from ethereumetl.utils import rpc_response_batch_to_results, validate_range

from ethereumetl.executors.batch_work_executor import BatchWorkExecutor
from blockchainetl.jobs.base_job import BaseJob
from ethereumetl.json_rpc_requests import generate_get_code_json_rpc
from ethereumetl.mappers.contract_mapper import EthContractMapper

from ethereumetl.service.eth_contract_service import EthContractService
from ethereumetl.utils import rpc_response_to_result

from constants import BATCH_SIZE, CONTRACT_ADDRESSES, MAX_WORKERS

from blockchainetl.file_utils import smart_open
from ethereumetl.jobs.export_contracts_job import ExportContractsJob
from ethereumetl.jobs.exporters.contracts_item_exporter import contracts_item_exporter
from blockchainetl.logging_utils import logging_basic_config
from ethereumetl.thread_local_proxy import ThreadLocalProxy
from ethereumetl.providers.auto import get_provider_from_uri
from ethereumetl.jobs.exporters.blocks_and_transactions_item_exporter import (
    blocks_and_transactions_item_exporter,
)

from export.base import BaseExport
from utils import get_data_path, get_provider_uri


class ContractExport(BaseExport):
    def __init__(
        self,
        start_block,
        end_block,
        chain,
    ):
        super().__init__(start_block, end_block, chain)
        self.item_exporter = blocks_and_transactions_item_exporter(
            get_data_path(chain, "blocks"), get_data_path(chain, "transactions")
        )

        self.item_exporter = blocks_and_transactions_item_exporter(
            get_data_path(chain, "blocks"), get_data_path(chain, "transactions")
        )

        self.contract_service = EthContractService()
        self.contract_mapper = EthContractMapper()

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

        print(contracts)
        for contract in contracts:
            self.contract_item_exporter.export_item(
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

    def _end(self):
        self.batch_work_executor.shutdown()
        self.item_exporter.close()
