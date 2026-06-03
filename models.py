from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Goal(db.Model):
    __tablename__ = 'goals'
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), nullable=False)
    target     = db.Column(db.Float, nullable=False)
    saved      = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    deposits   = db.relationship('Deposit', backref='goal', cascade='all, delete-orphan')

    def to_dict(self):
        pct = min(self.saved / self.target, 1.0) if self.target > 0 else 0
        return {
            'id':         self.id,
            'name':       self.name,
            'target':     self.target,
            'saved':      self.saved,
            'remaining':  max(self.target - self.saved, 0),
            'percent':    round(pct * 100, 1),
            'achieved':   pct >= 1.0,
            'created_at': self.created_at.strftime('%Y/%m/%d'),
        }

class Deposit(db.Model):
    __tablename__ = 'deposits'
    id         = db.Column(db.Integer, primary_key=True)
    goal_id    = db.Column(db.Integer, db.ForeignKey('goals.id'), nullable=False)
    amount     = db.Column(db.Float, nullable=False)
    memo       = db.Column(db.String(200), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':         self.id,
            'goal_id':    self.goal_id,
            'amount':     self.amount,
            'memo':       self.memo,
            'created_at': self.created_at.strftime('%Y/%m/%d %H:%M'),
        }