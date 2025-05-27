from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, func, Float, UniqueConstraint, Boolean, Time
from sqlalchemy.orm import relationship
from config.database import Base

class StylistReview(Base):
    """Model for stylist reviews and ratings."""
    __tablename__ = "stylist_reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stylist_id = Column(Integer, ForeignKey("stylists.id"), nullable=False)
    rating = Column(Float, nullable=False) # Rating between 1.0 and 5.0
    review_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Ensure a user can only review a stylist once
    __table_args__ = (UniqueConstraint('user_id', 'stylist_id', name='_user_stylist_uc'),)

    # Relationships
    user = relationship("User", back_populates="stylist_reviews")
    stylist = relationship("Stylist", back_populates="reviews")

    def __repr__(self):
        return f"<StylistReview {self.id} by user {self.user_id} for stylist {self.stylist_id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "stylist_id": self.stylist_id,
            "rating": self.rating,
            "review_text": self.review_text,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

class Stylist(Base):
    """Stylist model for barbers and hairdressers."""
    __tablename__ = "stylists"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    specialization = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    average_rating = Column(Float, default=0.0) # New field for average rating
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    bookings = relationship("Booking", back_populates="stylist")
    availability = relationship("StylistAvailability", back_populates="stylist")
    reviews = relationship("StylistReview", back_populates="stylist") # New relationship to reviews
    
    def __repr__(self):
        return f"<Stylist {self.name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "specialization": self.specialization,
            "bio": self.bio,
            "avatar_url": self.avatar_url,
            "is_active": self.is_active,
            "average_rating": self.average_rating,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        } 