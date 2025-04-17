"""
High School Management System API

A FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School, using MongoDB Atlas for storage.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
import pymongo
from pymongo import MongoClient
import json

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# MongoDB connection - local development instance
MONGODB_URI = "mongodb://localhost:27017/highschool"
client = MongoClient(MONGODB_URI)
db = client.highschool
activities_collection = db.activities

# Initial data to populate the database
initial_activities = {
    "Chess Club": {
        "name": "Chess Club",
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "name": "Programming Class",
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "name": "Gym Class",
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Basketball Club": {
        "name": "Basketball Club",
        "description": "Play basketball and compete in local tournaments",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": []
    },
    "Soccer Club": {
        "name": "Soccer Club",
        "description": "Practice soccer skills and play friendly matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": []
    },
    "Painting Club": {
        "name": "Painting Club",
        "description": "Explore different painting techniques and create artwork",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": []
    },
    "Drama Club": {
        "name": "Drama Club",
        "description": "Participate in theatrical productions and improve acting skills",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": []
    },
    "Debate Club": {
        "name": "Debate Club",
        "description": "Engage in debates and improve public speaking skills",
        "schedule": "Mondays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": []
    },
    "Science Club": {
        "name": "Science Club",
        "description": "Conduct science experiments and learn about scientific concepts",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": []
    }
}


@app.on_event("startup")
async def startup_db_client():
    """Initialize the database with activities if empty"""
    try:
        # Create a unique index on the name field
        activities_collection.create_index("name", unique=True)

        # Only insert if collection is empty
        if activities_collection.count_documents({}) == 0:
            # Insert all activities
            for activity in initial_activities.values():
                activities_collection.insert_one(activity)
    except Exception as e:
        print(f"Error initializing database: {e}")


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    """Get all activities"""
    activities_list = activities_collection.find({}, {'_id': 0})
    # Convert to dictionary with activity name as key
    return {activity['name']: activity for activity in activities_list}


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Find the activity
    activity = activities_collection.find_one({"name": activity_name})

    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Already signed up")

    # Add student using atomic update
    result = activities_collection.update_one(
        {"name": activity_name},
        {"$push": {"participants": email}}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to sign up")

    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Find the activity
    activity = activities_collection.find_one({"name": activity_name})

    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(
            status_code=404, detail="Participant not found in this activity")

    # Remove student using atomic update
    result = activities_collection.update_one(
        {"name": activity_name},
        {"$pull": {"participants": email}}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to unregister")

    return {"message": f"Unregistered {email} from {activity_name}"}
