from flask import Flask, request, jsonify
import datetime
import json  # ✅ Ensure JSON is imported
from app import predict_room_price  # ✅ Import function from app.py

app = Flask(__name__)

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
        print("✅ `predict_room_price()` returned a valid dictionary. Sending response...")
        return jsonify(result)

    # ✅ Step 7: If `result` is a string, attempt to parse JSON
    if isinstance(result, str):  
        try:
            print("🟡 Attempting to parse JSON string...")
            result_json = json.loads(result)  # ✅ Parse JSON string
            print("✅ JSON parsing successful! Returning response...")
            return jsonify(result_json)
        except json.JSONDecodeError as e:
            print("❌ JSON decode error:", e)
            return jsonify({"error": "Invalid response format from predict_room_price"}), 500

    # ✅ Step 8: Handle unknown cases (should never happen)
    print("❌ Unexpected response type from `predict_room_price()`. Returning error.")
    return jsonify({"error": "Unexpected response type"}), 500

if __name__ == '__main__':
    print("\n🚀 Starting Flask API Server...")
    app.run(debug=True)
