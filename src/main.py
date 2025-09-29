from fastapi import FastAPI, Depends, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from models.tables import get_db, Teachers, Students
app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})    

@app.post("/add-teacher")
def add_teacher(name: str = Form(...), subject: str = Form(...), db=Depends(get_db)):
    new_teacher = Teachers(name=name, subject=subject)
    db.add(new_teacher)
    db.commit()
    db.refresh(new_teacher)
    return {"message": "Teacher added successfully", "teacher": {"id": new_teacher.id, "name": new_teacher.name, "subject": new_teacher.subject}}

@app.post("/add-student")
def add_student(name: str = Form(...), grade: str = Form(...), db=Depends(get_db)):
    new_student = Students(name=name, grade=grade)
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return {"message": "Student added successfully", "student": {"id": new_student.id, "name": new_student.name, "grade": new_student.grade}}

@app.post("/assign-student")
def assign_student(request: Request, teacher_id: int = Form(...), student_id: int = Form(...), db=Depends(get_db)):
    """Assign a student to a teacher using form data and render the assign page with a message."""
    teacher = db.query(Teachers).filter(Teachers.id == teacher_id).first()
    student = db.query(Students).filter(Students.id == student_id).first()
    if not teacher or not student:
        teachers = db.query(Teachers).all()
        students = db.query(Students).all()
        return templates.TemplateResponse("assign.html", {"request": request, "teachers": teachers, "students": students, "error": "Teacher or Student not found"})
    teacher.students.append(student)
    db.commit()
    teachers = db.query(Teachers).all()
    students = db.query(Students).all()
    return templates.TemplateResponse("assign.html", {"request": request, "teachers": teachers, "students": students, "message": f"Student {student.name} assigned to Teacher {teacher.name} successfully"})

@app.get("/assign")
def assign_page(request: Request, db=Depends(get_db)):
    """Render the assign page with available teachers and students."""
    teachers = db.query(Teachers).all()
    students = db.query(Students).all()
    return templates.TemplateResponse("assign.html", {"request": request, "teachers": teachers, "students": students})

@app.post("/assign-teacher")
def assign_teacher(student_id: int, teacher_id: int, db=Depends(get_db)):
    student = db.query(Students).filter(Students.id == student_id).first()
    teacher = db.query(Teachers).filter(Teachers.id == teacher_id).first()
    if not student or not teacher:
        return {"error": "Student or Teacher not found"}
    student.teachers.append(teacher)
    db.commit()
    return {"message": f"Teacher {teacher.name} assigned to Student {student.name} successfully"}

@app.get("/teacher")
def teacher_search(request: Request, teacher_id: int = None, db=Depends(get_db)):
    """Render a search form or show teacher details when `teacher_id` query param is provided."""
    if teacher_id is None:
        return templates.TemplateResponse("teacher_search.html", {"request": request})

    teacher = db.query(Teachers).filter(Teachers.id == teacher_id).first()
    if not teacher:
        return templates.TemplateResponse("teacher_search.html", {"request": request, "error": "Teacher not found"})

    students = [{"id": s.id, "name": s.name, "grade": s.grade} for s in teacher.students]
    teacher_dict = {"id": teacher.id, "name": teacher.name, "subject": teacher.subject}
    return templates.TemplateResponse("teacher.html", {"request": request, "teacher": teacher_dict, "students": students})

@app.get("/teacher/{teacher_id}")
def get_teacher_by_id(request: Request, teacher_id: int, db=Depends(get_db)):
    """Return teacher details and their students for a given teacher_id as an HTML page."""
    teacher = db.query(Teachers).filter(Teachers.id == teacher_id).first()
    if not teacher:
        return templates.TemplateResponse("teacher_search.html", {"request": request, "error": "Teacher not found"})
    students = [{"id": s.id, "name": s.name, "grade": s.grade} for s in teacher.students]
    teacher_dict = {"id": teacher.id, "name": teacher.name, "subject": teacher.subject}
    return templates.TemplateResponse("teacher.html", {"request": request, "teacher": teacher_dict, "students": students})

@app.post("/remove-teacher")
def remove_teacher(request: Request, teacher_id: int = Form(...), db=Depends(get_db)):
    """Remove a teacher by id (detach associations first) and render the assign page with a message."""
    teacher = db.query(Teachers).filter(Teachers.id == teacher_id).first()
    teachers = db.query(Teachers).all()
    students = db.query(Students).all()
    if not teacher:
        return templates.TemplateResponse("assign.html", {"request": request, "teachers": teachers, "students": students, "error": "Teacher not found"})

    # detach associations then delete
    teacher.students = []
    db.delete(teacher)
    db.commit()

    teachers = db.query(Teachers).all()
    students = db.query(Students).all()
    return templates.TemplateResponse("assign.html", {"request": request, "teachers": teachers, "students": students, "message": f"Teacher {teacher.name} removed successfully"})

@app.get("/remove-teacher")
def remove_teacher_get():
    """Redirect GET requests for remove-teacher back to the assign page (deletes remain POST-only)."""
    return RedirectResponse(url="/assign")

@app.post("/remove-student")
def remove_student(request: Request, student_id: int = Form(...), db=Depends(get_db)):
    """Remove a student by id (detach associations first) and render the assign page with a message."""
    student = db.query(Students).filter(Students.id == student_id).first()
    teachers = db.query(Teachers).all()
    students = db.query(Students).all()
    if not student:
        return templates.TemplateResponse("assign.html", {"request": request, "teachers": teachers, "students": students, "error": "Student not found"})

    # detach associations then delete
    student.teachers = []
    db.delete(student)
    db.commit()

    teachers = db.query(Teachers).all()
    students = db.query(Students).all()
    return templates.TemplateResponse("assign.html", {"request": request, "teachers": teachers, "students": students, "message": f"Student {student.name} removed successfully"})

@app.get("/remove-student")
def remove_student_get():
    """Redirect GET requests for remove-student back to the assign page (deletes remain POST-only)."""
    return RedirectResponse(url="/assign")