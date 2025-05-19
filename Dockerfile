# Use official Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy files to the container
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Run the bot
CMD ["python", "bot.py"]