from abc import ABC

from constants import BATCH_SIZE, MAX_WORKERS
from ethereumetl.executors.batch_work_executor import BatchWorkExecutor
from ethereumetl.providers.auto import get_provider_from_uri
from ethereumetl.thread_local_proxy import ThreadLocalProxy
from ethereumetl.utils import validate_range
from file_exporter import FileExporter
from utils import get_provider_uri


class Baseexecute(ABC):
    def __init__(self, chain, start_block, end_block):
        validate_range(start_block, end_block)
        self.chain = chain
        self.start_block = start_block
        self.end_block = end_block
        self.export_blocks = True
        self.export_transactions = True

        self.item_exporter = FileExporter(self.chain)

        uri = get_provider_uri(chain)
        self.batch_web3_provider = ThreadLocalProxy(
            lambda: get_provider_from_uri(uri, batch=True)
        )

        batch_size = min(BATCH_SIZE, end_block - start_block)
        self.batch_work_executor = BatchWorkExecutor(batch_size, MAX_WORKERS)

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
