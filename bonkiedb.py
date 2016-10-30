from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Float, Integer, DateTime, text, func, ForeignKey, UniqueConstraint
from sqlalchemy.orm import sessionmaker, aliased, relationship

engine = create_engine("sqlite:///:memory:")

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    code = Column(Integer, nullable=False)  # telegram code
    first_name = Column(String)
    last_name = Column(String)
    start_datetime = Column(DateTime, nullable=False)

    #workouts = relationship("Workout", order_by=Workout.id, back_populates="users")

    def __repr__(self):
        return "<User(name={}, code={}, start_datetime={})>".format(self.name, self.code, self.start_datetime)


class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # link
    datetime = Column(DateTime)
    comment = Column(String)

    user = relationship("User", back_populates="workouts")
    #sets = relationship("Set", order_by=Set.id, back_populates="workouts")

    def __repr__(self):
        return "<Workout(id={}, user_id={}, datetime={})>"\
            .format(self.id, self.user_id, self.datetime)


class Set(Base):
    __tablename__ = "sets"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    workout_id = Column(Integer, ForeignKey("workouts.id"), nullable=False)
    type_set = Column(String, nullable=False)  # {'set', 'superset'}
    comment = Column(String)

    user = relationship("User", back_populates="sets")
    workout = relationship("Workout", back_populates="sets")
    #exercises = relationship("Exercise", order_by=Exercise.id, back_populates="sets")

    def __repr__(self):
        return "<Set(id={}, user_id={}, type_set={})>"\
            .format(self.id, self.user_id, self.type_set)


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    set_id = Column(Integer, ForeignKey("sets.id"), nullable=False)
    name = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    reps = Column(Integer, nullable=False)
    speed = Column(String)
    comment = Column(String)

    user = relationship("User", back_populates="exercises")
    set = relationship("Set", back_populates="exercises")

    def __repr__(self):
        return "<Exercise(id={}, user_id={}, set_id={}, name={})>"\
            .format(self.id, self.user_id, self.set_id, self.name)


class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True)
    datetime = Column(DateTime)
    level = Column(Integer)
    message = Column(String)

    def __repr__(self):
        return "<Log(id={}, datetime={}, level={}, message={})>"\
            .format(self.id, self.datetime, self.level, self.message)


class Error(Base):
    __tablename__ = "errors"

    id = Column(Integer, primary_key=True)
    log_id = Column(Integer, ForeignKey("logs.id"))
    message = Column(String)

    log = relationship("Log", back_populates="error")

    def __repr__(self):
        return "<Error(id={}, log_id={}, message={})>"\
            .format(self.id, self.log_id, self.message)


User.workouts = relationship("Workout", order_by=Workout.id, back_populates="user")
User.sets = relationship("Set", order_by=Set.id, back_populates="user")
User.exercises = relationship("Exercise", order_by=Exercise.id, back_populates="user")
Workout.sets = relationship("Set", order_by=Set.id, back_populates="workout")
Set.exercises = relationship("Exercise", order_by=Exercise.id, back_populates="set")
Log.error = relationship("Error", back_populates="log")


if __name__ == "__main__":
    from datetime import datetime

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    session = Session()

    Timo = User(name="Timo Lesterhuis", code=123456, start_datetime=datetime.now())

