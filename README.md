# Client_002 - Payment Processing Automation Service

## Overview

Client_002 is a FastAPI-based payment processing automation service that simulates payment transactions using real customer data and test payment cards. The application is designed to run continuously in the cloud, performing automated payment testing at configurable intervals while providing manual trigger capabilities through REST API endpoints.

## Architecture

The service consists of three main components:

1. **FastAPI Web Server** (`app.py`) - Provides REST API endpoints and manages the application lifecycle
2. **Payment Simulator** (`simulator.py`) - Handles payment processing workflow including tokenization, checkout, and payment creation
3. **Background Scheduler** - Runs automated payment tests at configurable intervals with jitter

## Features

- ✅ **Automated Payment Testing** - Runs payment simulations at scheduled intervals
- ✅ **Manual Trigger API** - Trigger payment tests on-demand via REST endpoints
- ✅ **Real Customer Data** - Uses actual customer data from CSV files for realistic testing
- ✅ **Multiple Payment Methods** - Supports various test cards and currencies (EUR, GBP)
- ✅ **Comprehensive Logging** - Detailed logging with timestamps for monitoring and debugging
- ✅ **Health Monitoring** - Built-in health check endpoints
- ✅ **Cloud-Ready** - Configured for AWS App Runner deployment
- ✅ **Environment-Based Configuration** - All settings configurable via environment variables

## Project Structure

```
Client_002/
├── app.py                      # Main FastAPI application
├── simulator.py                # Payment simulation logic
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container configuration
├── apprunner.yaml             # AWS App Runner configuration
├── AWS_DEPLOYMENT_CONFIG.md   # Deployment documentation
├── README.md                  # This file
├── config/
│   └── cards.json             # Test payment cards configuration
└── data/
    └── Client002.csv          # Customer data for testing
```

## Dependencies

### Core Dependencies
- **FastAPI** (0.112.2) - Modern web framework for APIs
- **Uvicorn** (0.30.1) - ASGI server for FastAPI
- **Requests** (2.32.3) - HTTP client for API calls
- **Pandas** (2.2.2) - Data manipulation and CSV processing
- **Faker** (26.0.0) - Generate fake data for testing
- **NumPy** (1.26.4) - Numerical computations

### Installation

```bash
pip install -r requirements.txt
```

## Configuration

### Environment Variables

#### Core Application Settings
| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8080` | Server port (required for AWS App Runner) |
| `RUN_INTERVAL_SECONDS` | `300` | Interval between automated runs (5 minutes) |
| `RUN_JITTER_SECONDS` | `120` | Random jitter to add to interval (±2 minutes) |
| `ITERATIONS_PER_RUN` | `2` | Number of payment tests per automated run |
| `ENABLE_LOOP` | `true` | Enable/disable background automation loop |

#### File Paths
| Variable | Default | Description |
|----------|---------|-------------|
| `CSV_PATH` | `data/Client002.csv` | Path to customer data CSV file |
| `CARDS_PATH` | `config/cards.json` | Path to test cards configuration |

#### Payment Gateway Configuration
| Variable | Default | Description |
|----------|---------|-------------|
| `FORM_ID` | `250729103005965673` | Datatrans form identifier |
| `MERCHANT_ID` | `1110020135` | Merchant identifier |
| `TOKENIZATION_URL` | Datatrans SecureFields API | Card tokenization endpoint |
| `CHECKOUT_URL` | PayIntelli Checkout API | Checkout creation endpoint |
| `PAYMENT_URL` | PayIntelli Payment API | Payment processing endpoint |

### Configuration Files

#### Test Cards (`config/cards.json`)
Contains test payment card details with the following structure:
```json
[
  {
    "number": "4111111111111111",
    "cvv": "123",
    "month": "12",
    "year": "2025"
  }
]
```

#### Customer Data (`data/Client002.csv`)
CSV file containing customer information with columns:
- `First_Name` - Customer first name
- `Last_Name` - Customer last name  
- `Email_Address` - Customer email
- `Address_line1` - Street address
- `City` - City name
- `State` - State/province
- `Postal_Code` - ZIP/postal code

## API Endpoints

### Health Check
```http
GET /health
```
Returns application health status.

**Response:**
```json
{
  "ok": true
}
```

### Root Status
```http
GET /
```
Returns basic application status.

**Response:**
```json
{
  "status": "running"
}
```

### Manual Payment Test
```http
POST /run?iterations=<number>
```
Triggers immediate payment test execution.

**Parameters:**
- `iterations` (optional) - Number of payment tests to run. Defaults to `ITERATIONS_PER_RUN` env var.

**Response:**
```json
{
  "status": "ok",
  "iterations": 2
}
```

## Local Development

### Prerequisites
- Python 3.11+
- pip package manager

### Setup
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Ensure data files are present:
   - `config/cards.json` - Test payment cards
   - `data/Client002.csv` - Customer data

### Running Locally
```bash
# Run with FastAPI development server
uvicorn app:app --host 0.0.0.0 --port 8080 --reload

# Or run directly with Python
python app.py
```

### Testing
```bash
# Test health endpoint
curl http://localhost:8080/health

# Trigger manual payment test
curl -X POST http://localhost:8080/run?iterations=1
```

## Docker Deployment

### Building the Image
```bash
docker build -t client-002 .
```

### Running the Container
```bash
docker run -p 8080:8080 \
  -e RUN_INTERVAL_SECONDS=300 \
  -e ITERATIONS_PER_RUN=2 \
  -e ENABLE_LOOP=true \
  client-002
```

### Environment Variables in Docker
All environment variables can be passed using `-e` flag or via docker-compose environment section.

## AWS App Runner Deployment

### Option 1: Source Code Deployment (Manual Configuration)

1. **Push to GitHub**: Commit all files to your GitHub repository
2. **Create App Runner Service**:
   - Go to AWS App Runner console
   - Choose "Source code repository"
   - Connect to your GitHub repository
   - Select branch (main)
   - **Manual Configuration (No YAML file)**

3. **Service Configuration**:
   - **Runtime**: Python 3.11
   - **Build command**: `python -m pip install --upgrade pip && pip install -r requirements.txt`
   - **Start command**: `python -m uvicorn app:app --host 0.0.0.0 --port 8080`
   - **Port**: 8080

4. **Environment Variables**: Configure in App Runner console (see section below)

### Option 2: Container Deployment

1. **Build and Push to ECR**:
   ```bash
   # Build image
   docker build -t client-002 .
   
   # Tag for ECR
   docker tag client-002:latest <account-id>.dkr.ecr.<region>.amazonaws.com/client-002:latest
   
   # Push to ECR
   docker push <account-id>.dkr.ecr.<region>.amazonaws.com/client-002:latest
   ```

2. **Create App Runner Service**:
   - Choose "Container registry"
   - Select your ECR repository
   - Configure environment variables in App Runner console

### Environment Variables in AWS App Runner

**Configure these manually in the App Runner service console:**

| Variable Name | Value | Description |
|---------------|-------|-------------|
| `PORT` | `8080` | Server port (required by AWS App Runner) |
| `RUN_INTERVAL_SECONDS` | `300` | Interval between automated runs (5 minutes) |
| `RUN_JITTER_SECONDS` | `120` | Random jitter (±2 minutes) |
| `ITERATIONS_PER_RUN` | `2` | Number of payment tests per run |
| `ENABLE_LOOP` | `true` | Enable background automation |
| `CSV_PATH` | `data/Client002.csv` | Customer data file path |
| `CARDS_PATH` | `config/cards.json` | Test cards configuration path |
| `FORM_ID` | `250729103005965673` | Datatrans form identifier |
| `MERCHANT_ID` | `1110020135` | Merchant identifier |

**Steps to add environment variables:**
1. In AWS App Runner console, go to your service
2. Navigate to "Configuration" tab
3. Edit "Environment variables" section
4. Add each variable from the table above
5. Save and deploy changes

### Monitoring and Logs

- **CloudWatch Logs**: All application logs are automatically sent to CloudWatch
- **Metrics**: App Runner provides built-in metrics for requests, CPU, memory
- **Health Checks**: Uses `/health` endpoint for health monitoring

## Payment Flow

### 1. Card Tokenization
- Calls Datatrans SecureFields API
- Converts card details to secure tokens
- Returns encrypted card data

### 2. Checkout Creation
- Uses customer data from CSV file
- Creates checkout session with PayIntelli API
- Generates unique order and customer IDs

### 3. Payment Processing
- Combines tokenized card data with checkout information
- Processes payment through PayIntelli API
- Logs all responses and errors

### 4. Data Flow
```
Customer Data (CSV) + Test Cards (JSON)
         ↓
   Card Tokenization (Datatrans)
         ↓
   Checkout Creation (PayIntelli)
         ↓
   Payment Processing (PayIntelli)
         ↓
   Logging & Monitoring
```

## Logging and Monitoring

### Log Format
All logs include ISO timestamps and flush immediately for real-time monitoring:
```
[2025-08-14T10:30:00.000000] Scheduled run starting...
[2025-08-14T10:30:15.000000] Scheduled run completed successfully.
```

### Log Types
- **Startup Logs**: Configuration and service initialization
- **Scheduled Run Logs**: Automated execution timestamps
- **API Response Logs**: Full API request/response data
- **Error Logs**: Exception details with stack traces
- **Manual Trigger Logs**: User-initiated test executions

### Monitoring Endpoints
- `/health` - Basic health check
- `/` - Service status
- Background thread status logged automatically

## Security Considerations

- **Test Environment**: Uses sandbox/development API endpoints
- **No Real Payments**: All transactions are test/simulation only
- **Secure Tokenization**: Card data is tokenized before transmission
- **Environment Variables**: Sensitive configuration via env vars
- **No Secrets in Code**: All credentials externalized

## Troubleshooting

### Common Issues

1. **Application Won't Start**
   - Check all required files are present (`config/cards.json`, `data/Client002.csv`)
   - Verify Python version (3.11+)
   - Check environment variables

2. **Payment Tests Failing**
   - Verify API endpoints are accessible
   - Check test card configurations
   - Review API credentials (FORM_ID, MERCHANT_ID)

3. **Background Loop Not Running**
   - Ensure `ENABLE_LOOP=true`
   - Check CloudWatch logs for startup messages
   - Verify interval settings

### Debug Mode
Set environment variables for debugging:
```bash
export ENABLE_LOOP=false  # Disable automation for testing
export ITERATIONS_PER_RUN=1  # Reduce iterations for debugging
```

## Performance Considerations

- **Interval Tuning**: Adjust `RUN_INTERVAL_SECONDS` based on load requirements
- **Jitter Configuration**: Use `RUN_JITTER_SECONDS` to avoid thundering herd
- **Resource Usage**: Each iteration processes one payment transaction
- **Timeout Settings**: API calls have 30-60 second timeouts
- **Memory Usage**: CSV data loaded once at startup

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create Pull Request

## License

This project is for internal testing and development purposes.

## Support

For issues and questions:
1. Check CloudWatch logs for error details
2. Review API endpoint responses
3. Verify environment configuration
4. Test with manual `/run` endpoint

---

**Last Updated**: August 14, 2025
