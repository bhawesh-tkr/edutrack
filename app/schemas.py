from pydantic import BaseModel
from typing import List
from datetime import datetime

class EnrollmentCreate(BaseModel):
    user_id: int
    course_id: int

class EnrollmentResponse(BaseModel):
    id: int
    user_id: int
    course_id: int
    completed_lessons_count: int
    status: str
    class Config:
        from_attributes = True

class ActiveCourseProgress(BaseModel):
    course_id: int
    title: str
    completed_lessons_count: int
    total_lessons: int
    progress_percentage: float

class AchievementSchema(BaseModel):
    title: str
    unlocked_at: datetime
    class Config:
        from_attributes = True

class DashboardResponse(BaseModel):
    user_id: int
    name: str
    email: str
    active_courses: List[ActiveCourseProgress]
    achievements: List[AchievementSchema]

class LeaderboardEntry(BaseModel):
    user_id: int
    name: str
    total_lessons_completed: int