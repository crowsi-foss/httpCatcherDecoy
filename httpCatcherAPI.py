# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.



# this is a low interaction http honeypot decoy written in python
# it sets up an http server which listens to all incoming requests and logs them to stdout.
# this server is intended to be sitting behind a traefik proxy as part of the crowsi honeypot platform

from flask import Flask, request, send_file
import os
import sys
import ecs_logging
import logging
from werkzeug.utils import secure_filename
import re
import urllib.parse

app = Flask(__name__)

# Read environment variables for response code and message at startup
RESPONSE_MESSAGE_VAR = os.environ.get('RESPONSE_MESSAGE', 'success')
RESPONSE_CODE_STR = os.environ.get('RESPONSE_CODE', '200')

try:
    RESPONSE_CODE_INT = int(RESPONSE_CODE_STR)
    if not 100 <= RESPONSE_CODE_INT <= 599:
        # Using app.logger.warning. Note: ECS formatting might not apply if handlers are set later.
        app.logger.warning(f"Invalid RESPONSE_CODE: '{RESPONSE_CODE_INT}'. Must be between 100 and 599. Defaulting to 200.")
        RESPONSE_CODE_VAR = 200
    else:
        RESPONSE_CODE_VAR = RESPONSE_CODE_INT
except ValueError:
    app.logger.warning(f"Invalid RESPONSE_CODE: '{RESPONSE_CODE_STR}'. Must be an integer. Defaulting to 200.")
    RESPONSE_CODE_VAR = 200

# set general log level
app.logger.setLevel(logging.INFO)

#configure log handler
#this codes uses the elastic common schema for simpler log formating
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(ecs_logging.StdlibFormatter())
app.logger.handlers=[stdout_handler]

# create global variables needed to parse expected client certificate data added by the traefik proxy
clientOrg="None"
clientSerialNr="None"

# log every incoming request
@app.before_request
def log_request_info():
    #make global variables available in function
    global clientOrg
    global clientSerialNr
    
    #parse client certificate data added by traefik for the organisation and the serial number 
    XForwardCertInfo=request.headers.get('X-Forwarded-Tls-Client-Cert-Info')
    if XForwardCertInfo:
        # Unquote the string
        unquoted_string = urllib.parse.unquote(XForwardCertInfo)

        # Use regular expressions to extract Organization and SerialNumber
        organization_match = re.search(r'O=([^";]+)', unquoted_string)
        serial_number_match = re.search(r'SerialNumber="([^"]+)"', unquoted_string)

        # Check if matches were found
        clientOrg = organization_match.group(1) if organization_match else None
        clientSerialNr = serial_number_match.group(1) if serial_number_match else None

    #log most relevant data into elastic common schema.
    app.logger.info("Request reached httpCatcherAPI", extra={"http.request.method": request.method, "url.path" : request.path, "client.ip": request.headers.get('X-Real-IP'), "host.hostname": request.headers.get('Host'), "tls.client.x509.serial_number": clientSerialNr, "tls.client.x509.subject.organization": clientOrg})


#create a simple response for each incoming request
@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def default(path):
    return RESPONSE_MESSAGE_VAR, RESPONSE_CODE_VAR


#start server and listen on port 8000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
