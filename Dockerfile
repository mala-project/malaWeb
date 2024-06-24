# Use a slim Python 3 image as the base
FROM python:3.11-slim
LABEL authors="Maximilian Wenger"


# Create a working directory for the application
WORKDIR /app

# Copy the requirements.txt file
COPY requirements.txt .

# Install dependencies using pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY install .

# Install any additional system dependencies (if needed)
# RUN apt-get update && apt-get install -y some-package

# Expose the port used by Dash app (usually 8050)
EXPOSE 8050

# Use gunicorn as the application server (recommended for production)
CMD ["gunicorn", "--bind", "0.0.0.0:8050", "server:app"]
