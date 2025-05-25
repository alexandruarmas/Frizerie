from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, func
from sqlalchemy.orm import relationship
from config.database import Base

class Notification(Base):
    """Notification model for user notifications."""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    method = Column(String(20), default="local")  # local, sms
    sent_at = Column(DateTime, default=func.now())
    status = Column(String(20), default="pending")  # pending, sent, delivered, failed
    
    # Relationships
    # user = relationship("User", back_populates="notifications")
    
    def __repr__(self):
        return f"<Notification {self.id} for user {self.user_id}>" 