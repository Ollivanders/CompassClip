from abc import ABC, abstractmethod

from execute.batch_worker import BatchWorkExecutor
from execute.util import validate_range
from provider import BatchHTTPProvider
from thread_proxy import ThreadLocalProxy
from output.file_exporter import FileExporter
from constants import BATCH_SIZE, DEFAULT_TIMEOUT, MAX_WORKERS
from utils import get_provider_uri


class BaseExecute(ABC):
    exporter: FileExporter

    def __init__(self, chain, start_block, end_block):
        validate_range(start_block, end_block)
        self.chain = chain
        self.start_block = start_block
        self.end_block = end_block
        self.export_blocks = True
        self.export_transactions = True

        uri = get_provider_uri(chain)
        self.batch_web3_provider = ThreadLocalProxy(
            lambda: BatchHTTPProvider(uri, request_kwargs={"timeout": DEFAULT_TIMEOUT})
        )

        batch_size = min(BATCH_SIZE, end_block - start_block)
        self.batch_work_executor = BatchWorkExecutor(batch_size, MAX_WORKERS)

    def run(self):
        try:
            self.exporter.open()
            self._export()
        finally:
            self._end()

    @abstractmethod
    def _export(self):
        ...

    def _end(self):
        self.batch_work_executor.shutdown()
        self.exporter.close()
