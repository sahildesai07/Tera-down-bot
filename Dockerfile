# Use the official Python runtime as a parent image
FROM hrishi2861/terabox:latest

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
# Install any needed packages specified in requirements.txt
# RUN pip install --no-cache-dir --upgrade pip && \
#     pip install -r requirements.txt

# Run your bot application
CMD ["bash", "start.sh"]
