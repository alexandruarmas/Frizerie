# Booking model removed to avoid duplicate table definitions. Use the Booking model from booking.models instead.

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean, Time, func
from sqlalchemy.orm import relationship
from config.database import Base
from booking.models import StylistAvailability