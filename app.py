from flask import Flask, request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import os
import logging
import uuid
import datetime
import whisper
from pydub import AudioSegment
import threading
import time

# ------------------------
# Logging Configuration
# ------------------------
class ReverseFileHandler(logging.FileHandler):
    def emit(self, record):
        with open(self.baseFilename, 'r+') as file:
            old_content = file.read()
            file.seek(0, 0)
            file.write(self.format(record) + '\n' + old_content)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger()
reverse_handler = ReverseFileHandler('error_log.txt')
logger.addHandler(reverse_handler)

# ------------------------
# Constants and Global Variables
# ------------------------
MODEL = whisper.load_model("base")
UPLOAD_FOLDER = 'uploads'
TRANSCRIPTS_FOLDER = 'transcripts'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TRANSCRIPTS_FOLDER, exist_ok=True)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# create the app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['MAX_CONTENT_LENGTH'] = None  # Remove upload limits
db.init_app(app)

# Store transcription progress and results in memory
transcription_data = {}

# ------------------------
# Helper Functions
# ------------------------

def save_transcript_as_txt(transcript, filename):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(TRANSCRIPTS_FOLDER, f"{timestamp}_{filename}.txt")

    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(transcript)
        logging.debug(f"Transcript saved to {file_path}.")
        return file_path
    except Exception as e:
        logging.error(f"Error saving transcript: {e}")
        return None

def split_audio(file_path, chunk_length_ms=15000):
    audio = AudioSegment.from_file(file_path)
    chunks = [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]
    return chunks

def transcribe_file(file_path, filename, job_id):
    try:
        audio_chunks = split_audio(file_path)
        total_chunks = len(audio_chunks)
        transcript = ""
        start_time = time.time()

        for i, chunk in enumerate(audio_chunks):
            chunk_file = f"{file_path}_chunk_{i}.wav"
            chunk.export(chunk_file, format="wav")

            # Transcribe the chunk
            result = MODEL.transcribe(chunk_file)
            chunk_transcript = result.get("text", "")
            transcript += chunk_transcript + "\n"

            elapsed_time = time.time() - start_time
            remaining_time = elapsed_time * (total_chunks - i - 1) / (i + 1)

            logging.debug(f"Chunk {i+1}/{total_chunks} transcribed. Transcript so far: {chunk_transcript}")

            # Update progress in the global dictionary
            transcription_data[job_id] = {
                'progress': (i + 1) / total_chunks * 100,
                'transcript': transcript,
                'total_chunks': total_chunks,
                'processed_chunks': i + 1,
                'elapsed_time': elapsed_time,
                'remaining_time': remaining_time,
                'complete': False
            }

        # Save the full transcript to a file
        save_transcript_as_txt(transcript, filename)

        # Mark transcription as complete
        transcription_data[job_id]['complete'] = True

    except Exception as e:
        logging.error(f"Error during transcription: {e}")
        transcription_data[job_id]['error'] = str(e)

# ------------------------
# Routes
# ------------------------

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            job_id = str(uuid.uuid4())
            filename = f"{job_id}_{file.filename}"
            file_path = os.path.join(UPLOAD_FOLDER, filename)

            with open(file_path, 'wb') as f:
                while chunk := file.stream.read(4096):
                    f.write(chunk)

            logging.debug(f"File uploaded to {file_path}. Beginning transcription.")

            # Start transcription in a background thread
            threading.Thread(target=transcribe_file, args=(file_path, filename, job_id)).start()

            return jsonify({'job_id': job_id}), 202

    return render_template('index.html')

@app.route('/progress/<job_id>')
def progress(job_id):
    return jsonify(transcription_data.get(job_id, {'error': 'Job not found'}))

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
