"""
PostgreSQL-based authentication manager.
Production-ready with JWT tokens, password hashing, and session management.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import secrets
import os
from dotenv import load_dotenv

from auth.db_models import (
    User, Organization, RefreshToken, 
    PasswordResetToken, EmailVerificationToken, AuditLog,
    OrganizationPlan
)
from auth.models import UserCreate, UserLogin, Token, TokenData
from auth.database import get_db

load_dotenv()

# Security Configuration
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour
REFRESH_TOKEN_EXPIRE_DAYS = 30  # 30 days

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class PostgreSQLAuthManager:
    """
    Production-level PostgreSQL-based authentication manager.
    
    Features:
    - JWT access & refresh tokens
    - Bcrypt password hashing
    - Session management with database
    - Multi-tenancy support
    - Email verification
    - Password reset
    - Audit logging
    """
    
    def __init__(self):
        """Initialize auth manager."""
        pass
    
    # ==================== Password Hashing ====================
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)
    
    # ==================== JWT Token Management ====================
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Create JWT refresh token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def verify_token(token: str) -> Optional[TokenData]:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            user_id: str = payload.get("user_id")
            organization_id: str = payload.get("organization_id")
            
            if email is None:
                return None
            
            return TokenData(
                email=email,
                user_id=user_id,
                organization_id=organization_id
            )
        except JWTError:
            return None
    
    # ==================== User Management ====================
    
    def register_user(
        self,
        user_data: UserCreate,
        db: Session
    ) -> User:
        """
        Register a new user and create their organization.
        
        Returns the created user.
        Raises HTTPException if email already exists.
        """
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create organization first
        org_slug = user_data.company.lower().replace(" ", "-").replace("_", "-") if user_data.company else f"org-{secrets.token_hex(4)}"
        
        # Ensure slug is unique
        base_slug = org_slug
        counter = 1
        while db.query(Organization).filter(Organization.slug == org_slug).first():
            org_slug = f"{base_slug}-{counter}"
            counter += 1
        
        organization = Organization(
            name=user_data.company or "Personal",
            slug=org_slug,
            plan=OrganizationPlan.FREE,
            graph_node_limit=1000,
            member_limit=3,
            owner_id=None  # Will update after user creation
        )
        db.add(organization)
        db.flush()  # Get organization ID
        
        # Create user
        hashed_password = self.get_password_hash(user_data.password)
        
        user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            company=user_data.company,
            role=user_data.role,
            organization_id=organization.id,
            is_active=True,
            is_verified=False  # Require email verification
        )
        
        db.add(user)
        db.flush()  # Get user ID
        
        # Update organization owner
        organization.owner_id = user.id
        
        db.commit()
        db.refresh(user)
        db.refresh(organization)
        
        # Log audit event
        self._log_audit(
            db=db,
            user_id=user.id,
            organization_id=organization.id,
            action="user.register",
            resource_type="user",
            resource_id=user.id
        )
        
        return user
    
    def authenticate_user(
        self,
        email: str,
        password: str,
        db: Session
    ) -> Optional[User]:
        """
        Authenticate a user with email and password.
        
        Returns the user if authentication successful, None otherwise.
        """
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            return None
        
        if not self.verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated"
            )
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Log audit event
        self._log_audit(
            db=db,
            user_id=user.id,
            organization_id=user.organization_id,
            action="user.login",
            resource_type="user",
            resource_id=user.id
        )
        
        return user
    
    def login(
        self,
        login_data: UserLogin,
        db: Session,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Token:
        """
        Login user and return access & refresh tokens.
        
        Raises HTTPException if authentication fails.
        """
        user = self.authenticate_user(login_data.email, login_data.password, db)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token = self.create_access_token(
            data={
                "sub": user.email,
                "user_id": user.id,
                "organization_id": user.organization_id
            }
        )
        
        # Create refresh token
        refresh_token_str = self.create_refresh_token(
            data={
                "sub": user.email,
                "user_id": user.id,
                "organization_id": user.organization_id
            }
        )
        
        # Store refresh token in database
        refresh_token = RefreshToken(
            user_id=user.id,
            token=refresh_token_str,
            expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
            user_agent=user_agent,
            ip_address=ip_address
        )
        db.add(refresh_token)
        db.commit()
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token_str,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user={
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "company": user.company,
                "role": user.role,
                "organization_id": user.organization_id,
                "is_verified": user.is_verified
            }
        )
    
    def get_current_user(
        self,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
    ) -> User:
        """
        Get current authenticated user from JWT token.
        
        Use as FastAPI dependency:
            @app.get("/me")
            def get_me(current_user: User = Depends(auth.get_current_user)):
                return current_user
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        token_data = self.verify_token(token)
        if token_data is None or token_data.email is None:
            raise credentials_exception
        
        user = db.query(User).filter(User.email == token_data.email).first()
        if user is None:
            raise credentials_exception
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated"
            )
        
        return user
    
    def refresh_access_token(
        self,
        refresh_token: str,
        db: Session
    ) -> Token:
        """
        Refresh access token using refresh token.
        
        Raises HTTPException if refresh token is invalid.
        """
        # Verify token
        token_data = self.verify_token(refresh_token)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Check if token exists in database and is valid
        db_token = db.query(RefreshToken).filter(
            RefreshToken.token == refresh_token
        ).first()
        
        if not db_token or not db_token.is_valid():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired or revoked"
            )
        
        # Get user
        user = db.query(User).filter(User.id == db_token.user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token
        access_token = self.create_access_token(
            data={
                "sub": user.email,
                "user_id": user.id,
                "organization_id": user.organization_id
            }
        )
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,  # Return same refresh token
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user={
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "company": user.company,
                "role": user.role,
                "organization_id": user.organization_id,
                "is_verified": user.is_verified
            }
        )
    
    def logout(
        self,
        refresh_token: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        Logout user by revoking refresh token.
        """
        db_token = db.query(RefreshToken).filter(
            RefreshToken.token == refresh_token
        ).first()
        
        if db_token:
            db_token.revoked_at = datetime.utcnow()
            db.commit()
            
            # Log audit event
            self._log_audit(
                db=db,
                user_id=db_token.user_id,
                action="user.logout",
                resource_type="user",
                resource_id=db_token.user_id
            )
        
        return {"message": "Successfully logged out"}
    
    # ==================== Audit Logging ====================
    
    def _log_audit(
        self,
        db: Session,
        user_id: Optional[str],
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Log an audit event."""
        audit_log = AuditLog(
            user_id=user_id,
            organization_id=organization_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata or {}
        )
        db.add(audit_log)
        db.commit()


# Global instance
auth_manager = PostgreSQLAuthManager()
