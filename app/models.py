from app import db
from datetime import datetime

CONTENT_TYPES = ('video', 'meet', 'pdf')
COURSE_TAGS   = ('general', 'computer', 'ai', 'forex')

class Profile(db.Model):
    """User profile model"""
    __tablename__ = 'profile'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255))
    bio = db.Column(db.Text)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    location = db.Column(db.String(255))
    profile_image_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    skills = db.relationship('Skill', backref='profile', lazy=True, cascade='all, delete-orphan')
    projects = db.relationship('Project', backref='profile', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'title': self.title,
            'bio': self.bio,
            'email': self.email,
            'phone': self.phone,
            'location': self.location,
            'profile_image_url': self.profile_image_url,
        }

class Skill(db.Model):
    """Skills model"""
    __tablename__ = 'skill'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    level = db.Column(db.String(50))  # Beginner, Intermediate, Advanced, Expert
    profile_id = db.Column(db.Integer, db.ForeignKey('profile.id'), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'level': self.level,
        }

class Project(db.Model):
    """Projects model"""
    __tablename__ = 'project'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    url = db.Column(db.String(500))
    github_url = db.Column(db.String(500))
    image_url = db.Column(db.String(500))
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    profile_id = db.Column(db.Integer, db.ForeignKey('profile.id'), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'url': self.url,
            'github_url': self.github_url,
            'image_url': self.image_url,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
        }


class Content(db.Model):
    """Learner content: free video links, Google Meet sessions, PDF resources."""
    __tablename__ = 'content'

    id           = db.Column(db.Integer, primary_key=True)
    title        = db.Column(db.String(300), nullable=False)
    content_type = db.Column(db.String(20), nullable=False)   # video | meet | pdf
    url          = db.Column(db.String(1000))                  # external link or /static/uploads/… path
    description  = db.Column(db.Text)
    course_tag   = db.Column(db.String(50), default='general') # general | computer | ai | forex
    scheduled_at = db.Column(db.DateTime)                      # for meet sessions: when they run
    is_active    = db.Column(db.Boolean, default=True)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at   = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id':           self.id,
            'title':        self.title,
            'content_type': self.content_type,
            'url':          self.url,
            'description':  self.description,
            'course_tag':   self.course_tag,
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'is_active':    self.is_active,
            'created_at':   self.created_at.isoformat(),
        }
