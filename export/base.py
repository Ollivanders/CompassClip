from ethereumetl.executors.batch_work_executor import BatchWorkExecutor
from ethereumetl.mappers.block_mapper import EthBlockMapper
from ethereumetl.mappers.transaction_mapper import EthTransactionMapper
from ethereumetl.utils import validate_range

from ethereumetl.mappers.contract_mapper import EthContractMapper

from ethereumetl.service.eth_contract_service import EthContractService

from constants import BATCH_SIZE, MAX_WORKERS

from ethereumetl.jobs.exporters.contracts_item_exporter import contracts_item_exporter
from ethereumetl.thread_local_proxy import ThreadLocalProxy
from ethereumetl.providers.auto import get_provider_from_uri
from ethereumetl.jobs.exporters.blocks_and_transactions_item_exporter import (
    blocks_and_transactions_item_exporter,
)

from utils import get_data_path, get_provider_uri


class BaseExport:
    def __init__(
        self,
        start_block,
        end_block,
        chain,
    ):
        validate_range(start_block, end_block)
        self.start_block = start_block
        self.end_block = end_block
        self.export_blocks = True
        self.export_transactions = True

        uri = get_provider_uri(chain)
        self.batch_web3_provider = ThreadLocalProxy(
            lambda: get_provider_from_uri(uri, batch=True)
        )

        batch_size = min(BATCH_SIZE, end_block - start_block)
        self.batch_work_executor = BatchWorkExecutor(batch_size, MAX_WORKERS)
        self.item_exporter = blocks_and_transactions_item_exporter(
            get_data_path(chain, "blocks"), get_data_path(chain, "transactions")
        )
        self.contract_item_exporter = contracts_item_exporter(
            get_data_path(chain, "contracts")
        )

        self.block_mapper = EthBlockMapper()
        self.transaction_mapper = EthTransactionMapper()
        self.contract_service = EthContractService()
        self.contract_mapper = EthContractMapper()

    def run(self):
        try:
            self._start()
            self._export()
        finally:
            self._end()

    def _start(self):
        self.item_exporter.open()

    def _export(self): ...

    def _end(self):
        self.batch_work_executor.shutdown()
        self.item_exporter.close()
