import os
from pathlib import Path

import requests
from dotenv import load_dotenv


# Find the project folder
project_folder = Path(__file__).resolve().parent

# Find and load the .env file
env_file = project_folder / ".env"
load_dotenv(env_file)

# Get SerpApi key
api_key = os.getenv("SERPAPI_API_KEY")


# Ask the user what they want to search
search_term = input("What do you want to search for? ")


# SerpApi endpoint
url = "https://serpapi.com/search"


# Parameters sent to SerpApi
params = {
    "engine": "google",
    "q": search_term,
    "api_key": api_key
}


# Send GET request
response = requests.get(url, params=params)


# Convert JSON response into Python data
data = response.json()


print()
print("Status code:", response.status_code)
print()


# Get normal Google search results
results = data["organic_results"]


# Display the first 5 results
for result in results[:5]:
    print(result["title"])
    print(result["link"])
    print()