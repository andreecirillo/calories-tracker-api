from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import models
import uvicorn
import typer
from pydantic import BaseModel
from typing import List, Optional as Opt
from ai_agents.gemini import get_diet_insights

app = FastAPI(title="Calories Tracker API")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class FoodEntryBase(BaseModel):
    user_id: int
    username: str
    food_name: str
    calories: int
    date_time: datetime


class FoodEntryCreate(FoodEntryBase):
    pass


class FoodEntry(FoodEntryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "user_id": 1,
                "username": "test_user",
                "food_name": "Sample Food",
                "calories": 500,
                "date_time": "2025-05-20T12:00:00",
            }
        }


# API Endpoints
@app.post(
    "/api/entries/",
    response_model=FoodEntry,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Food entry created successfully"},
        400: {"description": "Invalid input data"},
    },
)
def create_entry(entry: FoodEntryCreate, db: Session = Depends(models.get_db)):
    """Create a new food entry.

    Parameters:
    - **entry**: Food entry data including user_id, username, food_name, calories, and date_time

    Returns:
    - **FoodEntry**: The created food entry with ID and timestamps

    Raises:
    - **HTTPException(400)**: If the entry data is invalid or there's a database error
    """
    # Validate calories (must be positive)
    if entry.calories <= 0:
        raise HTTPException(
            status_code=400, detail="Calories must be a positive number"
        )

    try:
        db_entry = models.FoodEntry(**entry.dict())
        db.add(db_entry)
        db.commit()
        db.refresh(db_entry)
        return db_entry
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")


@app.get(
    "/api/diet-analysis/{username}",
    # Removido: response_model=FoodEntry
    responses={
        200: {"description": "Username found"},
        404: {"description": "Username not found"},
    },
)
def diet_analysis(
    username: str, db: Session = Depends(models.get_db)
) -> Dict[str, Any]:
    """Analyze a user's diet and return insights.

    Parameters:
    - **username**: The username to analyze

    Returns:
    - **Dict[str, Any]**: A dictionary containing the analysis results

    Raises:
    - **HTTPException(404)**: If the username is not found
    - **HTTPException(400)**: If there's a database error
    """
    try:
        entries = (
            db.query(models.FoodEntry)
            .filter(models.FoodEntry.username == username)
            .all()
        )
        if not entries:
            raise HTTPException(status_code=404, detail="Username not found")

        food_data = [
            {"food_name": entry.food_name, "calories": entry.calories}
            for entry in entries
        ]

        insights = get_diet_insights(food_data)

        return {"username": username, "entries": food_data, "insights": insights}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")


@app.get(
    "/api/entries/",
    response_model=List[FoodEntry],
    responses={200: {"description": "List of food entries"}},
)
def read_entries(
    skip: int = 0,
    limit: int = 100,
    username: Optional[str] = None,
    db: Session = Depends(models.get_db),
):
    """Get a list of food entries with optional filtering.

    Parameters:
    - **skip**: Number of entries to skip (pagination)
    - **limit**: Maximum number of entries to return
    - **username**: Optional filter by username

    Returns:
    - **List[FoodEntry]**: List of food entries

    Raises:
    - **HTTPException(400)**: If there's a database error
    - **HTTPException(422)**: If the query parameters are invalid
    """
    # Validate query parameters
    if skip < 0:
        raise HTTPException(status_code=422, detail="Skip value cannot be negative")
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=422, detail="Limit must be between 1 and 100")

    try:
        query = db.query(models.FoodEntry)
        if username:
            query = query.filter(models.FoodEntry.username == username)
        return query.offset(skip).limit(limit).all()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")


@app.get(
    "/api/entries/{entry_id}",
    response_model=FoodEntry,
    responses={
        200: {"description": "Food entry found"},
        404: {"description": "Food entry not found"},
    },
)
def read_entry(entry_id: int, db: Session = Depends(models.get_db)):
    """Get a specific food entry by ID.

    Parameters:
    - **entry_id**: ID of the food entry to retrieve

    Returns:
    - **FoodEntry**: The requested food entry

    Raises:
    - **HTTPException(404)**: If the entry is not found
    - **HTTPException(400)**: If there's a database error
    - **HTTPException(422)**: If the entry_id is invalid
    """
    # Validate entry_id
    if entry_id <= 0:
        raise HTTPException(
            status_code=422, detail="Entry ID must be a positive integer"
        )

    try:
        db_entry = (
            db.query(models.FoodEntry).filter(models.FoodEntry.id == entry_id).first()
        )
        if db_entry is None:
            raise HTTPException(status_code=404, detail="Entry not found")
        return db_entry
    except HTTPException:
        # Re-raise HTTPExceptions (like 404)
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")


# CLI Application
cli = typer.Typer()


@cli.command()
def add_entry(
    user_id: int = typer.Option(..., help="User ID (must be positive)"),
    username: str = typer.Option(..., help="Username"),
    food_name: str = typer.Option(..., help="Name of the food item"),
    calories: int = typer.Option(..., help="Calories"),
    date_time: str = typer.Option(
        None, help="Date and time in ISO format (YYYY-MM-DDTHH:MM:SS)"
    ),
):
    """Add a new food entry via CLI"""
    # Manual validation
    if user_id <= 0:
        typer.echo("Error: User ID must be positive", err=True)
        return
    if len(username) < 3:
        typer.echo("Error: Username must be at least 3 characters", err=True)
        return
    if len(food_name) < 2:
        typer.echo("Error: Food name must be at least 2 characters", err=True)
        return
    if calories <= 0 or calories > 5000:
        typer.echo("Error: Calories must be between 1 and 5000", err=True)
        return

    db = next(models.get_db())
    try:
        # Validate date_time format if provided
        if date_time:
            try:
                parsed_date = datetime.fromisoformat(date_time)
            except ValueError:
                typer.echo(
                    f"Error: Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)",
                    err=True,
                )
                return
        else:
            parsed_date = datetime.now()

        entry_data = {
            "user_id": user_id,
            "username": username,
            "food_name": food_name,
            "calories": calories,
            "date_time": parsed_date,
        }
        db_entry = models.FoodEntry(**entry_data)
        db.add(db_entry)
        db.commit()
        db.refresh(db_entry)
        typer.echo(f"Added entry: {db_entry.id}")
    except Exception as e:
        typer.echo(f"Error: {str(e)}", err=True)
        db.rollback()
    finally:
        db.close()


@cli.command()
def list_entries(
    username: str = typer.Option(None, help="Filter entries by username"),
    limit: int = typer.Option(10, help="Maximum number of entries to show"),
    sort_by: str = typer.Option(
        "date_time", help="Sort by field (id, username, calories, date_time)"
    ),
    descending: bool = typer.Option(True, help="Sort in descending order"),
):
    """List food entries with filtering and sorting options"""
    # Manual validation
    if limit < 1 or limit > 100:
        typer.echo("Error: Limit must be between 1 and 100", err=True)
        return

    valid_sort_fields = ["id", "username", "calories", "date_time"]
    if sort_by not in valid_sort_fields:
        typer.echo(
            f"Error: sort_by must be one of {', '.join(valid_sort_fields)}", err=True
        )
        return

    db = next(models.get_db())
    try:
        query = db.query(models.FoodEntry)

        # Apply username filter if provided
        if username:
            query = query.filter(models.FoodEntry.username == username)

        # Apply sorting
        if sort_by == "id":
            query = query.order_by(
                models.FoodEntry.id.desc() if descending else models.FoodEntry.id
            )
        elif sort_by == "username":
            query = query.order_by(
                models.FoodEntry.username.desc()
                if descending
                else models.FoodEntry.username
            )
        elif sort_by == "calories":
            query = query.order_by(
                models.FoodEntry.calories.desc()
                if descending
                else models.FoodEntry.calories
            )
        else:  # default to date_time
            query = query.order_by(
                models.FoodEntry.date_time.desc()
                if descending
                else models.FoodEntry.date_time
            )

        entries = query.limit(limit).all()

        if not entries:
            typer.echo("No entries found.")
            return

        # Print header
        typer.echo(f"Found {len(entries)} entries:")
        typer.echo("-" * 70)

        # Print entries
        for entry in entries:
            typer.echo(
                f"{entry.id}: {entry.username} - {entry.food_name} ({entry.calories} kcal) - {entry.date_time}"
            )

        typer.echo("-" * 70)
    finally:
        db.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # If arguments are provided, run CLI
        cli()
    else:
        # Otherwise, print help
        print("Use 'python main.py --help' for CLI commands")
        print("Use 'python run.py' to start the API server")
