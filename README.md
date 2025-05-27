# httpCatcherDecoy
httpCatcherDecoy is a docker container hosting a python based low interaction http endpoint decoy that can receive and log http requests.

it logs data to stdout making use of the elastic common schema to allow a simple log processing afterwards.

httpCatcherAPI is available on docker hub and is intended to be used as part of the crowsi honeypot platform
https://github.com/crowsi-foss/crowsi-platform

## Testing

The tests for httpCatcherDecoy are located in the `testing/` directory. These tests require Docker to be installed and running on your system.

To run the tests locally, follow these steps:

1.  **Build the Docker Image:** Ensure the Docker image is built with the tag `testimage:latest`. You can do this by running the following command from the root of the repository:
    ```bash
    docker build -t testimage:latest .
    ```
2.  **Install Test Dependencies:** Install the necessary Python packages for testing:
    ```bash
    pip install -r testing/requirements-test.txt
    ```
3.  **Run the Tests:** Execute the tests using the Python `unittest` module:
    ```bash
    python -m unittest testing.httpCatcherAPI_test
    ```

The tests interact with Docker to run the application in a containerized environment. Some tests may start their own Docker containers, while others might expect a container to be running, similar to the setup in CI environments.


