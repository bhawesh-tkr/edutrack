from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/leaderboard", response_model=List[schemas.LeaderboardEntry])
def get_leaderboard(db: Session = Depends(get_db)):
    leaderboard = db.query(
        models.User.id.label("user_id"),
        models.User.name.label("name"),
        func.sum(models.Enrollment.completed_lessons_count).label("total_lessons_completed")
    ).join(models.Enrollment, models.User.id == models.Enrollment.user_id)\
     .group_by(models.User.id)\
     .order_by(func.sum(models.Enrollment.completed_lessons_count).desc())\
     .limit(5)\
     .all()

    return leaderboard
