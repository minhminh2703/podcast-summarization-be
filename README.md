# Podcast Summarizer

A web application that transcribes podcast audio files and generates AI-powered summaries.

## Features

- Upload podcast audio files (MP3, WAV, M4A, MP4)
- Transcribe audio using OpenAI's Whisper model
- Summarize content using GPT models through LangChain
- Multiple summary types (concise, detailed, bullet points)
- Adjustable summary length
- Download both transcripts and summaries

## Architecture

- **Frontend**: Streamlit web application
- **Backend**: FastAPI REST API
- **Transcription**: OpenAI Whisper speech-to-text model
- **Summarization**: GPT models via LangChain

## Prerequisites

- Python 3.8+
- OpenAI API key

## Installation

1. Clone this repository:
```bash
git clone https://github.com/minhminh2703/podcast-summarization-be.git
cd podcast-summarizer
```

2. Set up the backend:
```bash
cd backend
pip install -r requirements.txt
```

3. Set up the frontend:
```bash
cd frontend
pip install -r requirements.txt
```

4. Set your OpenAI API key:
```bash
export OPENAI_API_KEY=your_api_key_here
```

## Running the Application

1. Start the backend server:
```bash
cd backend
uvicorn app:app --reload
```

2. Start the frontend application (in a separate terminal):
```bash
cd frontend
streamlit run app.py
```

3. Open your browser and navigate to http://localhost:8501

## Configuration

- The backend API URL can be configured by setting the `BACKEND_API_URL` environment variable
- The Whisper model size can be changed in `backend/models/whisper_model.py` (options: tiny, base, small, medium, large)
- OpenAI model selection can be modified in `backend/models/summarizer.py`

## License

MIT

## Acknowledgements

- [OpenAI Whisper](https://github.com/openai/whisper)
- [LangChain](https://github.com/langchain-ai/langchain)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Streamlit](https://streamlit.io/)