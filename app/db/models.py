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
    phone_number = Column(String)
    role = Column(Enum(UserRole), default=UserRole.CONSUMER)
    is_active = Column(Boolean, default=True)
    
    # Consumer-specific fields
    profile_photo = Column(String)  # URL to photo
    location_text = Column(String)  # Human-readable location
    latitude = Column(Float)
    longitude = Column(Float)
    diet_preference = Column(String)  # vegetarian, low-sodium, etc.
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    vendor_profile = relationship("VendorProfile", back_populates="user", uselist=False)
    ngo_profile = relationship("NGOProfile", back_populates="user", uselist=False)
    inferences = relationship("MLInference", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
    saved_items = relationship("SavedItem", back_populates="user")
    price_lookups = relationship("PriceLookupHistory", back_populates="user")

class VendorProfile(Base):
    __tablename__ = "vendor_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Business information
    business_name = Column(String, nullable=False)  # Previously shop_name
    owner_full_name = Column(String)
    business_type = Column(String)  # market_stall, grocery, farmer, distributor
    business_registration_number = Column(String)
    
    # Location
    location_text = Column(String)  # Previously location
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Verification & Rating
    verified_status = Column(String, default="pending")  # pending, approved, rejected
    rating_score = Column(Float, default=0.0)
    profile_photo = Column(String)  # URL to photo
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
    
    # Pricing
    price_per_unit = Column(Float, nullable=False)
    quantity_unit = Column(String)  # kg, bunch, piece, crate, bag
    currency = Column(String, default="GHS")  # Ghana Cedis
    
    # Quality & Availability
    freshness_status = Column(String)  # fresh, semi-fresh, slightly_spoiled
    stock_availability = Column(Boolean, default=True)
    measurement_accuracy_flag = Column(Boolean, default=True)
    
    # Location
    market_location = Column(String)  # Specific market/stall location
    
    date_posted = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    vendor = relationship("VendorProfile", back_populates="prices")
    food_item = relationship("FoodItem", back_populates="prices")

class Inventory(Base):
    __tablename__ = "inventories"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendor_profiles.id"), nullable=False)
    food_item_id = Column(Integer, ForeignKey("food_items.id"), nullable=False)
    batch_id = Column(String)
    
    # Stock tracking
    quantity = Column(Float, nullable=False)
    current_stock_level = Column(Float)  # Current available stock
    expiry_date = Column(DateTime)
    expected_expiry_date = Column(DateTime)
    
    # Analytics fields (system-computed)
    daily_sales_velocity = Column(Float)  # Average units sold per day
    restock_frequency = Column(Integer)  # Days between restocks
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
    
    # Listing details
    surplus_title = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    condition_status = Column(String)  # edible, near_expiry
    notes = Column(Text)
    
    # Photos
    photos = Column(Text)  # JSON array of image URLs
    
    # Timing
    expiry_date = Column(DateTime, nullable=False)
    pickup_deadline = Column(DateTime)
    
    # Location
    pickup_location = Column(String)
    
    # Status tracking  
    status = Column(Enum(SurplusStatus), default=SurplusStatus.AVAILABLE)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    vendor = relationship("VendorProfile", back_populates="surplus_listings")
    food_item = relationship("FoodItem", back_populates="surplus_listings")
    claims = relationship("SurplusClaim", back_populates="surplus")

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


class NGOProfile(Base):
    """NGO/Food Bank profile for claiming surplus food"""
    __tablename__ = "ngo_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Organization details
    organization_name = Column(String, nullable=False)
    organization_type = Column(String)  # food_bank, charity, outreach, etc.
    registration_number = Column(String)
    
    # Contact & Location
    address = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Operations
    operational_hours = Column(String)  # e.g., "Mon-Fri 8AM-5PM"
    focus_areas = Column(Text)  # JSON array: ["feeding children", "waste reduction"]
    
    # Verification
    verification_status = Column(String, default="pending")  # pending, verified, rejected
    partner_code = Column(String, unique=True)  # Optional partner reference
    
    # Pickup preferences (Phase 2)
    preferred_pickup_window = Column(String)
    delivery_capacity = Column(Integer)  # Number of collections per week
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="ngo_profile")
    claims = relationship("SurplusClaim", back_populates="ngo")


class SurplusClaim(Base):
    """Track NGO claims of surplus food"""
    __tablename__ = "surplus_claims"
    
    id = Column(Integer, primary_key=True, index=True)
    surplus_id = Column(Integer, ForeignKey("surplus_listings.id"), nullable=False)
    ngo_id = Column(Integer, ForeignKey("ngo_profiles.id"), nullable=False)
    
    # Timestamps
    timestamp_claimed = Column(DateTime, default=datetime.utcnow)
    timestamp_collected = Column(DateTime, nullable=True)
    
    # Proof of collection
    collection_photo_proof = Column(String)  # URL to photo
    
    # Status
    status = Column(String, default="claimed")  # claimed, collected, cancelled
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    surplus = relationship("SurplusListing", back_populates="claims")
    ngo = relationship("NGOProfile", back_populates="claims")


class SavedItem(Base):
    """User's saved/favorite food items"""
    __tablename__ = "saved_items"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("food_items.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="saved_items")
    item = relationship("FoodItem")


class PriceLookupHistory(Base):
    """Track user price searches for analytics"""
    __tablename__ = "price_lookup_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("food_items.id"), nullable=True)
    
    search_query = Column(String)
    location_used = Column(String)
    found_price_range = Column(Text)  # JSON: {"min": 5.0, "max": 12.0, "avg": 8.5}
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="price_lookups")
    item = relationship("FoodItem")
