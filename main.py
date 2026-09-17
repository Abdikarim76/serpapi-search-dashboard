import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

from database import (
    create_database,
    save_search,
    save_result,
    get_search_history,
    get_results_for_search
)


# Find project folder
project_folder = Path(__file__).resolve().parent

# Load .env file
env_file = project_folder / ".env"
load_dotenv(env_file)

# Get SerpApi key
api_key = os.getenv("SERPAPI_API_KEY")

# Make sure database tables exist
create_database()


def new_search():
    search_term = input("\nWhat do you want to search for? ")

    url = "https://serpapi.com/search"

    params = {
        "engine": "google",
        "q": search_term,
        "api_key": api_key
    }

    response = None

    # Try the request a maximum of 2 times
    for attempt in range(1, 3):

        try:
            print(f"\nRequest attempt {attempt}...")

            response = requests.get(
                url,
                params=params,
                timeout=10
            )

            response.raise_for_status()

            # Request succeeded
            break

        except requests.exceptions.Timeout:

            print("The request timed out.")

            if attempt < 2:
                print("Trying again...")
                time.sleep(2)

            else:
                print("The request failed after 2 attempts.")
                return

        except requests.exceptions.RequestException as error:
            print("Request failed:", error)
            return

    # Convert JSON response into Python data
    data = response.json()

    print()
    print("Status code:", response.status_code)
    print()

    # Only save after the API request succeeds
    search_id = save_search(search_term)

    results = data.get("organic_results", [])

    cleaned_results = []

    for result in results[:5]:

        cleaned_result = {
            "title": result.get("title", "No title"),
            "link": result.get("link", "No link"),
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

    if not cleaned_results:
        print("No search results were found.")

    else:
        for number, result in enumerate(
            cleaned_results,
            start=1
        ):
            print(f"Result {number}")
            print("Title:", result["title"])
            print("Link:", result["link"])
            print("Snippet:", result["snippet"])
            print()


def show_history():
    history = get_search_history()

    print("\nSaved searches:")
    print()

    if not history:
        print("No saved searches yet.")
        return

    for search in history:
        search_id = search[0]
        search_term = search[1]
        created_at = search[2]

        print(f"{search_id}. {search_term} | {created_at}")

    print()

    selected_id = input(
        "Enter a search ID to view its saved results, "
        "or press Enter to go back: "
    )

    if selected_id == "":
        return

    if not selected_id.isdigit():
        print("Invalid search ID.")
        return

    selected_id = int(selected_id)

    results = get_results_for_search(selected_id)

    if not results:
        print("No saved results found for that search.")
        return

    print()

    for number, result in enumerate(results, start=1):
        title = result[1]
        link = result[2]
        snippet = result[3]

        print(f"Result {number}")
        print("Title:", title)
        print("Link:", link)
        print("Snippet:", snippet)
        print()


while True:

    print("\n===== SerpApi Search CLI =====")
    print("1. New search")
    print("2. View search history")
    print("3. Exit")

    choice = input("\nChoose an option: ")

    if choice == "1":
        new_search()

    elif choice == "2":
        show_history()

    elif choice == "3":
        print("Goodbye.")
        break

    else:
        print("Invalid option. Choose 1, 2, or 3.")