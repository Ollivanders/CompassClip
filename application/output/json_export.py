from json import JSONEncoder

import decimal
import six


class JsonExport:
    def __init__(self, file):
        self.indent = 4
        self.file = file

        self.encoder = JSONEncoder(default=EncodeDecimal)

    def export_item(self, item_dict) -> None:
        data = self.encoder.encode(item_dict) + "\n"
        self.file.write(to_bytes(data))


def EncodeDecimal(o):
    if isinstance(o, decimal.Decimal):
        return float(round(o, 8))
    raise TypeError(repr(o) + " is not JSON serializable")


def to_bytes(text, encoding=None, errors="strict"):
    """Return the binary representation of `text`. If `text`
    is already a bytes object, return it as-is."""
    if isinstance(text, bytes):
        return text
    if not isinstance(text, six.string_types):
        raise TypeError(
            "to_bytes must receive a unicode, str or bytes "
            "object, got %s" % type(text).__name__
        )
    if encoding is None:
        encoding = "utf-8"
    return text.encode(encoding, errors)
