from application.output.file_exporter import FileExporter
from dirs import DATA_DIR


class TransactionExporter(FileExporter):
    def get_data_path(self, partition: str):
        data_path = DATA_DIR / self.chain / "transaction" / partition
        data_path.parent.mkdir(parents=True, exist_ok=True)
        return data_path

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
