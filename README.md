# httpCatcherDecoy
httpCatcherDecoy is a docker container hosting a python based low interaction http endpoint decoy that can receive and log http requests.

It logs data to stdout making use of the Elastic Common Schema to allow a simple log processing afterwards.

httpCatcherAPI is available on Docker Hub and is intended to be used as part of the crowsi honeypot platform  
https://github.com/crowsi-foss/crowsi-platform

## Configuration

You can control the HTTP response code and message returned by the decoy using environment variables:

- `HTTP_RESPONSE_CODE`: (optional) Set the HTTP status code to return (e.g., `200`, `404`). Must be an integer between 100 and 599. Defaults to `200` if not set or invalid.
- `HTTP_RESPONSE_MESSAGE`: (optional) Set the response message body. Defaults to `"success"` if not set.

If only `HTTP_RESPONSE_MESSAGE` is set, the code will default to `200`. If both are unset, the default response is `200` with message `"success"`.


