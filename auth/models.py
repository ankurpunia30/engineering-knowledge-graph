"""
Authentication models for user management and JWT tokens.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User roles for access control."""
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class OrganizationPlan(str, Enum):
    """Organization subscription plans."""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class User(BaseModel):
    """User model for API responses."""
    id: str
    email: EmailStr
    full_name: str
    organization_id: str
    organization_name: str
    role: UserRole = UserRole.MEMBER
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime] = None


class UserInDB(User):
    """User model with hashed password for database storage."""
    hashed_password: str


class UserCreate(BaseModel):
    """User registration model."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=100)
    organization_name: str = Field(..., min_length=2, max_length=255)
    role: Optional[str] = Field(None, max_length=100)  # Job role like "DevOps Engineer"
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "engineer@company.com",
                "password": "SecurePass123!",
                "full_name": "John Doe",
                "organization_name": "Acme Corp",
                "role": "DevOps Engineer"
            }
        }


class UserLogin(BaseModel):
    """User login model."""
    email: EmailStr
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "engineer@company.com",
                "password": "SecurePass123!"
            }
        }


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int = 3600  # 1 hour
    user: User  # User object without password


class TokenData(BaseModel):
    """JWT token payload data."""
    email: Optional[str] = None
    user_id: Optional[str] = None
    organization_id: Optional[str] = None


class Organization(BaseModel):
    """Organization model."""
    id: str
    name: str
    plan: OrganizationPlan = OrganizationPlan.FREE
    created_at: datetime
    owner_id: str
    member_count: int = 0
    graph_node_limit: int = 1000  # FREE: 1000, STARTER: 5000, PRO: 25000, ENT: unlimited
    is_active: bool = True


class PasswordReset(BaseModel):
    """Password reset request model."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation model."""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)
