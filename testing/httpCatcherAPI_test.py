import unittest
import subprocess
import time
import re
import requests

class TestHttpCatcherAPI(unittest.TestCase):

    X_FORWARDED_TLS_CLIENT_CERT_INFO = "Subject%3D%22O%3Dtestorg%22%3BSerialNumber%3D%22393838018661973899367923704705986215770034215499%22"

    @classmethod
    def setUpClass(cls):
        # Starten Sie den Docker-Container
        subprocess.Popen(["docker", "run", "-d", "--name", "httpCatcherAPI", "-p", "8000:8000", "crowsi/httpcatcherdecoy:0.1"])
        # Warten Sie, bis der Container gestartet ist
        time.sleep(10)

    @classmethod
    def tearDownClass(cls):
        # Stoppen und entfernen Sie den Docker-Container
        subprocess.run(["docker", "stop", "httpCatcherAPI"])
        subprocess.run(["docker", "rm", "httpCatcherAPI"])

    def test_default_route(self):
        # Führen Sie eine Anfrage an den Container aus
        headers = {'X-Forwarded-Tls-Client-Cert-Info': self.X_FORWARDED_TLS_CLIENT_CERT_INFO}
        response = requests.get('http://localhost:8000/', headers=headers)
        self.assertEqual(response.status_code, 400)

    def test_specific_route(self):
        # Führen Sie eine Anfrage an den Container aus
        headers = {'X-Forwarded-Tls-Client-Cert-Info': self.X_FORWARDED_TLS_CLIENT_CERT_INFO}
        response = requests.get('http://localhost:8000/some_specific_route', headers=headers)
        self.assertEqual(response.status_code, 400)

    def test_logging_contains_expected_info(self):
        # Lesen Sie die Protokolldatei des Containers
        logs = subprocess.check_output(["docker", "logs", "httpCatcherAPI"]).decode('utf-8')

        self.assertTrue(re.search(r'"serial_number":"393838018661973899367923704705986215770034215499"', logs))
        self.assertTrue(re.search(r'"organization":"testorg"', logs))
        
if __name__ == '__main__':
    # Führt die Tests aus und gibt das Ergebnis aus
    test_suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestHttpCatcherAPI)
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_result = test_runner.run(test_suite)

