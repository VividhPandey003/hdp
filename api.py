from flask import Flask, request, jsonify
import datetime
import json
import sqlite3
from app import predict_room_price  # ✅ Import function from app.py
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def init_db():
    """Initialize the database and create the table if it doesn't exist."""
    with sqlite3.connect("predictions.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                room_type TEXT NOT NULL,
                optimized_price INTEGER NOT NULL,
                avgOfSimilarHotelsPricing REAL NOT NULL,
                current_price INTEGER NOT NULL,
                selected_ancillaries TEXT NOT NULL,
                short_description TEXT NOT NULL,
                description TEXT NOT NULL,
                logic TEXT NOT NULL
            )
        ''')
        conn.commit()

@app.route('/predict_price', methods=['GET'])
def get_price_prediction():
    """Handles API requests to predict room price with detailed logging."""
    
    print("\n🔵 Received API Request for /predict_price")

    # ✅ Step 1: Get query parameters
    date = request.args.get('date')
    room_type = request.args.get('room_type')

    print(f"🟡 Extracted Parameters: date={date}, room_type={room_type}")

    # ✅ Step 2: Validate inputs
    if not date or not room_type:
        print("❌ Missing required parameters: date or room_type")
        return jsonify({"error": "Missing required parameters: date and room_type"}), 400
    
    # ✅ Step 3: Validate date format
    try:
        datetime.datetime.strptime(date, "%Y-%m-%d")
        print(f"✅ Date format is valid: {date}")
    except ValueError:
        print("❌ Invalid date format. Expected YYYY-MM-DD")
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    # ✅ Step 4: Call `predict_room_price()`
    print("🟡 Calling `predict_room_price()` with provided parameters...")
    result = predict_room_price(date, room_type)

    # ✅ Step 5: Debugging - Print raw result
    print("\n🔹 Raw result from `predict_room_price()`: ", result, "\n")

    # ✅ Step 6: Check if `result` is already a dictionary
    if isinstance(result, dict):
        result_json = result
    else:
        # ✅ Step 7: If `result` is a string, attempt to parse JSON
        try:
            print("🟡 Attempting to parse JSON string...")
            result_json = json.loads(result)
            print("✅ JSON parsing successful!")
        except json.JSONDecodeError as e:
            print("❌ JSON decode error:", e)
            return jsonify({"error": "Invalid response format from predict_room_price"}), 500

    # ✅ Step 8: Store result in database
    try:
        with sqlite3.connect("predictions.db") as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO predictions (date, room_type, optimized_price, avgOfSimilarHotelsPricing, current_price, 
                                        selected_ancillaries, short_description, description, logic)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                date,
                room_type,
                result_json.get("optimized_price", 0),
                result_json.get("avgOfSimilarHotelsPricing", 0.0),
                result_json.get("current_price", 0),
                json.dumps(result_json.get("selected_ancillaries", [])),  # Store as JSON string
                result_json.get("short_description", ""),
                json.dumps(result_json.get("description", [])),
                result_json.get("logic", "")
            ))
            conn.commit()
        print("✅ Prediction stored in database successfully!")
    except sqlite3.Error as e:
        print("❌ Database error while inserting:", e)
        return jsonify({"error": "Database error while inserting"}), 500

    return jsonify(result_json)

@app.route('/get_prediction', methods=['GET'])
def get_stored_prediction():
    """Fetches stored prediction from the database by date and room type."""
    print("\n🔵 Received API Request for /get_prediction")
    
    # ✅ Step 1: Get query parameters
    date = request.args.get('date')
    room_type = request.args.get('room_type')
    print(f"🟡 Extracted Parameters: date={date}, room_type={room_type}")
    
    # ✅ Step 2: Validate inputs
    if not date or not room_type:
        print("❌ Missing required parameters: date or room_type")
        return jsonify({"error": "Missing required parameters: date and room_type"}), 400
    
    # ✅ Step 3: Fetch from database
    try:
        with sqlite3.connect("predictions.db") as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT optimized_price, avgOfSimilarHotelsPricing, current_price, selected_ancillaries, 
                       short_description, description, logic 
                FROM predictions 
                WHERE date = ? AND room_type = ?
            ''', (date, room_type))
            row = cursor.fetchone()
        
        if row:
            print("✅ Prediction found in database. Returning result...")
            return jsonify({
                "date": date,
                "room_type": room_type,
                "optimized_price": row[0],
                "avgOfSimilarHotelsPricing": row[1],
                "current_price": row[2],
                "selected_ancillaries": json.loads(row[3]),  # Convert back from JSON string
                "short_description": row[4],
                "description": json.loads(row[5]),
                "logic": row[6]
            })
        else:
            print("❌ No prediction found for the given date and room type.")
            return jsonify({"error": "No prediction found"}), 404
    except sqlite3.Error as e:
        print("❌ Database error:", e)
        return jsonify({"error": "Database error"}), 500

@app.route('/delete_prediction', methods=['DELETE', 'GET'])
def delete_prediction():
    """Deletes a specific prediction entry from the database based on date and room type."""
    print("\n🔵 Received API Request for /delete_prediction")
    
    # ✅ Step 1: Get query parameters
    date = request.args.get('date')
    room_type = request.args.get('room_type')
    print(f"🟡 Extracted Parameters: date={date}, room_type={room_type}")
    
    # ✅ Step 2: Validate inputs
    if not date or not room_type:
        print("❌ Missing required parameters: date or room_type")
        return jsonify({"error": "Missing required parameters: date and room_type"}), 400
    
    try:
        with sqlite3.connect("predictions.db") as conn:
            cursor = conn.cursor()
            
            # ✅ Step 3: Check if the entry exists
            cursor.execute("SELECT * FROM predictions WHERE date = ? AND room_type = ?", (date, room_type))
            entry = cursor.fetchone()

            if not entry:
                print("❌ No matching prediction found.")
                return jsonify({"error": "No matching prediction found"}), 404

            # ✅ Step 4: Execute DELETE statement
            cursor.execute("DELETE FROM predictions WHERE date = ? AND room_type = ?", (date, room_type))
            conn.commit()
            print("✅ Prediction deleted successfully!")

            return jsonify({"message": "Prediction deleted successfully."}), 200

    except sqlite3.Error as e:
        print("❌ Database error:", e)
        return jsonify({"error": "Database error while deleting"}), 500


if __name__ == '__main__':
    print("\n🚀 Starting Flask API Server...")
    init_db()
    app.run(debug=True)
