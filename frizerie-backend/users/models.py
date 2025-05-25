from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from config.database import Base

# Remove this line as it redefines Base
# Base = declarative_base()

class User(Base):
    """User model representing customers and stylists."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    vip_level = Column(String(20), default="BRONZE")
    loyalty_points = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relații
    bookings = relationship("Booking", back_populates="user")
    # notifications = relationship("Notification", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.email}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "vip_level": self.vip_level,
            "loyalty_points": self.loyalty_points
        }


class VIPTier(Base):
    """VIP Tier model for defining loyalty tiers and perks."""
    __tablename__ = "vip_tiers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), unique=True, nullable=False)  # BRONZE, SILVER, GOLD, DIAMOND
    min_points = Column(Integer, nullable=False)
    perks = Column(Text, nullable=True)  # JSON string or description
    
    def __repr__(self):
        return f"<VIPTier {self.name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "min_points": self.min_points,
            "perks": self.perks
        } 