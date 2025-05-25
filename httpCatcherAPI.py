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

# Initialize defaults
CONFIG_RESPONSE_CODE = 200
CONFIG_RESPONSE_MESSAGE = "success" # Default message

# set general log level (needs to be set before any app.logger calls)
app.logger.setLevel(logging.INFO)

#configure log handler (needs to be set before any app.logger calls)
#this codes uses the elastic common schema for simpler log formating
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(ecs_logging.StdlibFormatter())
app.logger.handlers=[stdout_handler]


original_http_response_code_env = os.getenv('HTTP_RESPONSE_CODE')
original_http_response_message_env = os.getenv('HTTP_RESPONSE_MESSAGE')

if original_http_response_code_env is not None:
    try:
        parsed_code = int(original_http_response_code_env)
        if 100 <= parsed_code <= 599:
            CONFIG_RESPONSE_CODE = parsed_code
            # If code is valid and from env, try to use message from env, else default "success"
            if original_http_response_message_env is not None:
                CONFIG_RESPONSE_MESSAGE = original_http_response_message_env
            # else CONFIG_RESPONSE_MESSAGE remains "success" (already set as default)
        else:
            app.logger.warning(f"Invalid HTTP_RESPONSE_CODE provided: '{original_http_response_code_env}'. Must be an integer between 100 and 599. Using default 200 and message 'success'.")
            # CONFIG_RESPONSE_CODE remains 200, CONFIG_RESPONSE_MESSAGE remains "success" (already set as defaults)
    except ValueError:
        app.logger.warning(f"Invalid HTTP_RESPONSE_CODE provided: '{original_http_response_code_env}'. Must be an integer. Using default 200 and message 'success'.")
        # CONFIG_RESPONSE_CODE remains 200, CONFIG_RESPONSE_MESSAGE remains "success" (already set as defaults)
else:
    # HTTP_RESPONSE_CODE env var was not set, so defaults (200, "success") are used for code and message.
    # However, if HTTP_RESPONSE_MESSAGE *is* set, it should be used with the default code 200.
    if original_http_response_message_env is not None:
        CONFIG_RESPONSE_MESSAGE = original_http_response_message_env

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
    return CONFIG_RESPONSE_MESSAGE, CONFIG_RESPONSE_CODE


#start server and listen on port 8000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
