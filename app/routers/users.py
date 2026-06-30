from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/{user_id}/dashboard", response_model=schemas.DashboardResponse)
def get_dashboard(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    active_courses_progress = []
    active_enrollments = db.query(models.Enrollment).filter(
        models.Enrollment.user_id == user_id, 
        models.Enrollment.status == "active"
    ).all()

    for enroll in active_enrollments:
        course = db.query(models.Course).filter(models.Course.id == enroll.course_id).first()
        percentage = round((enroll.completed_lessons_count / course.total_lessons) * 100, 2)
        
        active_courses_progress.append(
            schemas.ActiveCourseProgress(
                course_id=course.id,
                title=course.title,
                completed_lessons_count=enroll.completed_lessons_count,
                total_lessons=course.total_lessons,
                progress_percentage=percentage
            )
        )

    achievements = db.query(models.Achievement).filter(models.Achievement.user_id == user_id).all()

    return schemas.DashboardResponse(
        user_id=user.id,
        name=user.name,
        email=user.email,
        active_courses=active_courses_progress,
        achievements=achievements
    )