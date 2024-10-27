import logging

from blockchainetl.atomic_counter import AtomicCounter
from blockchainetl.exporters import JsonLinesItemExporter
from blockchainetl.file_utils import close_silently, get_file_handle

from dirs import DATA_DIR
from mapper.block_mapper import BlockMapper
from mapper.contract_mapper import ContractMapper
from mapper.transaction_mapper import TransactionMapper

FILE_TYPES = ["block", "transaction", "contract"]

TYPE_MAPPING = {
    "block": BlockMapper,
    "transaction": TransactionMapper,
    "contract": ContractMapper,
}


class ItemExporter:
    def __init__(self, chain):
        self.chain = chain
        self.exporter_mapping = {}
        self.counter_mapping = {}

        self.file_mapping = {}

        self.logger = logging.getLogger("ItemExporter")

    def get_data_path(self, type: str):
        data_path = DATA_DIR / self.chain / f"{type}.json"
        data_path.parent.mkdir(parents=True, exist_ok=True)
        return data_path

    def open(self):
        for item_type in FILE_TYPES:
            filepath = self.get_data_path(item_type)
            file = get_file_handle(filepath, binary=True)
            self.file_mapping[item_type] = file

            self.exporter_mapping[item_type] = JsonLinesItemExporter(
                file,
                fields_to_export=TYPE_MAPPING[item_type].fields,
            )
            self.counter_mapping[item_type] = AtomicCounter()

    def export_items(self, items):
        for item in items:
            self.export_item(item)

    def export_item(self, item):
        item_type = item.get("type")
        if item_type is None:
            raise ValueError('"type" key is not found in item {}'.format(repr(item)))

        exporter = self.exporter_mapping.get(item_type)
        if exporter is None:
            raise ValueError("Exporter for item type {} not found".format(item_type))
        exporter.export_item(item)

        counter = self.counter_mapping.get(item_type)
        if counter is not None:
            counter.increment()

    def close(self):
        for item_type, file in self.file_mapping.items():
            close_silently(file)

            counter = self.counter_mapping[item_type]
            if counter is not None:
                self.logger.info(
                    "{} items exported: {}".format(item_type, counter.increment() - 1)
                )
