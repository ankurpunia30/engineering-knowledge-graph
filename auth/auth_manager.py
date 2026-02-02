"""
Production-level authentication manager with JWT tokens, password hashing, and session management.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import secrets
import uuid
import json
from pathlib import Path

from .models import User, UserInDB, Token, TokenData, UserCreate, UserLogin, Organization, UserRole, OrganizationPlan


# Security configuration
SECRET_KEY = secrets.token_urlsafe(32)  # Generate a secure random key (in production, use environment variable)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour - industry standard for access tokens
REFRESH_TOKEN_EXPIRE_DAYS = 30  # 30 days for refresh tokens

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class AuthManager:
    """
    Production-level authentication manager.
    
    Features:
    - JWT token-based authentication
    - Bcrypt password hashing
    - Session management (1 hour access tokens)
    - Multi-tenancy (organization-based isolation)
    - Role-based access control
    - Secure password requirements
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """Initialize auth manager with file-based storage (upgrade to database later)."""
        self.storage_path = Path(storage_path or "data/users.json")
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize storage
        if not self.storage_path.exists():
            self._init_storage()
        
        self.users: Dict[str, UserInDB] = {}
        self.organizations: Dict[str, Organization] = {}
        self._load_data()
    
    def _init_storage(self):
        """Initialize empty storage file."""
        initial_data = {
            "users": {},
            "organizations": {}
        }
        with open(self.storage_path, 'w') as f:
            json.dump(initial_data, f, indent=2, default=str)
    
    def _load_data(self):
        """Load users and organizations from storage."""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                
            # Load users
            for user_id, user_data in data.get("users", {}).items():
                # Convert string datetime to datetime objects
                if isinstance(user_data.get("created_at"), str):
                    user_data["created_at"] = datetime.fromisoformat(user_data["created_at"])
                if user_data.get("last_login") and isinstance(user_data["last_login"], str):
                    user_data["last_login"] = datetime.fromisoformat(user_data["last_login"])
                
                self.users[user_id] = UserInDB(**user_data)
            
            # Load organizations
            for org_id, org_data in data.get("organizations", {}).items():
                if isinstance(org_data.get("created_at"), str):
                    org_data["created_at"] = datetime.fromisoformat(org_data["created_at"])
                self.organizations[org_id] = Organization(**org_data)
                
        except Exception as e:
            print(f"Error loading auth data: {e}")
            self.users = {}
            self.organizations = {}
    
    def _save_data(self):
        """Persist users and organizations to storage."""
        try:
            data = {
                "users": {
                    user_id: user.model_dump(mode='json')
                    for user_id, user in self.users.items()
                },
                "organizations": {
                    org_id: org.model_dump(mode='json')
                    for org_id, org in self.organizations.items()
                }
            }
            
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving auth data: {e}")
    
    # ========================================================================
    # Password Hashing
    # ========================================================================
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash using bcrypt."""
        try:
            # Ensure password is within bcrypt's 72-byte limit
            password_bytes = plain_password.encode('utf-8')
            if len(password_bytes) > 72:
                password_bytes = password_bytes[:72]
            
            # Convert hashed password to bytes if it's a string
            if isinstance(hashed_password, str):
                hashed_password = hashed_password.encode('utf-8')
            
            return bcrypt.checkpw(password_bytes, hashed_password)
        except Exception as e:
            print(f"Password verification error: {e}")
            return False
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password using bcrypt."""
        try:
            # Ensure password is within bcrypt's 72-byte limit
            password_bytes = password.encode('utf-8')
            if len(password_bytes) > 72:
                password_bytes = password_bytes[:72]
            
            # Generate salt and hash password
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password_bytes, salt)
            
            # Return as string for JSON serialization
            return hashed.decode('utf-8')
        except Exception as e:
            print(f"Password hashing error: {e}")
            raise
    
    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, str]:
        """
        Validate password meets security requirements.
        
        Requirements:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one number
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"
        
        return True, "Password is strong"
    
    # ========================================================================
    # JWT Token Management
    # ========================================================================
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT access token.
        
        Industry standard: 1 hour expiration for access tokens.
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def decode_token(self, token: str) -> TokenData:
        """Decode and validate a JWT token."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            user_id: str = payload.get("user_id")
            organization_id: str = payload.get("organization_id")
            
            if email is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            return TokenData(email=email, user_id=user_id, organization_id=organization_id)
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    # ========================================================================
    # User Management
    # ========================================================================
    
    def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Get user by email address."""
        for user in self.users.values():
            if user.email == email:
                return user
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        """Get user by ID."""
        return self.users.get(user_id)
    
    def authenticate_user(self, email: str, password: str) -> Optional[UserInDB]:
        """Authenticate user with email and password."""
        user = self.get_user_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user
    
    def create_user(self, user_data: UserCreate) -> tuple[User, Token]:
        """
        Create a new user and organization.
        
        Returns:
            Tuple of (User, Token) for immediate login after registration.
        """
        # Check if user already exists
        if self.get_user_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Validate password strength
        is_valid, message = self.validate_password_strength(user_data.password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        # Create organization first
        org_id = f"org_{uuid.uuid4().hex[:12]}"
        organization = Organization(
            id=org_id,
            name=user_data.organization_name,
            plan=OrganizationPlan.FREE,
            created_at=datetime.utcnow(),
            owner_id="",  # Will be set after user creation
            member_count=1
        )
        
        # Create user
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        hashed_password = self.get_password_hash(user_data.password)
        
        db_user = UserInDB(
            id=user_id,
            email=user_data.email,
            full_name=user_data.full_name,
            organization_id=org_id,
            organization_name=user_data.organization_name,
            role=UserRole.ADMIN,  # First user is admin
            is_active=True,
            created_at=datetime.utcnow(),
            hashed_password=hashed_password
        )
        
        # Update organization owner
        organization.owner_id = user_id
        
        # Save to storage
        self.users[user_id] = db_user
        self.organizations[org_id] = organization
        self._save_data()
        
        # Create user object without password
        user = User(**db_user.model_dump(exclude={"hashed_password"}))
        
        # Generate access token
        access_token = self.create_access_token(
            data={
                "sub": user.email,
                "user_id": user.id,
                "organization_id": user.organization_id
            }
        )
        
        token = Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
            user=user
        )
        
        return user, token
    
    def login_user(self, login_data: UserLogin) -> Token:
        """
        Login user and return JWT token.
        
        Updates last_login timestamp.
        """
        user = self.authenticate_user(login_data.email, login_data.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive. Please contact support."
            )
        
        # Update last login
        user.last_login = datetime.utcnow()
        self.users[user.id] = user
        self._save_data()
        
        # Generate access token
        access_token = self.create_access_token(
            data={
                "sub": user.email,
                "user_id": user.id,
                "organization_id": user.organization_id
            }
        )
        
        # Create user object without password
        user_response = User(**user.model_dump(exclude={"hashed_password"}))
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_response
        )
    
    def get_current_user(self, token: str = Depends(oauth2_scheme)) -> User:
        """
        Get current authenticated user from JWT token.
        
        Use this as a dependency in protected routes:
            @app.get("/protected")
            async def protected_route(current_user: User = Depends(auth_manager.get_current_user)):
                return {"user": current_user.email}
        """
        token_data = self.decode_token(token)
        
        user = self.get_user_by_email(token_data.email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Return user without password
        return User(**user.model_dump(exclude={"hashed_password"}))
    
    def get_current_active_user(self, current_user: User = Depends(lambda token: get_current_user(token))) -> User:
        """
        Get current active user (checks is_active flag).
        
        Use this for routes that require active users only.
        """
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user"
            )
        return current_user


# Global auth manager instance
auth_manager = AuthManager()


# Dependency functions for FastAPI routes
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """FastAPI dependency to get current user."""
    return auth_manager.get_current_user(token)


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """FastAPI dependency to get current active user."""
    return auth_manager.get_current_active_user(current_user)
