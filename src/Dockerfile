FROM python:3.11.5
LABEL authors="mxy"

# Using Layered approach for the installation of requirements
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
#Copy files to your container
COPY .. ./
#Running your APP and doing some PORT Forwarding
CMD gunicorn app:server -b :8000