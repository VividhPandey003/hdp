import sqlite3
import json

def fetch_all_predictions():
    """Fetch all stored predictions from prediction.db."""
    try:
        with sqlite3.connect("predictions.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM predictions")  # Fetch all data
            rows = cursor.fetchall()

            if not rows:
                print("No data found in predictions table.")
                return []

            # Extract column names
            cursor.execute("PRAGMA table_info(predictions)")
            columns = [col[1] for col in cursor.fetchall()]

            # Convert data to a readable format
            predictions = [dict(zip(columns, row)) for row in rows]

            return predictions

    except sqlite3.Error as e:
        print("Database error:", e)
        return []

# Fetch and display predictions
all_predictions = fetch_all_predictions()
print(json.dumps(all_predictions, indent=4))  # Pretty print the data
