import sqlite3
from pathlib import Path


# Find the project folder
project_folder = Path(__file__).resolve().parent

# Database file location
database_file = project_folder / "search_results.db"


def create_database():
    connection = sqlite3.connect(database_file)
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS searches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        search_term TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    connection.commit()
    connection.close()


def save_search(search_term):
    connection = sqlite3.connect(database_file)
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO searches (search_term) VALUES (?)",
        (search_term,)
    )

    connection.commit()
    connection.close()


if __name__ == "__main__":
    create_database()
    print("Database ready.")