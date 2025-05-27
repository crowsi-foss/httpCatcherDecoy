import unittest
import subprocess
import time
import re
import requests
import docker

class TestHttpCatcherAPI(unittest.TestCase):

    X_FORWARDED_TLS_CLIENT_CERT_INFO = "Subject%3D%22O%3Dtestorg%22%3BSerialNumber%3D%22393838018661973899367923704705986215770034215499%22"
    IMAGE_NAME = "testimage:latest" # Image built by GitHub Actions

    def test_default_route(self):
        # This test relies on the 'testcontainer' started by GitHub Actions
        headers = {'X-Forwarded-Tls-Client-Cert-Info': self.X_FORWARDED_TLS_CLIENT_CERT_INFO}
        response = requests.get('http://localhost:8000/', headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_specific_route(self):
        # This test relies on the 'testcontainer' started by GitHub Actions
        headers = {'X-Forwarded-Tls-Client-Cert-Info': self.X_FORWARDED_TLS_CLIENT_CERT_INFO}
        response = requests.get('http://localhost:8000/some_specific_route', headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_logging_contains_expected_info(self):
        # This test relies on the 'testcontainer' started by GitHub Actions
        client = docker.from_env()
        # get Logs of container
        container = client.containers.get('testcontainer')
        logs = container.logs().decode('utf-8')

        self.assertTrue(re.search(r'"serial_number":"393838018661973899367923704705986215770034215499"', logs))
        self.assertTrue(re.search(r'"organization":"testorg"', logs))

    def test_custom_response_code_and_message(self):
        client = docker.from_env()
        container_name = "custom-response-test-container"
        env_vars = {
            "HTTP_RESPONSE_CODE": "403",
            "HTTP_RESPONSE_MESSAGE": "ForbiddenTest"
        }
        
        # Ensure no container with this name already exists (e.g. from a previous failed run)
        try:
            existing_container = client.containers.get(container_name)
            existing_container.remove(force=True)
        except docker.errors.NotFound:
            pass # Container doesn't exist, which is good

        container = None
        try:
            container = client.containers.run(
                self.IMAGE_NAME,
                detach=True,
                name=container_name,
                environment=env_vars,
                ports={'8000/tcp': None} # Let Docker assign a random available port
            )
            
            # Retrieve the dynamically assigned port
            container.reload() # Ensure container data is up-to-date
            assigned_port = container.ports['8000/tcp'][0]['HostPort']
            
            # Wait for the container to be ready (simple retry mechanism)
            max_retries = 10
            retry_delay = 2 # seconds
            for i in range(max_retries):
                try:
                    response = requests.get(f'http://localhost:{assigned_port}/')
                    if response.status_code == 403: # Check for expected code to confirm readiness with new env
                        break 
                except requests.exceptions.ConnectionError:
                    pass
                time.sleep(retry_delay)
            else:
                self.fail(f"Container did not become ready at http://localhost:{assigned_port}/")

            headers = {'X-Forwarded-Tls-Client-Cert-Info': self.X_FORWARDED_TLS_CLIENT_CERT_INFO}
            response = requests.get(f'http://localhost:{assigned_port}/', headers=headers)
            
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.text, "ForbiddenTest")
            
            # Also check logs for this specific container to ensure it's working as expected
            # This is optional but good for verifying the specific instance behaved
            logs = container.logs().decode('utf-8')
            self.assertIn("Request reached httpCatcherAPI", logs) # Basic check

        finally:
            if container:
                container.stop()
                container.remove()

if __name__ == '__main__':
    unittest.main()
