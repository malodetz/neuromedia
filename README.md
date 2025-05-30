# neuromedia
Brainrot broadcasting company

# Core

This module acts as the central controller of the system. It coordinates the flow of news data from the scraper to the machine learning (ML) component, and finally stores processed results in the database.

## Workflow

1. Input from Scraper. The scraper sends news entries in the form:
```json
{ "text": "news content", "source": "example.com" }
```
2. Interaction with ML Component.
    * Core forwards the `text` and `source` to the ML component asynchronously.
    * ML component responds with a unique `news_id`.
    * Core polls the ML component for status of this `news_id`:
        * `processing` – still in progress.
        * `drop` – duplicate or irrelevant.
        * `ok` – processed successfully, with:
        ```json
        { "rewritten_text": "...", "tags": ["tag1", "tag2"] }
        ```
3. Storing in Database. If processing is successful, Core saves the `id`, `rewritten_text`, and `tags` to the database.

## How to run tests

Run `pytest` command. Tests now mock every other module.

# Streamlit News Feed UI

The project includes a web-based news feed interface built with Streamlit that displays processed news articles with their AI-generated tags.

## Features

* **Real-time News Feed**: Displays all processed news articles from the database
* **Tag Filtering**: Filter news by specific tags using the sidebar
* **Auto-refresh**: Automatically updates every 30 seconds to show new news
* **Statistics Dashboard**: Shows total news count, filtered results, and unique tags
* **Responsive Design**: Clean, modern interface with colored tag pills

## Running the UI

1. Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

2. Ensure the PostgreSQL database is running and configured properly

3. Run the Streamlit app:
```bash
python run_streamlit.py
```

Or directly:
```bash
streamlit run streamlit_app.py
```

4. Open your browser and navigate to `http://localhost:8501`

## UI Components

* **News Items**: Each news article is displayed in a card format with:
  - News ID for reference
  - Processed/rewritten text from the ML component
  - Color-coded tags below the text
* **Sidebar Controls**:
  - Auto-refresh toggle
  - Manual refresh button
  - Tag filtering options
* **Statistics**: Real-time metrics showing total news, filtered results, and unique tags

The UI automatically connects to the same PostgreSQL database used by the core system and displays news as it gets processed.

# Database

## PostgreStorage class

* On creation accepts:
    * `dbname` - name of a PostgreSQL database.
    * `user` - name of a PostgreSQL user.
    * `password` - password for the user.
    * `host` - host of a running PostgreSQL instance. `localhost` by default.
    * `port` - port of a running PostgreSQL instance. `5433` by default.
* `store` stores record via `record_id`, `text` and `tags`.
* `get` gets record by `record_id`.
* `get_all` gets all records ordered by ID (newest first).
* `get_by_tag` gets records filtered by specific tag.
* `delete` deletes record by `record_id`.
* `close` closes connection to the database.

## How to run tests

1. Start a PostgreSQL instance. More on how to do it in the main [README](../README.md).
2. Make shure that all requirenments from `requirenments.txt` are satisfied.
3. Run `pytest` command.

## Connecting to PostgreSQL

First, make sure that `PostgreSQL` is installed. If it's not, you can install it with the following command:
```bash
sudo apt install postgresql postgresql-contrib
```

To start the container, run the following command from the root of the repository:
```bash
docker-compose up
```

After that, you can connect to the database using the command:
```bash
psql -U pguser -h localhost -p 5433 -d mydb
```

The default password for the user is `secret`.
