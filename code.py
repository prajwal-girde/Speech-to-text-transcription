from flask import Flask, request, jsonify
import speech_recognition as sr
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'wav', 'aiff', 'flac', 'mp3', 'm4a'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/transcribe', methods=['POST'])
def transcribe_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file part'}), 400
    file = request.files['audio']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(filepath) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)
            os.remove(filepath)  # Clean up uploaded file
            return jsonify({'transcription': text})
        except sr.UnknownValueError:
            os.remove(filepath)
            return jsonify({'error': 'Could not understand audio'}), 422
        except sr.RequestError as e:
            os.remove(filepath)
            return jsonify({'error': f'Could not request results from speech recognition service; {e}'}), 503
    else:
        return jsonify({'error': 'Unsupported file type'}), 415

if __name__ == '__main__':
    app.run(debug=True)

