#Using python
FROM python:3.9
# Using Layered approach for the installation of requirements
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
#Copy files to container
COPY . ./
#Running APP #and doing some PORT Forwarding
CMD gunicorn --chdir src app:server
