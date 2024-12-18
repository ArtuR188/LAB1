from flask import Flask, request, jsonify
from cryptography.fernet import Fernet
import json
import os

app = Flask(__name__)

KEY_FILE = "key.key"
NOTES_FILE = "notes.json"

if not os.path.exists(KEY_FILE):
    key = Fernet.generate_key()
    with open(KEY_FILE, 'wb') as f:
        f.write(key)
else:
    with open(KEY_FILE, 'rb') as f:
        key = f.read()

cipher = Fernet(key)

if not os.path.exists(NOTES_FILE):
    with open(NOTES_FILE, 'w') as f:
        json.dump({}, f)

@app.route('/add_note', methods=['POST'])
def add_note():
    data = request.json
    title = data.get('title')
    content = data.get('content')

    if not title or not content:
        return jsonify({'error': 'Both title and content are required'}), 400

    encrypted_content = cipher.encrypt(content.encode()).decode()

    with open(NOTES_FILE, 'r+') as f:
        notes = json.load(f)
        if title in notes:
            return jsonify({'error': 'Note with this title already exists'}), 400
        notes[title] = encrypted_content
        f.seek(0)
        json.dump(notes, f)
        f.truncate()

    return jsonify({'message': 'Note added successfully'}), 201

@app.route('/get_note/<title>', methods=['GET'])
def get_note(title):
    encrypt_code = request.args.get('code')

    if not encrypt_code:
        return jsonify({'error': 'Encryption code is required'}), 400

    if encrypt_code != key.decode():
        return jsonify({'error': 'Invalid encryption code'}), 403

    with open(NOTES_FILE, 'r') as f:
        notes = json.load(f)
        if title not in notes:
            return jsonify({'error': 'Note not found'}), 404

        decrypted_content = cipher.decrypt(notes[title].encode()).decode()

    return jsonify({'title': title, 'content': decrypted_content}), 200

if __name__ == '__main__':
    app.run(debug=True)
