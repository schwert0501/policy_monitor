from . import db
from datetime import datetime

class Policy(db.Model):
    __tablename__ = 'policies'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=True)
    pub_date = db.Column(db.Date, nullable=False)
    org = db.Column(db.String(100), nullable=False)  # 发文单位
    file_path = db.Column(db.String(255), nullable=True)  # Path to the policy file
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    content_md5 = db.Column(db.String(32), nullable=True)  # MD5 hash of the content for change detection
    source_url = db.Column(db.String(255), nullable=True)  # Source URL of the policy
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category = db.relationship('Category', back_populates='policies')
    
    def __repr__(self):
        return f'<Policy {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'pubDate': self.pub_date.isoformat() if self.pub_date else None,
            'org': self.org,
            'file_path': self.file_path,
            'category': self.category.name,
            'category_id': self.category_id,
            'content_md5': self.content_md5,
            'source_url': self.source_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'newCount': self.is_new()
        }
    
    def is_new(self):
        """Check if the policy was created today"""
        from datetime import date
        today = date.today()
        return 1 if self.created_at and self.created_at.date() == today else 0 