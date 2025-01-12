# Step 1: Use Python 3.9 base image
FROM python:3.9

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Step 4: Copy the entire application into the container
COPY . /app/

# Step 5: Expose port 5000
EXPOSE 5000

# Step 6: Run the Flask app when the container starts
CMD ["python", "ytdownloaderweb.py"]

