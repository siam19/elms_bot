FROM python:3.12

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY . .

# expose port 5000 
EXPOSE 5000

# run bot.py when the container launches
CMD ["python", "bot.py"]

