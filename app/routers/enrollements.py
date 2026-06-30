from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/enrollments", tags=["Enrollments"])

@router.post("", response_model=schemas.EnrollmentResponse, status_code=status.HTTP_201_CREATED)
def enroll_user(payload: schemas.EnrollmentCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == payload.user_id).first()
    course = db.query(models.Course).filter(models.Course.id == payload.course_id).first()
    if not user or not course:
        raise HTTPException(status_code=404, detail="User or Course not found")

    existing = db.query(models.Enrollment).filter(
        models.Enrollment.user_id == payload.user_id,
        models.Enrollment.course_id == payload.course_id,
        models.Enrollment.status == "active"
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="User is already actively enrolled in this course")

    new_enrollment = models.Enrollment(user_id=payload.user_id, course_id=payload.course_id)
    db.add(new_enrollment)
    db.commit()
    db.refresh(new_enrollment)
    return new_enrollment

@router.post("/{enrollment_id}/complete-lesson")
def complete_lesson(enrollment_id: int, db: Session = Depends(get_db)):
    enrollment = db.query(models.Enrollment).filter(models.Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    if enrollment.status == "completed":
        raise HTTPException(status_code=400, detail="Course already completed")

    course = db.query(models.Course).filter(models.Course.id == enrollment.course_id).first()
    enrollment.completed_lessons_count += 1

    if enrollment.completed_lessons_count >= course.total_lessons:
        enrollment.status = "completed"
        enrollment.completed_at = datetime.utcnow()
        
        unlocked_achievements = []
        
        # Trigger 1: "Fast Starter"
        prior_completions = db.query(models.Enrollment).filter(
            models.Enrollment.user_id == enrollment.user_id,
            models.Enrollment.status == "completed",
            models.Enrollment.id != enrollment.id
        ).count()
        
        if prior_completions == 0:
            exists = db.query(models.Achievement).filter_by(user_id=enrollment.user_id, title="Fast Starter").first()
            if not exists:
                db.add(models.Achievement(user_id=enrollment.user_id, title="Fast Starter"))
                unlocked_achievements.append("Fast Starter")

        # Trigger 2: "Deep Diver"
        if course.total_lessons >= 10:
            exists = db.query(models.Achievement).filter_by(user_id=enrollment.user_id, title="Deep Diver").first()
            if not exists:
                db.add(models.Achievement(user_id=enrollment.user_id, title="Deep Diver"))
                unlocked_achievements.append("Deep Diver")
        
        db.commit()
        return {
            "message": "Course completed successfully!", 
            "current_lessons": enrollment.completed_lessons_count,
            "achievements_unlocked": unlocked_achievements
        }

    db.commit()
    return {"message": "Lesson tracked successfully", "current_lessons": enrollment.completed_lessons_count}