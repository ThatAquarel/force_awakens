import io
import time
import importlib.resources

import numpy as np
from flask import Flask, request, jsonify, send_file

import force_awakens.web


def server_process(vec_queue):
    app = Flask(__name__)

    @app.route('/')
    def serve_index():
        index_bytes = importlib.resources.read_binary(force_awakens.web, "index.html")
        index_bytes = io.BytesIO(index_bytes)
        return send_file(index_bytes, download_name="index.html")

    @app.route('/data', methods=['POST'])
    def collect_data():
        nonlocal vec_queue

        data = request.json
        x = data.get("x")
        y = data.get("y")
        z = data.get("z")

        if x is None or y is None or z is None:
            return jsonify({"error": "Invalid data"}), 400

        x = float(x)
        y = float(y)
        z = float(z)

        vec_queue.put([x, y, z])
        
        return jsonify({"message": "Data saved successfully"}), 201

    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    app.run(host='0.0.0.0', port=8080)
