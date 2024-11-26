FROM cypress/browsers:latest

ARG PORT=8000

WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .

# Install Python and venv
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv

# Create and activate virtual environment
RUN python3 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Install dependencies in venv
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app .

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]