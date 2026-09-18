import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify

from database import (
    create_database,
    save_search,
    save_result,
    get_search_history,
    get_results_for_search
)


app = Flask(__name__)


# Find project folder
project_folder = Path(__file__).resolve().parent

# Load environment variables
env_file = project_folder / ".env"
load_dotenv(env_file)

# Get SerpApi API key
api_key = os.getenv("SERPAPI_API_KEY")

# Make sure database tables exist
create_database()


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

        else:

            url = "https://serpapi.com/search"

            params = {
                "engine": "google",
                "q": search_term,
                "api_key": api_key
            }

            response = None

            for attempt in range(1, 3):

                try:

                    response = requests.get(
                        url,
                        params=params,
                        timeout=10
                    )

                    response.raise_for_status()

                    break

                except requests.exceptions.Timeout:

                    if attempt < 2:
                        time.sleep(2)

                    else:
                        error = "The search request timed out."

                except requests.exceptions.RequestException as request_error:

                    error = f"Search request failed: {request_error}"

                    break

            if response is not None and error is None:

                data = response.json()

                organic_results = data.get(
                    "organic_results",
                    []
                )

                search_id = save_search(search_term)

                for result in organic_results[:5]:

                    cleaned_result = {
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
                    }

                    results.append(cleaned_result)

                    save_result(
                        search_id,
                        cleaned_result["title"],
                        cleaned_result["link"],
                        cleaned_result["snippet"]
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

    # Read JSON sent by the client
    body = request.get_json(silent=True)

    if not body:
        return jsonify({
            "error": "JSON body is required."
        }), 400

    query = body.get("query", "").strip()

    if not query:
        return jsonify({
            "error": "The query field is required."
        }), 400

    url = "https://serpapi.com/search"

    params = {
        "engine": "google",
        "q": query,
        "api_key": api_key
    }

    response = None

    for attempt in range(1, 3):

        try:

            response = requests.get(
                url,
                params=params,
                timeout=10
            )

            response.raise_for_status()

            break

        except requests.exceptions.Timeout:

            if attempt < 2:
                time.sleep(2)

            else:
                return jsonify({
                    "error": "SerpApi request timed out."
                }), 504

        except requests.exceptions.RequestException as error:

            return jsonify({
                "error": str(error)
            }), 502

    data = response.json()

    organic_results = data.get(
        "organic_results",
        []
    )

    search_id = save_search(query)

    cleaned_results = []

    for result in organic_results[:5]:

        cleaned_result = {
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
        }

        cleaned_results.append(cleaned_result)

        save_result(
            search_id,
            cleaned_result["title"],
            cleaned_result["link"],
            cleaned_result["snippet"]
        )

    return jsonify({
        "search_id": search_id,
        "query": query,
        "results": cleaned_results
    }), 200


if __name__ == "__main__":
    app.run(debug=True)