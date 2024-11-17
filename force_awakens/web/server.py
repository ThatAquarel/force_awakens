import io
import importlib.resources

from flask import Flask, request, jsonify, send_file

import force_awakens.web


def server_process(vec_queue, port):
    # new flask server to host the accelerometer data
    # receiving, and sending to the graphic display

    app = Flask(__name__)

    @app.route("/")
    def serve_index():
        # serve index.html to new clients that request /
        index_bytes = importlib.resources.read_binary(force_awakens.web, "index.html")
        index_bytes = io.BytesIO(index_bytes)
        return send_file(index_bytes, download_name="index.html")

    @app.route("/data", methods=["POST"])
    def collect_data():
        # received new data, parse xyz acceleration into
        # floats, and push new vector into multiprocessing
        # queue for rendering

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

        print(f"RECEIVED vec: {x} {y} {z}")
        vec_queue.put([x, y, z])
        print("put queue")

        return jsonify({"message": "Data saved successfully"}), 201

    # silence flask logs
    import logging

    log = logging.getLogger("werkzeug")
    log.setLevel(logging.ERROR)

    # host run webserver on port
    app.run(host="0.0.0.0", port=port)
