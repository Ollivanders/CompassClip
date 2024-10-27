import json

from constants import CONTRACT_ADDRESSES_SET
from ethereumetl.json_rpc_requests import generate_get_block_by_number_json_rpc
from ethereumetl.utils import rpc_response_batch_to_results
from mapper.block_mapper import BlockMapper
from mapper.transaction_mapper import TransactionMapper

from execute.base import BaseExecute


class BlockExport(BaseExecute):
    def __init__(self, start_block, end_block, chain):
        super().__init__(chain, start_block, end_block)

        self.block_mapper = BlockMapper()
        self.transaction_mapper = TransactionMapper()

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
        blocks = [self.block_mapper.json_dict_to_block(result) for result in results]

        for block in blocks:
            self._export_block(block)

    def _is_contract_in_access_list(self, access_list):
        for access in access_list:
            if access["address"] in CONTRACT_ADDRESSES_SET:
                return True

        return False

    def _export_block(self, block):
        if self.export_blocks:
            self.item_exporter.export_item(self.block_mapper.to_dict(block))

        if self.export_transactions:
            for tx in block.transactions:
                tx_mapper = self.transaction_mapper.to_dict(tx)

                if (
                    tx_mapper["from_address"] in CONTRACT_ADDRESSES_SET
                    or tx_mapper["to_address"] in CONTRACT_ADDRESSES_SET
                ):
                    self.item_exporter.export_item(tx_mapper)
                elif self._is_contract_in_access_list(tx_mapper["access_list"]):
                    self.item_exporter.export_item(tx_mapper)
