# Setup Guide - AI Food Safety Platform Backend

## Current Status

✅ **Completed:**
- Git repository initialized
- All code committed to main branch
- Remote added: https://github.com/officialjwise/ai-food-safety.git
- Dependencies installed
- Alembic configured

⚠️ **Next Steps Required:**

## 1. Push to GitHub

```bash
cd /Users/phill/Desktop/food_safety_platform/backend
git push -u origin main
```

## 2. Database Setup

The migrations are failing because the database connection isn't configured yet. You need to:

### Option A: Start PostgreSQL locally

```bash
# Check if PostgreSQL is running
pg_isready

# If not running, start it
brew services start postgresql@15
# OR
postgres -D /usr/local/var/postgres

# Create the database
createdb food_safety

# Verify connection
psql -d food_safety -c "SELECT version();"
```

### Option B: Use Docker for Database

```bash
cd /Users/phill/Desktop/food_safety_platform/backend

# Start only PostgreSQL and Redis
docker-compose up -d db redis

# Verify containers are running
docker ps
```

## 3. Run Migrations

Once the database is accessible:

```bash
# Generate initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

## 4. Seed Sample Data

```bash
# Seed nutrition data (10 sample foods)
python -m app.db.seed_nutrition
```

Select option 1 when prompted to seed sample data.

## 5. Start the Application

```bash
# Start the FastAPI server
uvicorn app.main:app --reload

# Or specify host/port
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 6. Verify Installation

### Test the API

1. Open browser: http://localhost:8000/health
   - Should return: `{"status": "healthy"}`

2. Open Swagger UI: http://localhost:8000/api/v1/docs
   - Test `/auth/signup` to create a user
   - Test `/auth/login` to get tokens

### Test Default Admin

```bash
# Request OTP
curl -X POST "http://localhost:8000/api/v1/auth/admin/request-otp" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@foodsafety.com"}'

# Check your SMTP email for the OTP code
# Then verify:
curl -X POST "http://localhost:8000/api/v1/auth/admin/verify-otp" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@foodsafety.com", "code": "123456"}'
```

## Troubleshooting

### Database Connection Issues

If you see `nodename nor servname provided, or not known`:

1. Check `.env` file - ensure DATABASE_URL is correct
2. Verify PostgreSQL is running: `pg_isready`
3. Test connection: `psql -h localhost -U postgres -d food_safety`

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill if needed
kill -9 <PID>
```

### Redis Connection Issues

```bash
# Check Redis is running
redis-cli ping
# Should return: PONG

# Start if needed
brew services start redis
```

### SMTP Email Not Working

OTP emails require SMTP configuration. Update `.env`:

```env
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # For Gmail, use App Password
```

For Gmail App Password:
1. Go to Google Account → Security
2. Enable 2-Step Verification
3. Generate App Password
4. Use that password in `.env`

## Database Migration Commands

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history

# View current version
alembic current
```

## Quick Start (All Steps)

```bash
# 1. Navigate to project
cd /Users/phill/Desktop/food_safety_platform/backend

# 2. Start database (Docker)
docker-compose up -d db redis

# 3. Run migrations
alembic upgrade head

# 4. Seed data
python -m app.db.seed_nutrition

# 5. Start server
uvicorn app.main:app --reload

# 6. Test in browser
open http://localhost:8000/api/v1/docs
```

## Project Structure

```
backend/
├── alembic/              # Database migrations
│   ├── versions/         # Migration files
│   └── env.py           # Alembic configuration
├── app/
│   ├── api/v1/routes/   # API endpoints
│   ├── core/            # Security, logging, middleware
│   ├── db/              # Database models & utilities
│   ├── schemas/         # Pydantic models
│   ├── services/        # Business logic services
│   └── main.py          # FastAPI app
├── logs/                # Application logs
├── tests/               # Test files
├── .env                 # Environment variables
├── alembic.ini         # Alembic config
├── docker-compose.yml  # Docker setup
└── requirements.txt    # Python dependencies
```

## Available Scripts

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app

# Seed nutrition data
python -m app.db.seed_nutrition

# Start production server
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

## Next Development Steps

1. Implement real ML model for food safety detection
2. Integrate actual USDA API for nutrition data
3. Add more comprehensive tests
4. Set up CI/CD pipeline
5. Deploy to production environment

---

**Need Help?** Check the main [README.md](README.md) or [NUTRITION_GUIDE.md](NUTRITION_GUIDE.md)
