#!/usr/bin/env python3
"""
Multi-Tenancy Test Script
Tests that organizations cannot see each other's data.
"""

import requests
import json
import time
from typing import Optional

BASE_URL = "http://localhost:8000"


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")


def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")


def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")


def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")


def register_user(email: str, password: str, org_name: str) -> dict:
    """Register a new user."""
    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": f"Test User {org_name}",
            "organization_name": org_name
        }
    )
    return response.json()


def login_user(email: str, password: str) -> Optional[str]:
    """Login and return access token."""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": email, "password": password}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None


def get_graph_data(token: str) -> dict:
    """Get graph data for authenticated user."""
    response = requests.get(
        f"{BASE_URL}/api/graph/data",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()


def upload_test_data(token: str, org_name: str) -> bool:
    """Upload test YAML data."""
    # Create test docker-compose content
    yaml_content = f"""
version: '3.8'
services:
  {org_name.lower()}-web:
    image: nginx:latest
    ports:
      - "8080:80"
    depends_on:
      - {org_name.lower()}-db
  
  {org_name.lower()}-db:
    image: postgres:15
    environment:
      POSTGRES_DB: {org_name.lower()}
"""
    
    files = {'file': (f'{org_name}-config.yml', yaml_content)}
    data = {'file_type': 'docker_compose'}
    
    response = requests.post(
        f"{BASE_URL}/api/upload",
        files=files,
        data=data,
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.status_code == 200


def get_org_info(token: str) -> dict:
    """Get organization information."""
    response = requests.get(
        f"{BASE_URL}/api/organization/info",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()


def test_multi_tenancy():
    """Run comprehensive multi-tenancy test."""
    print("=" * 80)
    print("Multi-Tenancy Isolation Test")
    print("=" * 80)
    print()
    
    # Generate unique test data
    timestamp = int(time.time())
    org_a_name = f"TestOrgA_{timestamp}"
    org_b_name = f"TestOrgB_{timestamp}"
    
    user_a_email = f"usera_{timestamp}@test.com"
    user_b_email = f"userb_{timestamp}@test.com"
    password = "TestPassword123!"
    
    print_info(f"Creating test organizations:")
    print(f"  • {org_a_name}")
    print(f"  • {org_b_name}")
    print()
    
    # Test 1: Register users in different organizations
    print("Test 1: User Registration")
    print("-" * 80)
    
    try:
        print_info(f"Registering user for {org_a_name}...")
        reg_a = register_user(user_a_email, password, org_a_name)
        if "access_token" in reg_a:
            print_success(f"User A registered: {user_a_email}")
        else:
            print_error(f"Failed to register User A: {reg_a}")
            return
        
        print_info(f"Registering user for {org_b_name}...")
        reg_b = register_user(user_b_email, password, org_b_name)
        if "access_token" in reg_b:
            print_success(f"User B registered: {user_b_email}")
        else:
            print_error(f"Failed to register User B: {reg_b}")
            return
    except Exception as e:
        print_error(f"Registration failed: {e}")
        return
    
    print()
    
    # Test 2: Login users
    print("Test 2: Authentication")
    print("-" * 80)
    
    token_a = login_user(user_a_email, password)
    token_b = login_user(user_b_email, password)
    
    if token_a:
        print_success(f"User A logged in successfully")
    else:
        print_error("Failed to login User A")
        return
    
    if token_b:
        print_success(f"User B logged in successfully")
    else:
        print_error("Failed to login User B")
        return
    
    print()
    
    # Test 3: Verify organization info
    print("Test 3: Organization Information")
    print("-" * 80)
    
    org_info_a = get_org_info(token_a)
    org_info_b = get_org_info(token_b)
    
    print_info(f"User A organization: {org_info_a.get('organization_name')}")
    print_info(f"User B organization: {org_info_b.get('organization_name')}")
    
    if org_info_a.get('organization_name') == org_a_name:
        print_success("User A has correct organization")
    else:
        print_error(f"User A organization mismatch!")
        return
    
    if org_info_b.get('organization_name') == org_b_name:
        print_success("User B has correct organization")
    else:
        print_error(f"User B organization mismatch!")
        return
    
    print()
    
    # Test 4: Upload data for Org A
    print("Test 4: Data Upload - Organization A")
    print("-" * 80)
    
    print_info(f"Uploading test data for {org_a_name}...")
    if upload_test_data(token_a, org_a_name):
        print_success("Data uploaded for Organization A")
    else:
        print_error("Failed to upload data for Organization A")
        return
    
    # Give backend time to process
    time.sleep(1)
    
    print()
    
    # Test 5: Upload data for Org B
    print("Test 5: Data Upload - Organization B")
    print("-" * 80)
    
    print_info(f"Uploading test data for {org_b_name}...")
    if upload_test_data(token_b, org_b_name):
        print_success("Data uploaded for Organization B")
    else:
        print_error("Failed to upload data for Organization B")
        return
    
    time.sleep(1)
    
    print()
    
    # Test 6: Verify data isolation
    print("Test 6: Data Isolation Verification")
    print("-" * 80)
    
    print_info("Fetching graph data for User A...")
    graph_a = get_graph_data(token_a)
    nodes_a = graph_a.get('nodes', {})
    
    print_info("Fetching graph data for User B...")
    graph_b = get_graph_data(token_b)
    nodes_b = graph_b.get('nodes', {})
    
    print_info(f"User A sees {len(nodes_a)} nodes")
    print_info(f"User B sees {len(nodes_b)} nodes")
    
    # Check Org A's nodes
    org_a_nodes = [n for n in nodes_a.values() 
                   if org_a_name.lower() in n.get('id', '').lower()]
    org_a_has_own = len(org_a_nodes) > 0
    
    # Check if Org A sees Org B's nodes
    org_a_sees_b = any(org_b_name.lower() in n.get('id', '').lower() 
                       for n in nodes_a.values())
    
    # Check Org B's nodes
    org_b_nodes = [n for n in nodes_b.values() 
                   if org_b_name.lower() in n.get('id', '').lower()]
    org_b_has_own = len(org_b_nodes) > 0
    
    # Check if Org B sees Org A's nodes
    org_b_sees_a = any(org_a_name.lower() in n.get('id', '').lower() 
                       for n in nodes_b.values())
    
    print()
    print("Isolation Test Results:")
    print("-" * 80)
    
    # Verify isolation
    isolation_passed = True
    
    if org_a_has_own:
        print_success(f"✓ Organization A can see their own data ({len(org_a_nodes)} nodes)")
    else:
        print_error("✗ Organization A cannot see their own data")
        isolation_passed = False
    
    if not org_a_sees_b:
        print_success("✓ Organization A CANNOT see Organization B's data")
    else:
        print_error("✗ Organization A CAN see Organization B's data (DATA LEAK!)")
        isolation_passed = False
    
    if org_b_has_own:
        print_success(f"✓ Organization B can see their own data ({len(org_b_nodes)} nodes)")
    else:
        print_error("✗ Organization B cannot see their own data")
        isolation_passed = False
    
    if not org_b_sees_a:
        print_success("✓ Organization B CANNOT see Organization A's data")
    else:
        print_error("✗ Organization B CAN see Organization A's data (DATA LEAK!)")
        isolation_passed = False
    
    print()
    print("=" * 80)
    
    if isolation_passed:
        print_success("🎉 MULTI-TENANCY TEST PASSED!")
        print_success("Organizations are completely isolated from each other.")
    else:
        print_error("🚨 MULTI-TENANCY TEST FAILED!")
        print_error("Data leakage detected between organizations!")
    
    print("=" * 80)
    print()
    
    # Cleanup info
    print_info("Test completed. You can manually delete test users from database if needed:")
    print(f"  DELETE FROM users WHERE email IN ('{user_a_email}', '{user_b_email}');")
    print()
    
    return isolation_passed


if __name__ == "__main__":
    try:
        # Check if backend is running
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            print_success("Backend is running")
            print()
        except:
            print_error("Backend is not running at http://localhost:8000")
            print_info("Start it with: python main.py")
            exit(1)
        
        # Run test
        result = test_multi_tenancy()
        exit(0 if result else 1)
        
    except KeyboardInterrupt:
        print()
        print_warning("Test interrupted by user")
        exit(1)
    except Exception as e:
        print_error(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
