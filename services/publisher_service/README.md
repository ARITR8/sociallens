# Publisher Service

The Publisher Service is responsible for generating AI-powered articles and publishing them to WordPress. It supports multiple LLM providers for flexible content generation.

## Features

- **Multi-Provider LLM Support**: Switch between AWS Bedrock (Claude) and Google Gemini
- **Article Generation**: AI-powered content creation with SEO optimization
- **WordPress Integration**: Automated publishing to WordPress sites
- **Content Quality Checks**: Automated validation of generated content
- **Batch Processing**: Process multiple articles efficiently
- **Retry Mechanism**: Automatic retry for failed publications

## Prerequisites

- Python 3.10+
- PostgreSQL database
- WordPress site with REST API enabled
- Either AWS Bedrock access OR Google Gemini API key

## Installation

1. **Create virtual environment:**
```bash
cd services/publisher_service
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Run database migrations:**
```bash
alembic upgrade head
```

## Configuration

### LLM Provider Setup

The service supports two LLM providers. Configure the `LLM_PROVIDER` environment variable to choose:

#### Option 1: Google Gemini (Recommended for this deployment)

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL_ID=gemini-pro
GEMINI_VISION_MODEL_ID=gemini-pro-vision
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_TOKENS=4096
```

**How to get Gemini API Key:**
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key to your `.env` file

#### Option 2: AWS Bedrock (Claude)

```env
LLM_PROVIDER=bedrock
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
BEDROCK_TEMPERATURE=0.7
BEDROCK_MAX_TOKENS=4096
```

### WordPress Configuration

```env
WP_API_URL=https://your-site.com/wp-json/wp/v2
WP_USERNAME=your_wordpress_username
WP_APP_PASSWORD=your_wordpress_app_password
WP_CATEGORY_ID=1
WP_DEFAULT_STATUS=draft
```

### Database Configuration

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=newsettler
POSTGRES_USER=newsettler_user
POSTGRES_PASSWORD=newsettler_pass
POSTGRES_SCHEMA=publisher
```

## Running the Service

### Development Mode

```bash
uvicorn app.main:app --reload --port 8001
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --workers 4
```

### Using Docker

```bash
docker-compose up -d
```

## API Endpoints

### Article Management

- `POST /api/v1/articles/` - Create a new article
- `GET /api/v1/articles/{article_id}` - Get article by ID
- `PUT /api/v1/articles/{article_id}` - Update article
- `GET /api/v1/articles/` - List articles
- `POST /api/v1/articles/{article_id}/publish` - Publish article to WordPress

### Batch Operations

- `POST /api/v1/process-batch` - Process multiple unpublished articles
- `POST /api/v1/retry-failed` - Retry failed publications

### Health & Stats

- `GET /api/v1/health` - Service health check
- `GET /api/v1/stats` - Publishing statistics

## API Documentation

Once the service is running, visit:
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

## Architecture

```
app/
├── api/                    # API endpoints
│   └── v1/
│       └── endpoints/
│           └── publisher.py
├── core/                   # Core configurations
│   ├── config.py          # Settings and environment variables
│   ├── database.py        # Database connection
│   └── logging.py         # Logging configuration
├── domain/                 # Domain models
│   ├── models/            # Business models
│   └── templates/         # Prompt templates
├── infrastructure/         # External integrations
│   ├── database/          # Database models & repositories
│   ├── llm/               # LLM provider clients
│   │   ├── base.py        # Base LLM interface
│   │   ├── bedrock_client.py  # AWS Bedrock implementation
│   │   ├── gemini_client.py   # Google Gemini implementation
│   │   └── factory.py     # Client factory
│   └── wordpress/         # WordPress API client
├── services/              # Business logic
│   ├── content_generator.py  # Content generation service
│   └── publisher_service.py  # Publishing orchestration
└── main.py               # FastAPI application
```

## Switching Between LLM Providers

To switch providers, simply update your `.env` file:

```bash
# Switch to Gemini
LLM_PROVIDER=gemini

# Or switch to Bedrock
LLM_PROVIDER=bedrock
```

Restart the service for changes to take effect.

## Troubleshooting

### Gemini API Issues

**Error: "Gemini API key not set"**
- Ensure `GEMINI_API_KEY` is set in your `.env` file
- Verify the API key is valid at [Google AI Studio](https://makersuite.google.com/)

**Error: "Rate limit exceeded"**
- Gemini has rate limits based on your quota
- Check your quota at [Google AI Studio](https://makersuite.google.com/)
- Consider implementing rate limiting in your application

### Bedrock API Issues

**Error: "AWS credentials not set"**
- Ensure `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` are set
- Verify your AWS credentials have Bedrock permissions

**Error: "Model not found"**
- Verify Bedrock model access in your AWS account
- Check the model ID is correct for your region

### WordPress Issues

**Error: "WordPress connection failed"**
- Verify your WordPress site URL is correct
- Ensure REST API is enabled on WordPress
- Check application password is valid

## Development

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests and linting
4. Submit a pull request

## License

[Your License Here]

## Support

For issues and questions, please contact [Your Contact Info]
