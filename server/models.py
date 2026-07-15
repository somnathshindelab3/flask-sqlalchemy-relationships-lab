import sys

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

# Ensure both package and top-level imports share the same model module.
sys.modules.setdefault("models", sys.modules[__name__])
sys.modules.setdefault("server.models", sys.modules[__name__])

# Association table for the many-to-many relationship between sessions and speakers.
session_speakers = db.Table(
    "session_speakers",
    db.Column("session_id", db.Integer, db.ForeignKey("sessions.id"), primary_key=True),
    db.Column("speaker_id", db.Integer, db.ForeignKey("speakers.id"), primary_key=True),
)


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)

    # An event has many sessions; deleting an event removes its sessions.
    sessions = db.relationship(
        "Session",
        back_populates="event",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Event {self.id}, {self.name}, {self.location}>"


class Session(db.Model):
    __tablename__ = "sessions"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    start_time = db.Column(db.DateTime)
    event_id = db.Column(
        db.Integer,
        db.ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
    )

    # A session belongs to one event.
    event = db.relationship("Event", back_populates="sessions")

    # A session has many speakers through the association table.
    speakers = db.relationship(
        "Speaker",
        secondary=session_speakers,
        back_populates="sessions",
    )

    def __repr__(self):
        return f"<Session {self.id}, {self.title}, {self.start_time}>"


class Speaker(db.Model):
    __tablename__ = "speakers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    # A speaker has one bio; deleting a speaker removes its bio.
    bio = db.relationship(
        "Bio",
        back_populates="speaker",
        uselist=False,
        cascade="all, delete-orphan",
    )

    # A speaker has many sessions through the association table.
    sessions = db.relationship(
        "Session",
        secondary=session_speakers,
        back_populates="speakers",
    )

    def __repr__(self):
        return f"<Speaker {self.id}, {self.name}>"


class Bio(db.Model):
    __tablename__ = "bios"

    id = db.Column(db.Integer, primary_key=True)
    bio_text = db.Column(db.Text, nullable=False)
    speaker_id = db.Column(
        db.Integer,
        db.ForeignKey("speakers.id", ondelete="CASCADE"),
        nullable=False,
    )

    # A bio belongs to one speaker.
    speaker = db.relationship("Speaker", back_populates="bio")

    def __repr__(self):
        return f"<Bio {self.id}, {self.bio_text}>"
