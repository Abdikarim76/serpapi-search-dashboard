# SerpApi Search Dashboard

A full-stack search dashboard built with Python, Flask, JavaScript, SQLite, and SerpApi.

## Features

- Google search through SerpApi
- Flask backend
- JavaScript Fetch API frontend
- SQLite search history
- REST API endpoints
- Pagination
- Input validation
- Timeout and retry handling
- Rate-limit handling
- Controlled CORS
- HTTP security headers
- Environment variable protection

## Technologies

Python, Flask, JavaScript, HTML, CSS, SQLite, REST API, SerpApi, Requests, python-dotenv, Flask-CORS, and Git.

## Installation

1. Create a virtual environment:

    python -m venv .venv

2. Activate it on macOS or Linux:

    source .venv/bin/activate

3. Install dependencies:

    pip install -r requirements.txt

4. Create the environment file:

    cp .env.example .env

5. Add your SerpApi key to .env:

    SERPAPI_API_KEY=your_real_serpapi_api_key

6. Run the application:

    python app.py

7. Open:

    http://127.0.0.1:5001

## REST API

POST /api/search
POST /api/search?page=2
GET /api/history
GET /api/history/<search_id>

Example search body:

    {"query": "python flask"}

## Database

The application uses SQLite with searches and results tables. results.search_id is a foreign key to searches.id with ON DELETE CASCADE.

## Security

- SerpApi key stored in .env
- .env excluded from Git
- Safe .env.example file
- Input validation
- Restricted CORS origins
- Flask debug mode disabled
- HTTP security headers

## Author

Abdikarim Ismail Muse

GitHub: https://github.com/Abdikarim76
