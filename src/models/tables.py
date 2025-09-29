from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, Table
from sqlalchemy.ext.declarative import declarative_base # Base class for declarative models - converts python codes to sql codes
from sqlalchemy.orm import relationship, sessionmaker

database_url = "sqlite:///./db/school.db"
engine = create_engine(database_url) # Example for SQLite
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base() # Base class for declarative models - converts python codes to sql codes 

teacher_student_association = Table(
    'teacher_student', 
    Base.metadata, 
    Column('teacher_id', Integer, ForeignKey('teachers.id')), 
    Column('student_id', Integer, ForeignKey('students.id')))

class Teachers(Base):
    __tablename__ = 'teachers'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    subject = Column(String, index=True)
    students = relationship("Students", secondary=teacher_student_association, back_populates="teachers")

class Students(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    grade = Column(String, index=True)
    teachers = relationship("Teachers", secondary=teacher_student_association, back_populates="students")

# Create all tables in the database
Base.metadata.create_all(bind=engine)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



