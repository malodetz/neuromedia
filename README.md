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
