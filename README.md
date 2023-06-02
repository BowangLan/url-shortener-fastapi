# URL Shortener FastAPI

A simple URL shortener implemented using FastAPI and SQLAlchemy. 

Based on a Real Python tutorial: https://realpython.com/build-a-python-url-shortener-with-fastapi/

## Set Up

Create a `.env` file with the following variable:

```
ENV_NAME="Development"
BASE_URL="http://127.0.0.1:8000"
DB_URL="sqlite:///./shortener.db"
```

Create a virtual environment and instal the dependencies:

```
python -m venv venv
pip install -r requirements.txt
```

Start the server:

```
uvcorn shortener_app.main:app --reload --port 8000
```