# AWS App Runner Environment Configuration

## Required Environment Variables for Deployment

### Core Application Settings
- **PORT**: `8080` (Required by AWS App Runner)
- **RUN_INTERVAL_SECONDS**: `300` (5 minutes between automated runs)
- **RUN_JITTER_SECONDS**: `120` (±2 minutes random delay)
- **ITERATIONS_PER_RUN**: `2` (Number of test iterations per run)
- **ENABLE_LOOP**: `true` (Enable background automation loop)

### File Paths (relative to app root)
- **CSV_PATH**: `data/Client002.csv`
- **CARDS_PATH**: `config/cards.json`

### Payment Gateway Configuration
- **CLIENT_ID**: `client_002` (Client identifier)
- **FORM_ID**: `250729103005965673` (Datatrans form identifier)
- **MERCHANT_ID**: `1110020135` (Merchant identifier)

### Optional API URLs (using defaults if not set)
- **TOKENIZATION_URL**: `https://pay.sandbox.datatrans.com/upp/payment/SecureFields/paymentField`
- **CHECKOUT_URL**: `https://checkout-api-dev.payintelli.com/api/v1/checkout/create`
- **PAYMENT_URL**: `https://api-dev.payintelli.com/api/v1/payments/create`

## AWS App Runner Deployment Options

### Option 1: Source Code Deployment (Manual Configuration)
Configure directly in AWS App Runner console without using apprunner.yaml file.

**Manual Configuration Steps:**
1. **Runtime**: Python 3.11
2. **Build Command**: `python -m pip install --upgrade pip && pip install -r requirements.txt`
3. **Start Command**: `python -m uvicorn app:app --host 0.0.0.0 --port 8080`
4. **Port**: 8080

### Option 2: Container Deployment
Use the `Dockerfile` for container-based deployment via ECR.

## Health Check Endpoints
- **Health Check**: `GET /health`
- **Root Status**: `GET /`
- **Manual Trigger**: `POST /run?iterations=<number>`

## Important Notes
1. The application will automatically start the background loop on startup if `ENABLE_LOOP=true`
2. All file paths are relative to the application root directory
3. The app logs all activities with timestamps for monitoring in AWS CloudWatch
4. Background processes run as daemon threads and won't block the main application
