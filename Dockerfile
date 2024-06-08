# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.



#This is the docker file to build a docker container hosting the httpCatcherAPI decoy

# base image
FROM python:3.13.0b2-alpine3.19


# create working directory in container
WORKDIR /home/httpCatcherAPI

#copy the python requirements.txt file into the container
COPY requirements.txt .

#install the needed python dependencies
RUN pip install --no-cache-dir -r requirements.txt

#delete requirements file from container
RUN rm requirements.txt


# copy the httpCatcherAPI source code into the work directory
COPY httpCatcherAPI.py .

# start a gunicorn web server in the container that listens on port 8000 and hosts the httpCatcherAPI
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "httpCatcherAPI:app"]

# expose port 8000
EXPOSE 8000


