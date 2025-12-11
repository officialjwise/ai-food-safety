import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float, Enum, Text
from sqlalchemy.orm import relationship
from app.db.database import Base

class UserRole(str, enum.Enum):
    CONSUMER = "consumer"
    VENDOR = "vendor"
    NGO = "ngo"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(Enum(UserRole), default=UserRole.CONSUMER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    vendor_profile = relationship("VendorProfile", back_populates="user", uselist=False)
    inferences = relationship("MLInference", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")

class VendorProfile(Base):
    __tablename__ = "vendor_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    shop_name = Column(String, nullable=False)
    location = Column(String)
    verified = Column(Boolean, default=False)

    user = relationship("User", back_populates="vendor_profile")
    prices = relationship("VendorPrice", back_populates="vendor")
    inventories = relationship("Inventory", back_populates="vendor")
    surplus_listings = relationship("SurplusListing", back_populates="vendor")

class FoodItem(Base):
    __tablename__ = "food_items"

    id = Column(Integer, primary_key=True, index=True)
    canonical_name = Column(String, unique=True, index=True, nullable=False)
    category = Column(String)
    example_image_url = Column(String)
    
    nutrition = relationship("NutritionData", back_populates="food_item", uselist=False)
    prices = relationship("VendorPrice", back_populates="food_item")
    inventories = relationship("Inventory", back_populates="food_item")
    surplus_listings = relationship("SurplusListing", back_populates="food_item")
    inferences = relationship("MLInference", back_populates="food_item")

class NutritionData(Base):
    __tablename__ = "nutrition_data"

    id = Column(Integer, primary_key=True, index=True)
    food_item_id = Column(Integer, ForeignKey("food_items.id"), unique=True, nullable=False)
    
    # Source information
    data_source = Column(String)  # "FAO", "USDA", "WHO", "Manual"
    source_id = Column(String)  # External database reference ID
    
    # Macronutrients (per 100g)
    calories_per_100g = Column(Float)
    protein_per_100g = Column(Float)
    carbs_per_100g = Column(Float)
    fat_per_100g = Column(Float)
    fiber_per_100g = Column(Float)
    sugar_per_100g = Column(Float)
    
    # Micronutrients (per 100g) - Vitamins
    vitamin_a_mcg = Column(Float)  # Vitamin A in micrograms
    vitamin_c_mg = Column(Float)   # Vitamin C in milligrams
    vitamin_d_mcg = Column(Float)
    vitamin_e_mg = Column(Float)
    vitamin_k_mcg = Column(Float)
    vitamin_b1_mg = Column(Float)  # Thiamine
    vitamin_b2_mg = Column(Float)  # Riboflavin
    vitamin_b3_mg = Column(Float)  # Niacin
    vitamin_b6_mg = Column(Float)
    vitamin_b12_mcg = Column(Float)
    folate_mcg = Column(Float)
    
    # Minerals (per 100g)
    calcium_mg = Column(Float)
    iron_mg = Column(Float)
    magnesium_mg = Column(Float)
    phosphorus_mg = Column(Float)
    potassium_mg = Column(Float)
    sodium_mg = Column(Float)
    zinc_mg = Column(Float)
    
    # Other properties
    water_content_percent = Column(Float)
    
    # Food preservation metadata
    spoilage_risk_level = Column(String)  # "low", "medium", "high"
    recommended_storage = Column(String)  # "refrigerate", "room_temp", "freeze"
    shelf_life_days = Column(Integer)
    
    food_item = relationship("FoodItem", back_populates="nutrition")


class VendorPrice(Base):
    __tablename__ = "vendor_prices"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendor_profiles.id"), nullable=False)
    food_item_id = Column(Integer, ForeignKey("food_items.id"), nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    date_posted = Column(DateTime, default=datetime.utcnow)

    vendor = relationship("VendorProfile", back_populates="prices")
    food_item = relationship("FoodItem", back_populates="prices")

class Inventory(Base):
    __tablename__ = "inventories"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendor_profiles.id"), nullable=False)
    food_item_id = Column(Integer, ForeignKey("food_items.id"), nullable=False)
    batch_id = Column(String)
    quantity = Column(Float, nullable=False)
    expiry_date = Column(DateTime)

    vendor = relationship("VendorProfile", back_populates="inventories")
    food_item = relationship("FoodItem", back_populates="inventories")

class SurplusStatus(str, enum.Enum):
    AVAILABLE = "available"
    CLAIMED = "claimed"
    COLLECTED = "collected"
    EXPIRED = "expired"

class SurplusListing(Base):
    __tablename__ = "surplus_listings"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendor_profiles.id"), nullable=False)
    food_item_id = Column(Integer, ForeignKey("food_items.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    expiry_date = Column(DateTime, nullable=False)
    status = Column(Enum(SurplusStatus), default=SurplusStatus.AVAILABLE)
    created_at = Column(DateTime, default=datetime.utcnow)
    claimed_by_ngo_id = Column(Integer, ForeignKey("users.id"), nullable=True) # NGO User ID

    vendor = relationship("VendorProfile", back_populates="surplus_listings")
    food_item = relationship("FoodItem", back_populates="surplus_listings")

class MLInference(Base):
    __tablename__ = "ml_inferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    food_item_id = Column(Integer, ForeignKey("food_items.id"), nullable=True)
    image_path = Column(String, nullable=False)
    label = Column(String)
    confidence = Column(Float)
    contamination_score = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="inferences")
    food_item = relationship("FoodItem", back_populates="inferences")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)
    meta_data = Column(Text) # JSON string or similar
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="audit_logs")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class OTPCode(Base):
    __tablename__ = "otp_codes"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True, nullable=False)
    code = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

