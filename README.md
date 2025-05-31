# Neuromedia
Brainrot Broadcasting Company

## Running the Neuromedia

1. Make sure all dependencies are installed (we recommend using [UV](https://docs.astral.sh/uv/)):
```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

2. Ensure the PostgreSQL database is running and configured properly

3. Run the backend:
```bash
uv run neuromedia.py
```

4. Run the Streamlit app:
```bash
streamlit run streamlit_app.py
```

5. Open your browser and navigate to `http://localhost:8501`

## Connecting to PostgreSQL

First, make sure that `PostgreSQL` is installed. If it's not, you can install it with the following command:
```bash
sudo apt install postgresql postgresql-contrib
```

To start the container, run the following command from the root of the repository:
```bash
docker compose up
```

After that, you can connect to the database using the command:
```bash
psql -U pguser -h localhost -p 5433 -d mydb
```

The default password for the user is `secret`.

## How to run tests

Run `PYTHONPATH=. pytest` command. Tests now mock every other module.
