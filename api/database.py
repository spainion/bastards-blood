"""Database configuration and models using SQLAlchemy."""
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, JSON, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timezone
from passlib.context import CryptContext
import os

# Database URL from environment or default to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bastards_blood.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    """User account model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    characters = relationship("DBCharacter", back_populates="owner")
    
    def verify_password(self, password: str) -> bool:
        """Verify password against hash."""
        return pwd_context.verify(password, self.hashed_password)
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)


class DBCharacter(Base):
    """Character stored in database."""
    __tablename__ = "characters"
    
    id = Column(String(50), primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    class_name = Column(String(50))
    level = Column(Integer, default=1)
    xp = Column(Integer, default=0)
    
    # Stats
    stats = Column(JSON, nullable=False)
    hp_max = Column(Integer, default=100)
    hp_current = Column(Integer, default=100)
    
    # Location
    location_x = Column(Float, default=0.0)
    location_y = Column(Float, default=0.0)
    location_z = Column(Float, default=0.0)
    region = Column(String(100))
    area = Column(String(100))
    
    # Extended data
    inventory = Column(JSON, default=list)
    equipment = Column(JSON, default=dict)
    skills = Column(JSON, default=dict)
    attributes = Column(JSON, default=dict)
    currency = Column(JSON, default=dict)
    
    # Metadata
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    is_alive = Column(Boolean, default=True)
    
    # Relationships
    owner = relationship("User", back_populates="characters")


class DBEnemy(Base):
    """Enemy/Mob stored in database."""
    __tablename__ = "enemies"
    
    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    enemy_type = Column(String(50), nullable=False)
    level = Column(Integer, default=1)
    
    # Stats
    stats = Column(JSON, nullable=False)
    hp_max = Column(Integer, default=100)
    hp_current = Column(Integer, default=100)
    
    # Combat
    damage_min = Column(Integer, default=1)
    damage_max = Column(Integer, default=10)
    armor = Column(Integer, default=0)
    attack_speed = Column(Float, default=1.0)
    aggro_range = Column(Float, default=10.0)
    
    # Loot
    xp_reward = Column(Integer, default=10)
    loot_table = Column(JSON, default=dict)
    
    # Location
    spawn_x = Column(Float, default=0.0)
    spawn_y = Column(Float, default=0.0)
    spawn_z = Column(Float, default=0.0)
    current_x = Column(Float, default=0.0)
    current_y = Column(Float, default=0.0)
    current_z = Column(Float, default=0.0)
    region = Column(String(100))
    
    # AI
    ai_type = Column(String(50), default="aggressive")
    behavior_pattern = Column(String(50), default="patrol")
    abilities = Column(JSON, default=list)
    
    # State
    is_alive = Column(Boolean, default=True)
    respawn_time = Column(Integer, default=300)  # seconds
    last_death = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class CombatLog(Base):
    """Combat log for tracking fights."""
    __tablename__ = "combat_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    combat_id = Column(String(100), nullable=False, index=True)
    
    # Participants
    attacker_id = Column(String(100), nullable=False)
    attacker_type = Column(String(20), nullable=False)  # "player" or "enemy"
    defender_id = Column(String(100), nullable=False)
    defender_type = Column(String(20), nullable=False)
    
    # Action
    action_type = Column(String(50), nullable=False)  # "attack", "cast_spell", "use_ability"
    damage_dealt = Column(Integer, default=0)
    damage_type = Column(String(50), default="physical")
    was_critical = Column(Boolean, default=False)
    was_miss = Column(Boolean, default=False)
    
    # State changes
    attacker_hp_before = Column(Integer)
    attacker_hp_after = Column(Integer)
    defender_hp_before = Column(Integer)
    defender_hp_after = Column(Integer)
    
    # Results
    defender_defeated = Column(Boolean, default=False)
    xp_gained = Column(Integer, default=0)
    loot_dropped = Column(JSON, default=list)
    
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class GameSession(Base):
    """Active game session."""
    __tablename__ = "game_sessions"
    
    id = Column(String(100), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    character_id = Column(String(50), nullable=False)
    
    # Session data
    campaign = Column(String(100))
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_activity = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)
    
    # Real-time data
    websocket_connected = Column(Boolean, default=False)
    connection_id = Column(String(100), nullable=True)


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
