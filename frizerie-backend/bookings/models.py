from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean, Time, func
from sqlalchemy.orm import relationship
from config.database import Base

class Booking(Base):
    """Booking model for appointments."""
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stylist_id = Column(Integer, ForeignKey("stylists.id"), nullable=False)
    service_type = Column(String(100), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(String(20), default="SCHEDULED")  # SCHEDULED, COMPLETED, CANCELLED
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="bookings")
    stylist = relationship("Stylist", back_populates="bookings")
    
    def __repr__(self):
        return f"<Booking {self.id}: {self.user_id} with {self.stylist_id}>"

class Stylist(Base):
    """Stylist model for barbers and hairdressers."""
    __tablename__ = "stylists"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    specialization = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    bookings = relationship("Booking", back_populates="stylist")
    availability = relationship("StylistAvailability", back_populates="stylist")
    
    def __repr__(self):
        return f"<Stylist {self.name}>"

class StylistAvailability(Base):
    """Stylist availability model for defining working hours."""
    __tablename__ = "stylist_availability"
    
    id = Column(Integer, primary_key=True, index=True)
    stylist_id = Column(Integer, ForeignKey("stylists.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    vip_restricted = Column(Boolean, default=False)
    
    # Relationships
    stylist = relationship("Stylist", back_populates="availability")
    
    def __repr__(self):
        return f"<StylistAvailability {self.stylist_id} from {self.start_time} to {self.end_time}>" 