# Sample Gunicorn configuration file

# Bind address (host and port)
bind = '0.0.0.0:8000'  # Listens on all interfaces, port 8000

# Number of worker processes
workers = 4  # Adjust based on your application and hardware

# Worker timeout in seconds
timeout = 300  # Default is 30 seconds, adjust if needed

# Logging configuration
# Replace '-' with a filename for file-based logging
accesslog = '-'  # Logs access information to standard output
errorlog = '-'  # Logs errors to standard output

# Preload application code before starting workers
preload_app = True  # Speeds up initial request

# Send static files directly from the filesystem
# (Only use if your application serves static files itself)
sendfile = True
