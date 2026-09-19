import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

from database import (
    create_database,
    save_search,
    save_result,
    get_search_history,
    get_results_for_search
)


app = Flask(__name__)


# Allow only approved frontend origins to access API routes
CORS(
    app,
    resources={
        r"/api/*": {
            "origins": [
                "http://localhost:3000",
                "http://127.0.0.1:3000"
            ]
        }
    }
)


# Maximum allowed search length
MAX_QUERY_LENGTH = 200


# Find project folder
project_folder = Path(__file__).resolve().parent

# Load environment variables from .env
env_file = project_folder / ".env"
load_dotenv(env_file)

# Get SerpApi API key
api_key = os.getenv("SERPAPI_API_KEY")

# Make sure database tables exist
create_database()


@app.after_request
def add_security_headers(response):
    """
    Add basic security headers to every Flask response.
    """

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"

    return response


def search_serpapi(query, start=0, num=5):
    """
    Send a search request to SerpApi.

    Returns:
        results
        error message
        HTTP status code
    """

    if not api_key:

        return (
            [],
            "SerpApi API key is not configured.",
            500
        )

    url = "https://serpapi.com/search"

    params = {
        "engine": "google",
        "q": query,
        "api_key": api_key,
        "start": start,
        "num": num
    }

    for attempt in range(1, 3):

        try:

            response = requests.get(
                url,
                params=params,
                timeout=10
            )

            if response.status_code == 429:

                return (
                    [],
                    "SerpApi rate limit reached. Please try again later.",
                    429
                )

            response.raise_for_status()

            data = response.json()

            organic_results = data.get(
                "organic_results",
                []
            )

            cleaned_results = []

            for result in organic_results[:num]:

                cleaned_results.append({
                    "title": result.get(
                        "title",
                        "No title"
                    ),
                    "link": result.get(
                        "link",
                        "No link"
                    ),
                    "snippet": result.get(
                        "snippet",
                        "No snippet available"
                    )
                })

            return cleaned_results, None, 200

        except requests.exceptions.Timeout:

            if attempt < 2:

                time.sleep(2)

            else:

                return (
                    [],
                    "SerpApi request timed out.",
                    504
                )

        except requests.exceptions.RequestException as error:

            return (
                [],
                f"SerpApi request failed: {error}",
                502
            )


@app.route("/", methods=["GET", "POST"])
def home():

    search_term = ""
    results = []
    error = None

    if request.method == "POST":

        search_term = request.form.get(
            "search_term",
            ""
        ).strip()

        if not search_term:

            error = "Please enter something to search for."

        elif len(search_term) > MAX_QUERY_LENGTH:

            error = (
                f"Search must be {MAX_QUERY_LENGTH} "
                "characters or fewer."
            )

        else:

            results, error, status_code = search_serpapi(
                search_term
            )

            if error is None:

                search_id = save_search(search_term)

                for result in results:

                    save_result(
                        search_id,
                        result["title"],
                        result["link"],
                        result["snippet"]
                    )

    return render_template(
        "index.html",
        search_term=search_term,
        results=results,
        error=error
    )


@app.route("/history")
def history():

    searches = get_search_history()

    return render_template(
        "history.html",
        searches=searches
    )


@app.route("/history/<int:search_id>")
def history_results(search_id):

    results = get_results_for_search(search_id)

    return render_template(
        "history_results.html",
        results=results,
        search_id=search_id
    )


@app.route("/api/history")
def api_history():

    searches = get_search_history()

    history_data = []

    for search in searches:

        history_data.append({
            "id": search[0],
            "search_term": search[1],
            "created_at": search[2]
        })

    return jsonify(history_data)


@app.route("/api/history/<int:search_id>")
def api_history_results(search_id):

    results = get_results_for_search(search_id)

    results_data = []

    for result in results:

        results_data.append({
            "id": result[0],
            "title": result[1],
            "link": result[2],
            "snippet": result[3]
        })

    return jsonify(results_data)


@app.route("/api/search", methods=["POST"])
def api_search():

    body = request.get_json(silent=True)

    if body is None:

        return jsonify({
            "error": "JSON body is required."
        }), 400

    if not isinstance(body, dict):

        return jsonify({
            "error": "JSON body must be an object."
        }), 400

    query_value = body.get("query")

    if query_value is None:

        return jsonify({
            "error": "The query field is required."
        }), 400

    if not isinstance(query_value, str):

        return jsonify({
            "error": "The query field must be a string."
        }), 400

    query = query_value.strip()

    if not query:

        return jsonify({
            "error": "The query field cannot be empty."
        }), 400

    if len(query) > MAX_QUERY_LENGTH:

        return jsonify({
            "error": (
                f"The query must be {MAX_QUERY_LENGTH} "
                "characters or fewer."
            )
        }), 400

    page_text = request.args.get(
        "page",
        "1"
    )

    if not page_text.isdigit():

        return jsonify({
            "error": "Page must be a positive whole number."
        }), 400

    page = int(page_text)

    if page < 1:

        return jsonify({
            "error": "Page must be 1 or greater."
        }), 400

    results_per_page = 5

    start = (
        page - 1
    ) * results_per_page

    results, error, status_code = search_serpapi(
        query,
        start=start,
        num=results_per_page
    )

    if error is not None:

        return jsonify({
            "error": error
        }), status_code

    search_id = save_search(query)

    for result in results:

        save_result(
            search_id,
            result["title"],
            result["link"],
            result["snippet"]
        )

    return jsonify({
        "search_id": search_id,
        "query": query,
        "page": page,
        "results_per_page": results_per_page,
        "results": results
    }), 200


if __name__ == "__main__":
    app.run(
        debug=False,
        port=5001
    )