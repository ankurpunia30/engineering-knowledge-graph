"""
SQLAlchemy database models for PostgreSQL.
"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Enum as SQLEnum, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
import uuid

from auth.database import Base


class OrganizationPlan(enum.Enum):
    """Organization subscription plans."""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class User(Base):
    """User model for authentication and authorization."""
    __tablename__ = "users"
    
    # Primary Key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile
    full_name = Column(String(255), nullable=False)
    company = Column(String(255), nullable=True)
    role = Column(String(100), nullable=True)  # e.g., "DevOps Engineer", "SRE"
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Organization relationship
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True)
    organization = relationship("Organization", back_populates="members")
    
    # User preferences
    preferences = Column(JSON, default=dict)  # Store UI preferences, theme, etc.
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, org={self.organization_id})>"


class Organization(Base):
    """Organization model for multi-tenancy."""
    __tablename__ = "organizations"
    
    # Primary Key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Organization Info
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)  # URL-friendly name
    
    # Subscription
    plan = Column(SQLEnum(OrganizationPlan), default=OrganizationPlan.FREE, nullable=False)
    plan_started_at = Column(DateTime(timezone=True), server_default=func.now())
    plan_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Limits based on plan
    graph_node_limit = Column(Integer, default=1000, nullable=False)  # FREE: 1000, PRO: 25000
    member_limit = Column(Integer, default=3, nullable=False)  # FREE: 3, PRO: unlimited
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Owner
    owner_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    members = relationship("User", back_populates="organization")
    
    # Settings
    settings = Column(JSON, default=dict)  # Organization-specific settings
    
    def __repr__(self):
        return f"<Organization(id={self.id}, name={self.name}, plan={self.plan.value})>"


class RefreshToken(Base):
    """Refresh token model for JWT token rotation."""
    __tablename__ = "refresh_tokens"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(500), unique=True, nullable=False, index=True)
    
    # Token lifecycle
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(50), nullable=True)
    
    def is_valid(self) -> bool:
        """Check if token is still valid."""
        return (
            self.revoked_at is None and
            self.expires_at > datetime.utcnow()
        )
    
    def __repr__(self):
        return f"<RefreshToken(id={self.id}, user_id={self.user_id}, valid={self.is_valid()})>"


class PasswordResetToken(Base):
    """Password reset token model."""
    __tablename__ = "password_reset_tokens"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(100), unique=True, nullable=False, index=True)
    
    # Token lifecycle
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    
    def is_valid(self) -> bool:
        """Check if token is still valid."""
        return (
            self.used_at is None and
            self.expires_at > datetime.utcnow()
        )
    
    def __repr__(self):
        return f"<PasswordResetToken(id={self.id}, user_id={self.user_id}, valid={self.is_valid()})>"


class EmailVerificationToken(Base):
    """Email verification token model."""
    __tablename__ = "email_verification_tokens"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(100), unique=True, nullable=False, index=True)
    
    # Token lifecycle
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    
    def is_valid(self) -> bool:
        """Check if token is still valid."""
        return (
            self.verified_at is None and
            self.expires_at > datetime.utcnow()
        )
    
    def __repr__(self):
        return f"<EmailVerificationToken(id={self.id}, user_id={self.user_id}, valid={self.is_valid()})>"


class AuditLog(Base):
    """Audit log for tracking user actions."""
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True)
    
    # Action details
    action = Column(String(100), nullable=False, index=True)  # e.g., "user.login", "graph.upload"
    resource_type = Column(String(50), nullable=True)  # e.g., "user", "organization", "graph"
    resource_id = Column(String(100), nullable=True)
    
    # Request context
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Additional data
    metadata = Column(JSON, default=dict)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, user_id={self.user_id})>"
