import json

from constants import CONTRACT_ADDRESSES_SET
from execute.base import BaseExecute
from execute.rpc_wrappers import generate_get_block_by_number_json_rpc
from execute.util import rpc_response_batch_to_results
from mapper.block_mapper import EthBlock
from output.file_exporter import FileExporter


class BlockExport(BaseExecute):
    def __init__(self, chain, start_block, end_block):
        super().__init__(chain, start_block, end_block)

        self.exporter = FileExporter(self.chain, ["block", "transaction"])

    def _export(self):
        self.batch_work_executor.execute(
            range(self.start_block, self.end_block + 1),
            self._export_batch,
            total_items=self.end_block - self.start_block + 1,
        )

    def _export_batch(self, block_number_batch):
        blocks_rpc = list(
            generate_get_block_by_number_json_rpc(
                block_number_batch,
                self.export_transactions,
            )
        )
        response = self.batch_web3_provider.make_batch_request(json.dumps(blocks_rpc))

        results = rpc_response_batch_to_results(response)

        for result in results:
            block = EthBlock.from_json(result)
            self._export_block(block)

    def _is_contract_in_access_list(self, access_list):
        for access in access_list:
            if access["address"] in CONTRACT_ADDRESSES_SET:
                return True
        return False

    def _export_block(self, block):
        used_transactions_count = 0

        for tx in block.transactions:
            if (
                tx.from_address in CONTRACT_ADDRESSES_SET
                or tx.to_address in CONTRACT_ADDRESSES_SET
            ):
                used_transactions_count += 1
                self.exporter.export_item(tx.to_dict())
            elif self._is_contract_in_access_list(tx.access_list):
                self.exporter.export_item(tx.to_dict())
                used_transactions_count += 1

        block.used_transactions_count = used_transactions_count
        self.exporter.export_item(block.to_dict())
