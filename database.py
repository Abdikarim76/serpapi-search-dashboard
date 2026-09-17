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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        search_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        link TEXT NOT NULL,
        snippet TEXT,
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

    search_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return search_id


def save_result(search_id, title, link, snippet):
    connection = sqlite3.connect(database_file)
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO results (search_id, title, link, snippet)
        VALUES (?, ?, ?, ?)
        """,
        (search_id, title, link, snippet)
    )

    connection.commit()
    connection.close()


def get_search_history():
    connection = sqlite3.connect(database_file)
    cursor = connection.cursor()

    cursor.execute("""
    SELECT id, search_term, created_at
    FROM searches
    ORDER BY id DESC
    """)

    searches = cursor.fetchall()

    connection.close()

    return searches


if __name__ == "__main__":
    create_database()

    history = get_search_history()

    print("Saved searches:")
    print()

    for search in history:
        print(search)