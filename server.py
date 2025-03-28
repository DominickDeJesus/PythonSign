from flask import Flask, request, jsonify, send_from_directory
import os
import json

app = Flask(__name__)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
settings_file = os.path.join(BASE_DIR, "settings.json")
themes_dir = os.path.join(BASE_DIR, "themes")

# Ensure themes folder exists
os.makedirs(themes_dir, exist_ok=True)

# Load/save helpers
def load_settings():
    try:
        with open(settings_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("[INFO] No settings.json found. Using defaults.")
        return {
            "mode": "all",
            "theme": None,
            "duration": 2,
            "sleep_enable": False,
            "sleep_range": {"start": "00:00", "end": "09:00"},
            "static_image": None
        }

def save_settings(data):
    with open(settings_file, "w") as f:
        json.dump(data, f, indent=4)
    print("[INFO] Settings saved:", data)

# ------------------------------
# Endpoints
# ------------------------------

@app.route('/get_settings', methods=['GET'])
def get_settings():
    settings = load_settings()
    print("[GET] /get_settings →", settings)
    return jsonify(settings)

@app.route('/set_settings', methods=['POST'])
def set_settings():
    data = request.json
    save_settings(data)
    print("[POST] /set_settings ←", data)
    return jsonify({"status": "success", "settings": data})

@app.route('/get_themes', methods=['GET'])
def get_themes():
    themes = [d for d in os.listdir(themes_dir) if os.path.isdir(os.path.join(themes_dir, d))]
    print("[GET] /get_themes →", themes)
    return jsonify({"themes": themes})

@app.route('/get_theme_images/<theme>', methods=['GET'])
def get_theme_images(theme):
    theme_path = os.path.join(themes_dir, theme)
    if not os.path.isdir(theme_path):
        print(f"[WARN] Theme '{theme}' not found")
        return jsonify({"images": []})

    images = [f for f in os.listdir(theme_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    print(f"[GET] /get_theme_images/{theme} → {len(images)} images")
    return jsonify({"images": images})

@app.route('/themes/<theme>/<filename>')
def serve_theme_image(theme, filename):
    file_path = os.path.join(themes_dir, theme, filename)
    if not os.path.exists(file_path):
        print(f"[404] File not found: {file_path}")
    else:
        print(f"[GET] Serving file: {file_path}")
    return send_from_directory(os.path.join(themes_dir, theme), filename)

@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        print("[ERROR] No file in request")
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    theme = request.form.get('theme') or request.form.get('new_theme')

    if not theme:
        print("[ERROR] No theme provided")
        return jsonify({"error": "No theme provided"}), 400

    theme_path = os.path.join(themes_dir, theme)
    os.makedirs(theme_path, exist_ok=True)

    file_path = os.path.join(theme_path, file.filename)
    file.save(file_path)

    print(f"[UPLOAD] File uploaded to theme '{theme}': {file.filename}")
    return jsonify({"status": "success", "filename": file.filename, "theme": theme})

@app.route('/')
def index():
    return send_from_directory(os.path.join(BASE_DIR, 'static'), 'index.html')

@app.route('/static/<path:filename>')
def serve_static_file(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'static'), filename)

# ------------------------------
# Launch the server
# ------------------------------

if __name__ == '__main__':
    print(f"🚀 Server running at http://0.0.0.0:5000/")
    print("📁 Themes folder:", themes_dir)
    app.run(host='0.0.0.0', port=5000)
