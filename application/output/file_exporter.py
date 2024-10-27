import logging

from output.json_export import JsonExport
from dirs import DATA_DIR
from mapper.block_mapper import BlockMapper
from mapper.contract_mapper import ContractMapper
from mapper.transaction_mapper import TransactionMapper

import itertools

TYPE_MAPPING = {
    "block": BlockMapper,
    "transaction": TransactionMapper,
    "contract": ContractMapper,
}


class AtomicCounter:
    def __init__(self):
        self._counter = itertools.count()
        next(self._counter)

    def increment(self, increment=1):
        assert increment > 0
        return [next(self._counter) for _ in range(0, increment)][-1]


class FileExporter:
    def __init__(self, chain, data_types=[]):
        for data_type in data_types:
            assert data_type in TYPE_MAPPING.keys()
        self.data_types = data_types

        self.chain = chain
        self.exporter_mapping = {}
        self.counter_mapping = {}

        self.file_mapping = {}

        self.logger = logging.getLogger("ItemExporter")
        self.open()

    def get_data_path(self, type: str):
        data_path = DATA_DIR / self.chain / type
        data_path.parent.mkdir(parents=True, exist_ok=True)
        return data_path

    def open(self):
        for item_type in self.data_types:
            filepath = self.get_data_path(item_type)
            file = open(filepath, "wb")

            self.file_mapping[item_type] = file
            self.exporter_mapping[item_type] = JsonExport(file)
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
            file.close()

            counter = self.counter_mapping[item_type]
            if counter is not None:
                self.logger.info(
                    "{} items exported: {}".format(item_type, counter.increment() - 1)
                )
