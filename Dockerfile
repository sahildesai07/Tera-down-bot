# Start with the base image
FROM hrishi2861/terabox:latest

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install required packages from requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Expose any ports the app is expected to listen on
# For example, if your application runs on port 8080, use:
# EXPOSE 8080

# Define the command to run your app using CMD which defines your runtime.
CMD ["bash", "start.sh"]
