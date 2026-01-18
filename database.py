from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime

# 1. Tworzymy bazę i silnik
engine = create_engine("sqlite:///logopedia.db", echo=False)  # echo=True pokazuje SQL w konsoli
Base = declarative_base()

# 2. Model dziecka
class Child(Base):
    __tablename__ = "children"
    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    birth_date = Column(Date, nullable=False)
    gender = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

    examinations = relationship("Examination", back_populates="child")

    def __repr__(self):
        return (
            f"<Child id={self.id} name={self.first_name} {self.last_name} "
            f"birth_date={self.birth_date} gender={self.gender}>"
        )

# 3. Model badania
class Examination(Base):
    __tablename__ = "examinations"
    id = Column(Integer, primary_key=True)
    child_id = Column(Integer, ForeignKey("children.id"))
    date = Column(Date, default=datetime.date.today)
    exam_type = Column(String, nullable=True)
    conclusions = Column(Text, nullable=True)

    child = relationship("Child", back_populates="examinations")
    answers = relationship("Answer", back_populates="examination")

# 4. Model odpowiedzi
class Answer(Base):
    __tablename__ = "answers"
    id = Column(Integer, primary_key=True)
    examination_id = Column(Integer, ForeignKey("examinations.id"))
    question_id = Column(String, nullable=False)  # np. "r_articulation"
    answer_value = Column(String, nullable=False)

    examination = relationship("Examination", back_populates="answers")

# 5. Tworzymy tabele w bazie
Base.metadata.create_all(engine)

# 6. Tworzymy sesję do pracy z bazą
Session = sessionmaker(bind=engine)
session = Session()

# Functions for main.py compatibility
def connect_to_db():
    """Create and return a database connection"""
    import sqlite3
    return sqlite3.connect("logopedia.db")

def init_db():
    """Initialize the database by creating all tables"""
    Base.metadata.create_all(engine)

def get_all_children(session):
    """
    Zwraca listę wszystkich dzieci z bazy danych
    """
    return session.query(Child).all()

children = get_all_children(session)
if __name__ == "__main__":
    if not children:
        print("Brak dzieci w bazie.")
    else:
        print("Lista dzieci:")
        for child in children:
            print(
                f"{child.id} - {child.first_name} {child.last_name} "
                f"{child.birth_date} Płeć: {child.gender} Notatki: {child.notes}"
            )
