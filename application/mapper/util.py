def to_normalized_address(address):
    if address is None or not isinstance(address, str):
        return address
    return address.lower()


def hex_to_dec(hex_string):
    if hex_string is None:
        return None

    try:
        return int(hex_string, 16)
    except ValueError:
        print("Not a hex string %s" % hex_string)
        return hex_string
