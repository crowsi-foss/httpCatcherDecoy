#This is the docker file to build a docker container hosting the httpCatcherAPI decoy

# base image
FROM python:3.13.0a4-alpine3.19

#add ecs-logging capabilities
RUN pip install ecs-logging

#add flask
RUN pip install flask

#add gunicorn
RUN pip install gunicorn


# create working directory in container
WORKDIR /home/httpCatcherAPI

# copy the httpCatcherAPI source code into the work directory
COPY httpCatcherAPI.py .

# start a gunicorn web server in the container that listens on port 8000 and hosts the httpCatcherAPI
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "httpCatcherAPI:app"]

# expose port 8000
EXPOSE 8000


