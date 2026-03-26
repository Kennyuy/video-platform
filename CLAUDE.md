# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A video and audio platform built with FastAPI (backend) and Vue 3 (frontend). The platform supports video/audio uploads, playback, user interactions (likes, coins, favorites), and includes both admin and user content management interfaces.

## Development Commands

### Backend (from `/backend`)

```bash
# Create virtual environment and install dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials

# Run development server (port 8002 in current deployment)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8002
```

### Frontend (from `/frontend`)

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Architecture

### Backend Structure

- `app/main.py` - FastAPI application entry point, CORS config, route registration
- `app/config.py` - Settings loaded from environment variables via pydantic-settings
- `app/database.py` - SQLAlchemy engine, session factory, and `get_db()` dependency
- `app/models/` - SQLAlchemy ORM models (User, Video, Audio, Comment, interactions, etc.)
- `app/schemas/` - Pydantic request/response schemas
- `app/api/` - FastAPI routers organized by domain:
  - `auth.py` - User authentication (login, register, JWT tokens)
  - `admin_videos.py` - Admin video management endpoints
  - `videos.py` - Public video endpoints
  - `user_videos.py` - User video upload/management
  - `audios.py` - Public audio endpoints
  - `user_audios.py` - User audio upload/management
- `app/utils/auth.py` - JWT token utilities and password hashing

### Frontend Structure

- `src/main.ts` - Vue app initialization with Pinia and Vue Router
- `src/router/index.ts` - Route definitions with auth guards (requiresAuth, requiresAdmin)
- `src/store/user.ts` - Pinia store for user state, login/logout, token management
- `src/api/index.ts` - API client functions using axios
- `src/utils/request.ts` - Axios instance with auth interceptors
- `src/views/` - Page components organized by area:
  - Home, Videos, Audios, Login, Register, VideoDetail, AudioDetail
  - `admin/` - Admin management pages
  - `studio/` - User content management (upload videos/audios)
- `src/components/` - Reusable components (Navbar, Loading)

### API Proxy

Frontend dev server proxies `/api` requests to `http://localhost:8002` (configured in `vite.config.ts`).

## Key Domain Models

- **User**: username, email, role (admin/user), coins (virtual currency)
- **Video/Audio**: title, description, cover, media URL, duration, visibility, status
- **User Interactions**: likes, coins (投币), favorites, shares per video/audio
- **Coin Transactions**: Daily login rewards, coin spending for interactions

## Authentication

- JWT tokens stored in localStorage
- Backend uses `python-jose` for JWT, `passlib` for bcrypt password hashing
- Frontend attaches `Authorization: Bearer <token>` header via axios interceptor
- 401 responses trigger automatic redirect to `/login`