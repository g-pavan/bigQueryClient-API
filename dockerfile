# Use an official Python 3.11.1 runtime as a parent image
FROM python:3.11.1-slim

# Set the working directory to / (the root directory)
WORKDIR /

# Copy the current directory contents into the container at / (root)
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Run app.py when the container launches
CMD ["python", "main.py"]
