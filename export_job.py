from ethereumetl.jobs.export_blocks_job import ExportBlocksJob
from ethereumetl.json_rpc_requests import generate_get_block_by_number_json_rpc
from ethereumetl.utils import rpc_response_batch_to_results
import json

from constants import CONTRACT_ADDRESSES, USDC_ADDRESS


class BlockExport(ExportBlocksJob):
    def _export_batch(self, block_number_batch):
        blocks_rpc = list(
            generate_get_block_by_number_json_rpc(
                block_number_batch, self.export_transactions
            )
        )
        response = self.batch_web3_provider.make_batch_request(json.dumps(blocks_rpc))

        results = rpc_response_batch_to_results(response)
        blocks = [self.block_mapper.json_dict_to_block(result) for result in results]

        for block in blocks:
            self._export_block(block)

    def _export_block(self, block):
        if self.export_blocks:
            self.item_exporter.export_item(self.block_mapper.block_to_dict(block))

        if self.export_transactions:
            for tx in block.transactions:
                tx_mapper = self.transaction_mapper.transaction_to_dict(tx)

                if (
                    tx_mapper["from_address"] in CONTRACT_ADDRESSES
                    or tx_mapper["to_address"] in CONTRACT_ADDRESSES
                ):
                    self.item_exporter.export_item(tx_mapper)
