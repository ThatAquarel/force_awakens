from flask import Flask, request, jsonify, send_from_directory
import numpy as np
import os
import time

app = Flask(__name__)

# Define a buffer to store accelerometer data
BUFFER_SIZE = 1000  # Maximum number of records to store
data_buffer = np.zeros((BUFFER_SIZE, 5))  # Columns: timestamp, x, y, z, user_id
buffer_index = 0

# Serve the index.html file
@app.route('/')
def serve_index():
    return send_from_directory(os.path.dirname(__file__), 'index.html')

# Collect accelerometer data
@app.route('/data', methods=['POST'])
def collect_data():
    print("post collect")

    global buffer_index, data_buffer

    # Parse JSON payload
    data = request.json
    user_id = data.get("user_id", 0)  # Default to 0 if user_id is not provided
    x = data.get("x")
    y = data.get("y")
    z = data.get("z")

    if x is None or y is None or z is None:
        return jsonify({"error": "Invalid data"}), 400

    # Store data in the buffer
    timestamp = float(time.time())
    x = float(x)
    y = float(y)
    z = float(z)
    user_id = float(x)

    data_buffer[buffer_index % BUFFER_SIZE] = [timestamp, x, y, z, user_id]
    
    print(data)

    buffer_index += 1

    return jsonify({"message": "Data saved successfully"}), 201

# Retrieve data from the buffer
@app.route('/data', methods=['GET'])
def get_data():
    global buffer_index, data_buffer

    # Return data currently in the buffer
    valid_data = data_buffer[:min(buffer_index, BUFFER_SIZE)]  # Only valid entries
    return jsonify(valid_data.tolist())

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
