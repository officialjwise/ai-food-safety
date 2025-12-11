# AI Food Safety & Market Intelligence Platform - Backend

> Production-ready FastAPI backend with AI-powered food safety detection, FAO/USDA nutrition data, and market intelligence.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- SMTP credentials (for admin OTP)

### Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 3. Run migrations
alembic upgrade head

# 4. Seed sample data
python -m app.db.seed_nutrition

# 5. Start server
uvicorn app.main:app --reload
```

### Access
- API Docs: http://localhost:8000/api/v1/docs
- Health Check: http://localhost:8000/health

## 🔐 Default Admin
- Email: `admin@foodsafety.com`
- Password: `admin123` ⚠️ Change in production!

## 📚 Key Features

- **Authentication**: JWT + OTP for admins
- **Food Safety**: AI-powered image analysis (stubbed)
- **Nutrition**: FAO/USDA database with 30+ nutrients
- **Market Intel**: Price tracking & analytics
- **Surplus**: Food waste reduction system
- **Production**: Logging, error handling, health checks

## 📖 Documentation

- [Nutrition Guide](NUTRITION_GUIDE.md) - FAO/USDA integration
- [Main README](../README.md) - Full project overview

## 🐳 Docker

```bash
docker-compose up --build
```

## 🧪 Testing

```bash
pytest
```

---

See [Main README](../README.md) for complete documentation.
