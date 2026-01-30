# Spanish OCR API

Simple FastAPI service for Spanish text recognition using RapidOCR with PPOCRv5 Latin models and ONNX runtime. Supports both images and PDFs.

## Features

- **Spanish OCR** using PPOCRv5 Latin models
- **Two model types**: Mobile (faster, ~10MB) and Server (more accurate, ~100MB)
- **PDF support**: Multi-page PDF processing with concatenated output
- **10MB upload limit** for files
- **Docker ready** with health checks
- **Dokploy compatible** for easy deployment

## Quick Start

### Deploy with Dokploy (Recommended)

1. **Create a new service in Dokploy:**
   - Go to your Dokploy dashboard
   - Click "Create Service" → "Docker Compose"
   - Connect your Git repository or upload files

2. **Set environment variables in Dokploy:**
   ```
   MODEL_TYPE=mobile
   TEXT_SCORE_THRESHOLD=0.5
   PORT=5000
   MAX_FILE_SIZE_MB=10
   ```

3. **Configure port mapping:**
   - Internal Port: `5000`
   - External Port: Choose available port (e.g., `5000`)

4. **Deploy:**
   - Dokploy will automatically build and deploy using the Dockerfile
   - Health checks are configured automatically via the Dockerfile

5. **Access your API:**
   - `https://your-domain.com/docs` (Swagger UI)
   - `https://your-domain.com/health` (Health check)

**Important Dokploy Notes:**
- Models (~10-100MB) will be downloaded on first request - first startup may take 1-2 minutes
- Volume for model caching is configured in docker-compose.yml
- Health checks ensure the service is ready before routing traffic
- Use the Mobile model initially to reduce startup time and resource usage
- **Local testing requires Python 3.12 or lower** (rapidocr-onnxruntime doesn't support Python 3.13 yet)

## Quick Start

### Using Docker Compose (Recommended)

1. Copy environment file:
```bash
cp .env.example .env
```

2. Build and run:
```bash
docker-compose up -d
```

3. Check health:
```bash
curl http://localhost:5000/health
```

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python app.py
```

## API Usage

### OCR Endpoint

**POST** `/ocr`

**Parameters:**
- `file` (required): Image file (jpg, png, etc.) or PDF
- `model_type` (optional): `mobile` (default) or `server`

**Example - Image with Mobile model:**
```bash
curl -X POST "http://localhost:5000/ocr?model_type=mobile" \
  -F "file=@document.jpg"
```

**Example - PDF with Server model:**
```bash
curl -X POST "http://localhost:5000/ocr?model_type=server" \
  -F "file=@document.pdf"
```

**Example - Python:**
```python
import requests

with open("document.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:5000/ocr",
        params={"model_type": "mobile"},
        files={"file": f}
    )

data = response.json()
print(data["text"])
```

**Response:**
```json
{
  "text": "Extracted Spanish text from the document...",
  "model_type": "mobile",
  "file_name": "document.jpg"
}
```

### Health Check Endpoint

**GET** `/health`

```bash
curl http://localhost:5000/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "spanish-ocr"
}
```

## Configuration

Edit `.env` or set environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_TYPE` | `mobile` | Model size: `mobile` or `server` |
| `TEXT_SCORE_THRESHOLD` | `0.5` | OCR confidence threshold (0.0-1.0) |
| `PORT` | `5000` | Server port |
| `MAX_FILE_SIZE_MB` | `10` | Maximum upload size in MB |

## Model Comparison

| Model | Size | Speed | Use Case |
|-------|------|-------|----------|
| **Mobile** | ~10MB | Fast | Clean documents, general use |
| **Server** | ~100MB | Slower | Low-quality images, complex layouts |

## Notes

- Models are downloaded automatically on first use (~10-100MB depending on model type)
- Models are cached in the `models/` directory
- Multi-page PDFs return concatenated text with double line breaks between pages
- Supports Latin alphabet languages (Spanish, English, French, Portuguese, etc.)

## Docker Commands

```bash
# Build image
docker-compose build

# Start service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop service
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

## Dokploy Deployment Guide

### Method 1: Git Repository (Recommended)

1. **Push to Git:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. **In Dokploy:**
   - Create new service → Docker Compose
   - Select your Git repository
   - Branch: `main`
   - Docker Compose Path: `docker-compose.yml`

3. **Environment Variables:**
   Add in Dokploy's environment section:
   ```
   MODEL_TYPE=mobile
   TEXT_SCORE_THRESHOLD=0.5
   PORT=5000
   MAX_FILE_SIZE_MB=10
   ```

4. **Port Configuration:**
   - Container Port: `5000`
   - Public Port: Your choice (e.g., `5000`)

5. **Deploy** and wait for build completion (~3-5 minutes first time)

### Method 2: Direct Docker Deployment

1. **In Dokploy:**
   - Create new service → Docker Image
   - Build from repository or upload Dockerfile

2. **Set environment variables** as above

3. **Configure volumes:**
   - Mount path: `/root/.cache/modelscope`
   - Host path: Let Dokploy manage (for model caching)

### Troubleshooting Dokploy

**Service won't start:**
- Check logs in Dokploy dashboard
- Ensure port 5000 is not in use
- Verify environment variables are set

**First request is slow:**
- Models download on first use (~10-100MB)
- Subsequent requests will be fast
- Check logs to see download progress

**Out of memory:**
- Server model needs ~2GB RAM
- Mobile model needs ~1GB RAM
- Increase container memory limit in Dokploy

**Health check failing:**
- Wait 40 seconds after container start
- Models need to initialize first
- Check `/health` endpoint manually

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:5000/docs
- ReDoc: http://localhost:5000/redoc
