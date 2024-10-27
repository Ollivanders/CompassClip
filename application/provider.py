from web3 import HTTPProvider
from web3._utils.request import make_post_request


class BatchHTTPProvider(HTTPProvider):
    def make_batch_request(self, text):
        self.logger.debug(
            "Making request HTTP. URI: %s, Request: %s", self.endpoint_uri, text
        )
        request_data = text.encode("utf-8")
        raw_response = make_post_request(
            self.endpoint_uri,
            request_data,
            **self.get_request_kwargs(),  # type: ignore
        )
        response = self.decode_rpc_response(raw_response)
        self.logger.debug(
            "Getting response HTTP. URI: %s, " "Request: %s, Response: %s",
            self.endpoint_uri,
            text,
            response,
        )
        return response
