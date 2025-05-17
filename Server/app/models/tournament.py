from ..extensions import db
from datetime import datetime
from .device import DeviceType

class Tournament(db.Model):
    __tablename__ = 'tournaments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    game_type = db.Column(db.Enum(DeviceType), nullable=False)
    date = db.Column(db.DateTime, nullable=False)

    participants = db.relationship("TournamentParticipant", back_populates="tournament")


class TournamentParticipant(db.Model):
    __tablename__ = 'tournament_participants'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'))
    score = db.Column(db.Integer, nullable=True)

    user = db.relationship("User", back_populates="tournament_participations")
    tournament = db.relationship("Tournament", back_populates="participants")
