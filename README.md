# Google Search Results Analytics and Synthesis System

## Overview

This project is a backend-focused search analytics system that allows users to search for a keyword and retrieve the top organic Google search results.

The application uses **Serper.dev** to fetch search results, stores them in **MongoDB**, and generates an AI-powered summary using **Ollama with the Mistral 7B model**.

To improve performance and reduce unnecessary API calls, the application caches search results for **60 seconds**. Every new search after the cache expires is stored as a **new version** instead of overwriting existing data.

The entire application can be started using a single `docker compose up --build` command.

---

# Features

- Search Google organic results using Serper.dev
- Store search results in MongoDB
- Version every search instead of updating existing records
- 60-second cache for repeated searches
- AI-generated summary using Ollama (Mistral 7B)
- Simple Streamlit dashboard
- FastAPI backend with Swagger documentation
- Dockerized deployment
- Clean layered architecture
- Proper error handling and validation

---

# Technology Stack

| Layer | Technology |
|--------|------------|
| Backend | FastAPI |
| Frontend | Streamlit |
| Database | MongoDB |
| Search API | Serper.dev |
| AI Model | Ollama + Mistral 7B |
| Containerization | Docker Compose |

---

# System Architecture

```
                    Streamlit UI
                          │
                          ▼
                  FastAPI Backend
                          │
                Search Orchestrator
                          │
      ┌───────────┬────────────┬──────────────┐
      ▼           ▼            ▼              ▼
 Repository   Cache Service  Serper Service  Summary Service
      │                        │              │
      ▼                        ▼              ▼
   MongoDB                 Serper.dev      Ollama
```

---

# Backend Architecture

The backend follows a layered architecture to keep responsibilities separate.

```
Request

↓

API Layer

↓

Orchestrator

↓

Business Services

↓

Repository

↓

MongoDB
```

## API Layer

The API layer receives requests, validates input using Pydantic models, and returns standardized responses.

It does not contain business logic.

---

## Orchestrator

The orchestrator coordinates the complete search flow.

It is responsible for:

- Checking the cache
- Calling the search provider
- Generating summaries
- Creating document versions
- Saving data
- Returning responses

---

## Services

Business logic is separated into small services.

### Cache Service

Determines whether an existing search can be returned from cache.

### Serper Service

Communicates with the Serper.dev API and converts the response into application models.

### Summary Service

Sends search results to Ollama and generates a one-paragraph summary using Mistral 7B.

### Version Service

Calculates the next document version for a keyword.

---

## Repository

The repository handles all MongoDB operations.

The rest of the application never communicates with MongoDB directly.

---

# Search Flow

When a user searches for a keyword, the following steps occur:

```
User enters keyword

↓

Validate Request

↓

Check Latest Search

↓

Cache Available?

↓

Yes
│
└── Return Cached Result

No
│
▼

Call Serper.dev

↓

Parse Results

↓

Generate AI Summary

↓

Calculate Version

↓

Store Document

↓

Return Response
```

---

# Versioning Strategy

The application never overwrites existing documents.

Example:

```
python

↓

Version 1

↓

Version 2

↓

Version 3
```

This preserves complete search history and allows previous searches to be audited.

---

# Cache Strategy

The application uses a simple MongoDB-based cache.

When a keyword is searched:

- Retrieve the latest version
- Compare the timestamp with the current time
- If the search is less than **60 seconds old**, return the stored document
- Otherwise perform a new search

No additional caching system is required.

---

# Database Schema

Each search is stored as a single MongoDB document.

```json
{
    "keyword": "python",
    "version": 2,
    "provider": "SERPER",
    "status": "SUCCESS",
    "summary": "Python is a popular programming language...",
    "results": [
        {
            "rank": 1,
            "title": "Welcome to Python.org",
            "url": "https://www.python.org",
            "snippet": "Official Python website"
        }
    ],
    "created_at": "2026-07-10T12:30:00Z"
}
```

---

# API Endpoints

## Health Check

```
GET /health
```

Returns application health status.

---

## Search

```
POST /search
```

Example request:

```json
{
    "keyword": "python"
}
```

Example response:

```json
{
    "keyword": "python",
    "version": 2,
    "cached": false,
    "summary": "...",
    "results": []
}
```

---

# Error Handling

The application handles common failure scenarios gracefully.

### No Search Results

- Stores an empty results array
- Returns a successful response

---

### Missing Snippets

If a result does not contain a snippet, the application stores `null` instead of failing.

---

### Serper API Failure

Returns an appropriate error message without crashing the application.

---

### Ollama Failure

Search results are still stored successfully.

Only the summary is returned as `null`.

---

### Database Errors

MongoDB exceptions are converted into user-friendly API responses.

---

# Project Structure

```
SERP_Practical_Assessment/

├── docker-compose.yml
├── README.md

├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── api/
│       ├── config/
│       ├── database/
│       ├── models/
│       ├── orchestration/
│       ├── repository/
│       ├── schemas/
│       ├── services/
│       ├── utils/
│       └── main.py

└── frontend/
    ├── Dockerfile
    ├── app.py
    └── api_client.py
```

---

# Running the Project

## Prerequisites

- Docker
- Docker Compose

---

## Clone the Repository

```bash
git clone <repository-url>

cd SERP_Practical_Assessment
```

---

## Configure Environment Variables

Create a `.env` file inside the `backend` directory.

Example:

```env
SERPER_API_KEY=YOUR_SERPER_API_KEY

MONGO_URI=mongodb://mongodb:27017

DATABASE_NAME=google_search_db

CACHE_EXPIRY_SECONDS=60

OLLAMA_URL=http://ollama:11434
```

---

## Start the Application

```bash
docker compose up --build
```

Docker will start:

- MongoDB
- Ollama
- FastAPI Backend
- Streamlit Frontend

---

# Access the Application

| Service | URL |
|----------|-----|
| Streamlit Dashboard | http://localhost:8501 |
| Swagger Documentation | http://localhost:8000/docs |
| Health API | http://localhost:8000/health |

---

# Testing

### First Search

- Calls Serper.dev
- Generates AI summary
- Stores Version 1

---

### Second Search (within 60 seconds)

- Returns cached result
- No API call
- No AI generation

---

### Third Search (after 60 seconds)

- Calls Serper.dev again
- Generates a new summary
- Stores Version 2

---

# Design Principles

This project follows several software engineering best practices:

- SOLID Principles
- DRY (Don't Repeat Yourself)
- Repository Pattern
- Service Layer Pattern
- Dependency Injection
- Layered Architecture
- Separation of Concerns
- Pydantic Validation
- Global Exception Handling

---

# Future Improvements

Possible enhancements include:

- Redis for distributed caching
- Background processing for AI summaries
- Authentication and authorization
- Search history page
- Pagination
- Multiple search providers
- Unit and integration tests
- Monitoring and metrics

---

# Conclusion

This project demonstrates how to build a clean, maintainable, and scalable search analytics system using FastAPI, MongoDB, Streamlit, and Ollama.

The architecture keeps responsibilities well separated, supports versioned data storage, minimizes unnecessary API calls through caching, and provides AI-generated summaries while remaining simple enough to understand and extend.
