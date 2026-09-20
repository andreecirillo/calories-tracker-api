# Calories Tracker API

A FastAPI-based backend application for tracking food entries and calories with both REST API endpoints and CLI functionality.

## Technical Requirements

- **Python 3.11** (Required for compatibility with dependencies)
- pip package manager
- Docker and Docker Compose (optional, for containerized setup)

> **Note**: This application is optimized for Python 3.11 and may encounter compatibility issues with newer Python versions.

## Quick Setup with Docker

```bash
# Build and start the application
docker compose up --build

# Import sample data (in a separate terminal while the container is running)
docker compose exec app python import_data.py

# Run in detached mode (background)
docker compose up -d

# View logs when running in detached mode
docker compose logs -f

# Run tests in the Docker container
docker compose exec app python -m pytest

# Stop the application
docker compose down
```

The API will be available at http://localhost:8000

## Python Virtual Environment Setup (Alternative)

Alternatively, you can run the application directly with Python 3.11:

```bash
# Create a virtual environment with Python 3.11
python3.11 -m venv venv  # On Unix/macOS
# OR
py -3.11 -m venv venv    # On Windows

# Activate the virtual environment
source venv/bin/activate  # On Unix/macOS
# OR
.\venv\Scripts\activate   # On Windows

# Install dependencies
pip install -r requirements.txt

# Import sample data
python import_data.py

# Run the application
python run.py
```

The API will be available at http://localhost:8000 just like the Docker setup.

## Running Tests

```bash
# Run all tests
python -m pytest

# Run tests with verbose output
python -m pytest -v
```

## API Endpoints

- `GET /api/entries/` - List all food entries
- `GET /api/entries/?username=healthy_user` - Filter entries by username
- `GET /api/entries/{entry_id}` - Get a specific entry
- `POST /api/entries/` - Create a new entry

## CLI Commands

```bash
# List all food entries
python main.py list-entries

# List entries for a specific user
python main.py list-entries --username healthy_user

# Add a new entry
python main.py add-entry --user-id 4 --username "healthy_user" --food-name "Protein Shake" --calories 250
```

## Project Structure

- `main.py` - FastAPI application and CLI commands
- `models.py` - SQLAlchemy database models
- `import_data.py` - Script to import sample data
- `run.py` - Server startup script
- `calories.sql` - Sample data for import
- `ai_agents/gemini.py` - Specialized GEN AI model that will analyze the diet and generate valuable insights.

### API Documentation

- Interactive API docs (Swagger UI): `http://localhost:8000/docs`
- Alternative API docs (ReDoc): `http://localhost:8000/redoc`

### Using the CLI

The application includes a command-line interface for managing food entries:

1. Add a new food entry:
   ```bash
   python main.py add-entry --user-id 1 --username test_user --food-name "Apple" --calories 95
   ```

2. List recent food entries:
   ```bash
   python main.py list-entries --username test_user
   ```

## API Endpoints

### Create a Food Entry
- **POST** `/api/entries/`
  - Request body: JSON with `user_id`, `username`, `food_name`, `calories`, `date_time`
  - Example:
    ```json
    {
      "user_id": 1,
      "username": "test_user",
      "food_name": "Banana",
      "calories": 105,
      "date_time": "2025-05-20T12:00:00"
    }
    ```

### List Food Entries
- **GET** `/api/entries/`
  - Query parameters:
    - `skip`: Number of entries to skip (pagination)
    - `limit`: Maximum number of entries to return (default: 100)
    - `username`: Filter entries by username (optional)

### Get a Specific Food Entry
- **GET** `/api/entries/{entry_id}`
  - Returns details for a specific food entry by ID

## Development

### Database Schema

The application uses SQLite with the following schema:

```sql
CREATE TABLE food_entries_foodentry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    food_name TEXT,
    calories INTEGER,
    date_time DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Environment Variables

Create a `.env` file in the project root for environment-specific configurations:

```
DATABASE_URL=sqlite:///./calories.db
GOOGLE_API_KEY=YOUR_GOOGLE_AI_STUDIO_KEY_HERE
```

## Testing

To run the tests:

```bash
# Install test dependencies
pip install pytest httpx

# Run tests
pytest
```

## AI Integration Guide

### Setting Up Google AI Studio and Gemini API

1. **Create a Google AI Studio Account**
   - Visit [Google AI Studio](https://aistudio.google.com/welcome)
   - Sign in with your Google account (create one if needed)
   - Accept the terms of service and privacy policy

2. **Get Your Gemini API Key**
   - In the Google AI Studio dashboard, look for the "Get API key" on top right
   - Click on "Create API key"
   - A new API key will be generated for you
   - Copy and save this key in a secure location (you won't be able to see it again)

## License

This project is licensed under the MIT License.
