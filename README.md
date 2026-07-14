# FastAPI Backend API

A production-style REST API built with **FastAPI**, **PostgreSQL**, **SQLAlchemy**, **Alembic**, and **JWT Authentication**.

## Features

- User Registration
- User Login
- JWT Authentication
- Refresh Tokens
- Role-Based Authorization
- Admin User Management
- User Profile Update
- Change Password
- Forgot Password (OTP)
- Verify OTP
- Reset Password
- PostgreSQL Database
- Alembic Database Migrations

---

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- Pydantic
- Passlib (bcrypt)
- Python-Jose (JWT)

---

## Project Structure

```
app/
│
├── core/
├── database/
├── models/
├── routers/
├── schemas/
├── services/
├── utils/
│
alembic/
requirements.txt
main.py
```

---

## Installation

Clone the repository

```bash
git clone https://github.com/stanley-dev-code/my-fastapi-backend.git
```

Move into the project

```bash
cd my-fastapi-backend
```

Create a virtual environment

```bash
python -m venv fastenv
```

Activate it

Windows

```bash
fastenv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file.

Example:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/stanley_db

SECRET_KEY=your_secret_key

REFRESH_SECRET_KEY=your_refresh_secret_key

ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=30

REFRESH_TOKEN_EXPIRE_DAYS=7
```

---

## Database Migration

Create tables

```bash
alembic upgrade head
```

---

## Run the Project

```bash
uvicorn app.main:app --reload
```

API Documentation

```
http://127.0.0.1:8000/docs
```

---

## API Endpoints

### Authentication

- POST /auth/register
- POST /auth/login
- POST /auth/refresh
- POST /auth/forgot-password
- POST /auth/verify-otp
- POST /auth/reset-password

### Users

- GET /users/me
- PATCH /users/me
- PATCH /users/change-password
- DELETE /users/me

### Admin

- GET /users
- POST /users/admin/create-user
- PATCH /users/{user_id}/role
- DELETE /users/{user_id}

---

## Author

Stanley Santiago

GitHub:
https://github.com/stanley-dev-code