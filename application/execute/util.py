def rpc_response_to_result(response):
    result = response.get("result")
    if result is None:
        error_message = "result is None in response {}.".format(response)
        if response.get("error") is None:
            error_message = error_message + " Make sure Ethereum node is synced."
            # When nodes are behind a load balancer it makes sense to retry the request in hopes it will go to other,
            # synced node
            raise ValueError(error_message)
        elif response.get("error") is not None and is_retriable_error(
            response.get("error").get("code")
        ):
            raise ValueError(error_message)
        raise ValueError(error_message)
    return result


def rpc_response_batch_to_results(response):
    for response_item in response:
        yield rpc_response_to_result(response_item)


def is_retriable_error(error_code):
    if error_code is None:
        return False

    if not isinstance(error_code, int):
        return False

    # https://www.jsonrpc.org/specification#error_object
    if error_code == -32603 or (-32000 >= error_code >= -32099):
        return True

    return False


def validate_range(range_start_incl, range_end_incl):
    if range_start_incl < 0 or range_end_incl < 0:
        raise ValueError("range_start and range_end must be greater or equal to 0")

    if range_end_incl < range_start_incl:
        raise ValueError("range_end must be greater or equal to range_start")
