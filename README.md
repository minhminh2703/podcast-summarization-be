# 🎧 Podcast Summarization Backend

## 🚀 Getting Started

To start the project from scratch:

1. Install all required libraries:
    ```bash
    pip install -r requirements.txt
    ```
2. Create the database schema and apply the latest migrations:
    ```bash
    alembic upgrade head
    ```
3. Run the server:
    ```bash
    python main.py
    ```

## ⚙️ Prerequisites

-   Python version 3.9
-   SQLite (or another database configured via `SQLALCHEMY_DATABASE_URL`)

## API

-   Check out [PostmanAPI.json](./PostmanAPI.json) file to get to know about API parameters.

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
-   `podcast_id`: Foreign key linking to podcasts.id
