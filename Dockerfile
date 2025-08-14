FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and data
COPY app.py .
COPY simulator.py .
COPY config/ ./config/
COPY data/ ./data/

# Expose port
EXPOSE 8080

# Set default environment variables
ENV PORT=8080
ENV RUN_INTERVAL_SECONDS=300
ENV RUN_JITTER_SECONDS=120
ENV ITERATIONS_PER_RUN=2
ENV ENABLE_LOOP=true
ENV CSV_PATH=data/Client002.csv
ENV CARDS_PATH=config/cards.json
ENV FORM_ID=250729103005965673
ENV MERCHANT_ID=1110020135

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
