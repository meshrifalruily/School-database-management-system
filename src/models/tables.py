from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, Table
from sqlalchemy.ext.declarative import declarative_base  # Base class for declarative models
from sqlalchemy.orm import relationship, sessionmaker

database_url = "sqlite:///./db/school.db"
engine = create_engine(database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Association table for teachers <-> students many-to-many
teacher_student_association = Table(
    'teacher_student',
    Base.metadata,
    Column('teacher_id', Integer, ForeignKey('teachers.id'), primary_key=True),
    Column('student_id', Integer, ForeignKey('students.id'),primary_key=True )
)

# Association table for teachers <-> courses many-to-many
teacher_course_association = Table(
    'teacher_course',
    Base.metadata,
    Column('teacher_id', Integer, ForeignKey('teachers.id'), primary_key=True),
    Column('course_id', Integer, ForeignKey('courses.id'), primary_key=True)
)

# Association table for students <-> courses many-to-many
student_course_association = Table(
    'student_course',
    Base.metadata,
    Column('student_id', Integer, ForeignKey('students.id'), primary_key=True),
    Column('course_id', Integer, ForeignKey('courses.id'), )
)

class Courses(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    teachers = relationship("Teachers", secondary=teacher_course_association, back_populates="courses")
    students = relationship("Students", secondary=student_course_association, back_populates="courses")

class Teachers(Base):
    __tablename__ = 'teachers'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    subject = Column(String, index=True)
    # teacher <-> student
    students = relationship("Students", secondary=teacher_student_association, back_populates="teachers")
    # teacher <-> course
    courses = relationship("Courses", secondary=teacher_course_association, back_populates="teachers")

class Students(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    grade = Column(String, index=True)
    # student <-> teacher
    teachers = relationship("Teachers", secondary=teacher_student_association, back_populates="students")
    # student <-> course
    courses = relationship("Courses", secondary=student_course_association, back_populates="students")

# Create all tables in the database
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



