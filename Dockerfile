# Use a slim Python base image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file (if any) and install dependencies first
# This improves layer caching if requirements don't change often
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask application code into the container
COPY app.py .

# Expose the port that the Flask application will run on
EXPOSE 5000

# Set environment variables for Flask (optional but good practice)
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Command to run the Flask application using Gunicorn (recommended for production)
# For development, you could use `flask run` but Gunicorn is more robust.
# If you don't have gunicorn in requirements.txt, you'd use:
# CMD ["python", "app.py"]
# Assuming gunicorn is in requirements.txt:
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
