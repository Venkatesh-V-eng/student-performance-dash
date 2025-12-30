from fastapi import FastAPI, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker, Session
import uvicorn

# 1. DATABASE CONFIGURATION (SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///./students.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. DATABASE MODEL (The Schema)
class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    math = Column(Float)
    physics = Column(Float)
    cs = Column(Float)
    average = Column(Float)
    grade = Column(String)

# Create tables
Base.metadata.create_all(bind=engine)

# 3. APP INITIALIZATION
app = FastAPI(title="Student Dashboard")
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 4. GRADING ALGORITHM
def calculate_grade(avg):
    if avg >= 90: return 'A+'
    elif avg >= 80: return 'A'
    elif avg >= 70: return 'B'
    elif avg >= 60: return 'C'
    else: return 'F'

# 5. ROUTES
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    students = db.query(Student).all()
    return templates.TemplateResponse("index.html", {"request": request, "students": students})

@app.post("/add")
def add_student(
    name: str = Form(...),
    math: float = Form(...),
    physics: float = Form(...),
    cs: float = Form(...),
    db: Session = Depends(get_db)
):
    # Business Logic
    avg = (math + physics + cs) / 3
    grade = calculate_grade(avg)
    
    # Save to DB
    new_student = Student(name=name, math=math, physics=physics, cs=cs, average=avg, grade=grade)
    db.add(new_student)
    db.commit()
    
    return RedirectResponse(url="/", status_code=303)

# 6. RUNNER (For Debugging)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)