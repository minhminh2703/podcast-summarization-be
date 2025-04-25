# 🎧 Podcast Summarization Backend

## 🚀 Getting Started

To start the project from scratch:

1. Install all required libraries:
    ```bash
    pip install -r requirements.txt
    ```
2. Rename the `example_env.txt` file to `.env` and fill in the required configuration.
3. Create the database schema and apply the latest migrations:
    ```bash
    alembic upgrade head
    ```
4. Run the server:
    ```bash
    python main.py
    ```

## ⚙️ Prerequisites

-   You must have [FFmpeg](https://ffmpeg.org/download.html) installed and accessible via the command line (`ffmpeg`, `ffprobe`).

    -   Macos using this command: `brew install ffmpeg`
    -   Linux using this command: `sudo apt install ffmpeg`
    -   Window download directly from: https://ffmpeg.org/download.html

-   Python version 3.9
-   SQLite (or another database configured via `SQLALCHEMY_DATABASE_URL`)

## 🎧 Project Description

This project provides a backend server for **Podcast Summarization**, which allows you to input a podcast link (either from RSS or YouTube), transcribe it using Whisper, and generate a concise summary using GPT-4o-mini.

### 🔗 Supported Podcast Sources

-   **RSS Feeds**  
    Only RSS links from the following sources are currently supported:

    -   [Listen Notes](https://www.listennotes.com/)
    -   [Castos](https://castos.com/tools/find-podcast-rss-feed/)

-   **YouTube**  
    Any **public YouTube** link can be used as input.

### ⚙️ Tech Stack

-   **[FastAPI](https://fastapi.tiangolo.com/)** — High-performance web framework for building APIs
-   **[Whisper](https://github.com/openai/whisper)** — Automatic speech recognition (ASR) model used for podcast transcription
-   **GPT-4o-mini** — Lightweight GPT model for generating podcast summaries

### 🚀 How It Works

1. Submit a podcast link (RSS or YouTube)
2. The server downloads and transcribes the audio using Whisper
3. The transcript is segmented by topic and summarized using GPT-4o-mini
4. The final output includes:
    - Section-wise headings and summaries
    - A complete episode summary

## API

Check out [PostmanAPI.json](./PostmanAPI.json), import it to Postman discover how API works.

## 📦 Database Migration (with Alembic)

This project uses **Alembic** for managing database schema migrations. Make sure you've installed Alembic (usually via `pip install -r requirements.txt`) and initialized the migration folder (`alembic/`).

### 🔼 Upgrade to Latest Version

Apply all available migrations to bring the database schema up-to-date:

```bash
alembic upgrade head
```

### 🔽 Downgrade to Previous Version

Rollback the most recent migration:

```bash
alembic downgrade -1
```

Or downgrade to a specific version:

```bash
alembic downgrade <revision_id>
```

### 🔄 Reset to Base (Initial) Version

If you want to reset the schema to the very first version:

```bash
alembic downgrade base
```

## 🧱 Database Structure

This project uses Alembic for schema migration and version control, with the following main tables:

### 🔐 users

Stores user information:

-   `userid`: UUID (Primary key)
-   `password`: Hashed password
-   `email`: Email address (Unique)
-   `created_at, updated_at`: Timestamps for record creation and update
-   `profile_picture`: User profile picture (Binary)

### 🎙️ podcasts

Stores uploaded podcasts:

-   `id`: UUID (Primary key)
-   `title`: Podcast title
-   `userid`: Foreign key linking to users.userid
-   `thumbnail_url`: URL of the podcast thumbnail
-   `summarized_content`: Summarized content (optional)
-   `target_language`: Target language for the summary
-   `audio_path`: File path to the podcast audio
-   `duration`: Podcast duration (in seconds)

### 📝 heading_section

Stores summarized sections (headings) of podcasts:

-   `id`: UUID (Primary key)
-   `header`: Section header (e.g., "Heading 1")
-   `title`: Section title
-   `content`: Summarized text content
-   `start, end`: Start and end timestamps (in seconds) for this section
-   `podcast_id`: Foreign key linking to podcasts id
