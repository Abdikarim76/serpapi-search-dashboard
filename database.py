import sqlite3
from pathlib import Path


# Find the project folder
project_folder = Path(__file__).resolve().parent

# Database file location
database_file = project_folder / "search_results.db"


def get_connection():
    """
    Open a connection to SQLite
    and enable foreign key checking.
    """

    connection = sqlite3.connect(database_file)

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    return connection


def create_results_table(cursor):
    """
    Create the results table with
    a foreign key relationship.
    """

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        search_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        link TEXT NOT NULL,
        snippet TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (search_id)
            REFERENCES searches(id)
            ON DELETE CASCADE
    )
    """)


def create_database():

    connection = get_connection()
    cursor = connection.cursor()

    # Create searches table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS searches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        search_term TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Check whether results table already exists
    cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    AND name = 'results'
    """)

    results_table_exists = cursor.fetchone()

    if results_table_exists is None:

        create_results_table(cursor)

    else:

        # Check whether results already has a foreign key
        cursor.execute("""
        PRAGMA foreign_key_list(results)
        """)

        foreign_keys = cursor.fetchall()

        has_search_foreign_key = False

        for foreign_key in foreign_keys:

            table_name = foreign_key[2]
            from_column = foreign_key[3]
            to_column = foreign_key[4]

            if (
                table_name == "searches"
                and from_column == "search_id"
                and to_column == "id"
            ):
                has_search_foreign_key = True

        # Migrate old results table if needed
        if not has_search_foreign_key:

            cursor.execute("""
            ALTER TABLE results
            RENAME TO results_old
            """)

            create_results_table(cursor)

            cursor.execute("""
            INSERT INTO results (
                id,
                search_id,
                title,
                link,
                snippet,
                created_at
            )
            SELECT
                results_old.id,
                results_old.search_id,
                results_old.title,
                results_old.link,
                results_old.snippet,
                results_old.created_at
            FROM results_old
            INNER JOIN searches
                ON searches.id = results_old.search_id
            """)

            cursor.execute("""
            DROP TABLE results_old
            """)

    connection.commit()
    connection.close()


def save_search(search_term):

    connection = get_connection()
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

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO results (
            search_id,
            title,
            link,
            snippet
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            search_id,
            title,
            link,
            snippet
        )
    )

    connection.commit()
    connection.close()


def get_search_history():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT
        id,
        search_term,
        created_at
    FROM searches
    ORDER BY id DESC
    """)

    searches = cursor.fetchall()

    connection.close()

    return searches


def get_results_for_search(search_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            title,
            link,
            snippet
        FROM results
        WHERE search_id = ?
        ORDER BY id ASC
        """,
        (search_id,)
    )

    results = cursor.fetchall()

    connection.close()

    return results


if __name__ == "__main__":

    create_database()

    print("Database ready.")