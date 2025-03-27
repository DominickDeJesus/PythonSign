from flask import Flask, request, jsonify, send_from_directory
import os
import json

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
settings_file = os.path.join(BASE_DIR, "settings.json")
themes_dir = os.path.join(BASE_DIR, "themes")

os.makedirs(themes_dir, exist_ok=True)

def save_settings(data):
    with open(settings_file, "w") as f:
        json.dump(data, f, indent=4)

def load_settings():
    try:
        with open(settings_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"mode": "logo", "theme": None, "duration": 2}

@app.route('/set_theme', methods=['POST'])
def set_theme():
    data = request.json
    theme = data.get("theme")
    settings = load_settings()
    settings["theme"] = theme
    save_settings(settings)
    return jsonify({"status": "success", "theme": theme})

@app.route('/set_duration', methods=['POST'])
def set_duration():
    data = request.json
    duration = data.get("duration", 2)
    settings = load_settings()
    settings["duration"] = duration
    save_settings(settings)
    return jsonify({"status": "success", "duration": duration})

@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'file' not in request.files or 'theme' not in request.form:
        return jsonify({"error": "Missing file or theme"}), 400

    file = request.files['file']
    theme = request.form['theme']
    theme_path = os.path.join(themes_dir, theme)
    os.makedirs(theme_path, exist_ok=True)

    file_path = os.path.join(theme_path, file.filename)
    file.save(file_path)

    return jsonify({"status": "success", "filename": file.filename, "theme": theme})

@app.route('/get_themes', methods=['GET'])
def get_themes():
    themes = [d for d in os.listdir(themes_dir) if os.path.isdir(os.path.join(themes_dir, d))]
    return jsonify({"themes": themes})

@app.route('/')
def index():
    return send_from_directory(BASE_DIR, "static/index.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
