# AI Blog Generator

An AI-assisted blog post generator built with Django (DRF) and React. Features authentic source citations, engagement tracking, and multiple writing personas.

## Features

- **AI-Powered Generation**: Uses Anthropic's Claude API for content generation
- **Multiple Personas**: Technical Writer, Storyteller, Industry Analyst, Educator
- **Authentic Sources**: Automatic citation extraction and display
- **Engagement Tracking**: Like/dislike system for content feedback
- **Analytics Dashboard**: Track post performance and user engagement
- **Dark Mode**: Full dark mode support

## Tech Stack

### Backend
- Django 4.2+ with Django REST Framework
- PostgreSQL
- Anthropic Claude SDK
- Service-Oriented Architecture

### Frontend
- React 18 with Vite
- Tailwind CSS
- React Router
- Axios

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- Anthropic API Key

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Run migrations
python manage.py migrate

# Load initial personas
python manage.py loadpersonas

# Create superuser (optional)
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

Backend will be available at `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at `http://localhost:5173`

### Docker Setup

```bash
# Copy environment file
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Start all services
docker-compose up --build

# Run migrations (first time only)
docker-compose exec backend python manage.py migrate

# Load personas
docker-compose exec backend python manage.py loadpersonas
```

## Project Structure

```
ai-blog-generator/
├── backend/
│   ├── ai_blog/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── apps/
│   │       ├── blog/           # Blog app (models, services, views)
│   │       └── core/           # Core services (base classes, exceptions)
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   │   ├── ui/             # Reusable UI components
│   │   │   ├── blog/           # Blog-specific components
│   │   │   └── layout/         # Layout components
│   │   ├── pages/              # Page components
│   │   ├── hooks/              # Custom React hooks
│   │   ├── services/           # API service
│   │   └── contexts/           # React contexts
│   └── package.json
├── docker-compose.yml
└── README.md
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/blog/generate/` | Generate a new blog post |
| GET | `/api/blog/` | List all blog posts |
| GET | `/api/blog/{id}/` | Get a single blog post |
| DELETE | `/api/blog/{id}/` | Delete a blog post |
| POST | `/api/engage/` | Record like/dislike |
| GET | `/api/blog/{id}/engagement/` | Get engagement metrics |
| GET | `/api/personas/` | List all personas |
| GET | `/api/analytics/` | Get analytics data |

## Architecture

The application follows a Service-Oriented Layer (SOL) architecture:

```
Presentation Layer (React)
    ↓ HTTP/REST
API Gateway Layer (DRF Views)
    ↓ Calls
Service Layer (Business Logic)
    ↓ Uses
External Services (Claude API)
    ↓ Persists
Data Layer (PostgreSQL)
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ANTHROPIC_API_KEY` | Claude API key | Yes |
| `DJANGO_SECRET_KEY` | Django secret key | Yes |
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `CORS_ALLOWED_ORIGINS` | Allowed frontend origins | Yes |

## Development

### Running Tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm run lint
```

### Loading Personas

```bash
python manage.py loadpersonas
```

This loads the default personas (Technical Writer, Storyteller, Industry Analyst, Educator).

## License

MIT
