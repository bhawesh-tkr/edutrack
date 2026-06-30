from fastapi import FastAPI
from app.database import engine, Base, SessionLocal
from app.models import Course, User

# Change direct package imports to explicit module imports
from app.routers.enrollements import router as enrollments_router
from app.routers.users import router as users_router
from app.routers.analytics import router as analytics_router

app = FastAPI(title="EduTrack Micro-Learning API")

@app.on_event("startup")
def startup_event():
    # Build database tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    # Auto-seed basic data if Courses table is completely empty
    if db.query(Course).count() == 0:
        sample_courses = [
            Course(title="Python Basics", description="Learn Python programming", total_lessons=5),
            Course(title="Intro to FastAPI", description="Build high-performance web APIs", total_lessons=3),
            Course(title="SQL 101", description="Master relational structures", total_lessons=10),
        ]
        sample_user = User(name="Alex Doe", email="alex@example.com")
        db.add_all(sample_courses)
        db.add(sample_user)
        db.commit()
    db.close()

# Include the explicitly imported routers
app.include_router(enrollments_router)
app.include_router(users_router)
app.include_router(analytics_router)