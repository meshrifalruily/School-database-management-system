from fastapi import FastAPI, Depends, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from models.tables import get_db, Teachers, Students, Courses

app = FastAPI()

templates = Jinja2Templates(directory="templates")

# Home route - main endpoint
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})    

# shows the add teacher page
@app.get("/add-teacher")
def add_teacher(request: Request):

    return templates.TemplateResponse("add_teacher.html", {"request": request}) 


# Recive form data to add a new teacher
@app.post("/add-teacher")
def add_teacher(name: str = Form(...), subject: str = Form(...), db=Depends(get_db)):
    new_teacher = Teachers(name=name, subject=subject)
    db.add(new_teacher)
    db.commit()
    db.refresh(new_teacher)
    return {"message": "Teacher added successfully", "teacher": {"id": new_teacher.id, "name": new_teacher.name, "subject": new_teacher.subject}}

# shows the add student page
@app.get("/add-student")
def add_student(request: Request):
    return templates.TemplateResponse("add_student.html", {"request": request})

# Recive form data to add a new student
@app.post("/add-student")
def add_student(request: Request, student_name: str = Form(...), grade: str = Form(...), db=Depends(get_db)):
    new_student = Students(name=student_name, grade=grade)
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return templates.TemplateResponse("success.html", {"request": request})

@app.get("/add-course")
def add_course_page(request: Request):
    return templates.TemplateResponse("add_course.html", {"request": request})

@app.post("/add-course")
def add_course(request: Request,course_name: str = Form(...), db=Depends(get_db)):
    """Create a new course."""
    new_course = Courses(name=course_name)
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return templates.TemplateResponse("success.html", {"request": request})


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
    """Render the assign page with available teachers, students and courses."""
    teachers = db.query(Teachers).all()
    students = db.query(Students).all()
    courses = db.query(Courses).all()
    return templates.TemplateResponse("assign.html", {"request": request, "teachers": teachers, "students": students, "courses": courses})

@app.post("/assign-teacher")
def assign_teacher(student_id: int, teacher_id: int, db=Depends(get_db)):
    student = db.query(Students).filter(Students.id == student_id).first()
    teacher = db.query(Teachers).filter(Teachers.id == teacher_id).first()
    if not student or not teacher:
        return {"error": "Student or Teacher not found"}
    student.teachers.append(teacher)
    db.commit()
    return {"message": f"Teacher {teacher.name} assigned to Student {student.name} successfully"}

@app.post("/assign-course-to-teacher")
def assign_course_to_teacher(course_id: int = Form(...), teacher_id: int = Form(...), db=Depends(get_db)):
    """Assign a course to a teacher."""
    course = db.query(Courses).filter(Courses.id == course_id).first()
    teacher = db.query(Teachers).filter(Teachers.id == teacher_id).first()
    if not course or not teacher:
        return {"error": "Course or Teacher not found"}
    teacher.courses.append(course)
    db.commit()
    return {"message": f"Course {course.name} assigned to Teacher {teacher.name} successfully"}

@app.post("/assign-course-to-student")
def assign_course_to_student(course_id: int = Form(...), student_id: int = Form(...), db=Depends(get_db)):
    """Assign a course to a student."""
    course = db.query(Courses).filter(Courses.id == course_id).first()
    student = db.query(Students).filter(Students.id == student_id).first()
    if not course or not student:
        return {"error": "Course or Student not found"}
    student.courses.append(course)
    db.commit()
    return {"message": f"Course {course.name} assigned to Student {student.name} successfully"}

@app.get("/search")
def teacher_search(request: Request, teacher_id: int = None, db=Depends(get_db)):
    """Render a search form or show teacher details when `teacher_id` query param is provided."""
    if teacher_id is None:
        return templates.TemplateResponse("search.html", {"request": request})

    teacher = db.query(Teachers).filter(Teachers.id == teacher_id).first()
    if not teacher:
        return templates.TemplateResponse("search.html", {"request": request, "error": "Teacher not found"})

    students = [{"id": s.id, "name": s.name, "grade": s.grade} for s in teacher.students]
    courses = [{"id": c.id, "name": c.name} for c in teacher.courses]
    teacher_dict = {"id": teacher.id, "name": teacher.name, "subject": teacher.subject}
    return templates.TemplateResponse("search.html", {"request": request, "teacher": teacher_dict, "students": students, "courses": courses})

@app.get("/search/{teacher_id}")
def get_teacher_by_id(request: Request, teacher_id: int, db=Depends(get_db)):
    """Return teacher details and their students/courses for a given teacher_id as an HTML page."""
    teacher = db.query(Teachers).filter(Teachers.id == teacher_id).first()
    if not teacher:
        return templates.TemplateResponse("search.html", {"request": request, "error": "Teacher not found"})
    students = [{"id": s.id, "name": s.name, "grade": s.grade} for s in teacher.students]
    courses = [{"id": c.id, "name": c.name} for c in teacher.courses]
    teacher_dict = {"id": teacher.id, "name": teacher.name, "subject": teacher.subject}
    return templates.TemplateResponse("search.html", {"request": request, "teacher": teacher_dict, "students": students, "courses": courses})

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

@app.get("/student")
def student_search(request: Request, student_id: int = None, db=Depends(get_db)):
    """Render a search form or show student details when `student_id` query param is provided."""
    if student_id is None:
        return templates.TemplateResponse("search.html", {"request": request})

    student = db.query(Students).filter(Students.id == student_id).first()
    if not student:
        return templates.TemplateResponse("search.html", {"request": request, "error": "Student not found"})

    student_teachers = [{"id": t.id, "name": t.name, "subject": t.subject} for t in student.teachers]
    student_courses = [{"id": c.id, "name": c.name} for c in student.courses]
    student_dict = {"id": student.id, "name": student.name, "grade": student.grade}
    return templates.TemplateResponse("search.html", {"request": request, "student": student_dict, "student_teachers": student_teachers, "student_courses": student_courses})

@app.get("/teacher")
def teacher_alias(request: Request, teacher_id: int = None, db=Depends(get_db)):
    """Compatibility wrapper for /teacher -> uses the same logic as /search."""
    return teacher_search(request, teacher_id, db)

@app.get("/teacher/{teacher_id}")
def teacher_by_id_alias(request: Request, teacher_id: int, db=Depends(get_db)):
    """Compatibility wrapper for /teacher/{teacher_id} -> uses the same logic as /search/{teacher_id}."""
    return get_teacher_by_id(request, teacher_id, db)