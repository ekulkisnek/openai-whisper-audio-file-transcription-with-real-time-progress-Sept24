
# Audio Transcription Service

A Flask-based web application that transcribes audio and video files using OpenAI's Whisper model.

## Features

- Upload audio/video files for transcription
- Real-time progress tracking
- Chunk-based processing for large files
- Browser-based interface
- Copy transcription to clipboard
- Persistent storage of transcripts
- Reverse chronological logging

## Prerequisites

- Python 3.11+
- Flask
- OpenAI Whisper
- PyDub
- SQLAlchemy
- PostgreSQL

## Installation

The project uses Poetry for dependency management. All dependencies are automatically installed when running on Replit.

Required packages:
```
flask
flask-sqlalchemy
psycopg2-binary
whisper
pydub
openai-whisper
```

## Configuration

1. Set up your database URL in the environment variables:
   ```
   DATABASE_URL=your_database_url
   ```

2. The application will create necessary folders:
   - `uploads/` - For storing uploaded files
   - `transcripts/` - For storing generated transcripts

## Usage

1. Access the web interface
2. Upload an audio/video file using the file input
3. The file will be processed in chunks of 15 seconds
4. Monitor real-time progress on the progress bar
5. Once complete, the transcript will be displayed
6. Use the "Copy to Clipboard" button to copy the transcript

## API Endpoints

- `GET /` - Main page with upload form
- `POST /` - Upload endpoint for files
- `GET /progress/<job_id>` - Check transcription progress

## Technical Details

- Uses Whisper's base model for transcription
- Implements chunk-based processing for memory efficiency
- Stores progress data in memory during transcription
- Uses threading for background processing
- Implements custom reverse logging for better debugging

## File Structure

```
├── app.py            # Main application logic
├── main.py           # Entry point
├── models.py         # Database models
├── static/           # Static files
│   └── js/          
│       └── main.js   # Frontend JavaScript
└── templates/        
    └── index.html    # Main HTML template
```

## Error Handling

- Custom logging with ReverseFileHandler
- Error states tracked in transcription_data
- Client-side error display
- Automatic cleanup of temporary files

## License

This project is open source and available under the MIT License.
