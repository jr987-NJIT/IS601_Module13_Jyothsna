import pytest
from playwright.sync_api import Page, expect
import time
import subprocess
import sys
import os

# We need to run the server for E2E tests
# In a real CI environment, the server would be started separately
# For local testing, we can assume it's running or start it
# Here we'll assume the user or CI starts it, but we can add a check

BASE_URL = "http://localhost:8000"

@pytest.fixture(scope="session", autouse=True)
def ensure_server_running():
    """
    Ensure the server is running before tests.
    In CI, this is handled by the workflow.
    Locally, you should run `uvicorn app.main:app --reload`
    """
    # Simple check if server is reachable
    import requests
    try:
        requests.get(f"{BASE_URL}/health")
    except requests.exceptions.ConnectionError:
        pytest.fail(f"Server is not running at {BASE_URL}. Please start it before running E2E tests.")

def test_register_success(page: Page):
    """Test successful user registration."""
    page.goto(f"{BASE_URL}/static/register.html")
    
    # Generate unique user
    timestamp = int(time.time())
    username = f"user_{timestamp}"
    email = f"user_{timestamp}@example.com"
    password = "securepassword123"
    
    page.fill("#username", username)
    page.fill("#email", email)
    page.fill("#password", password)
    page.fill("#confirmPassword", password)
    
    page.click("button[type='submit']")
    
    # Check for success message
    success_message = page.locator(".alert-success")
    expect(success_message).to_be_visible()
    expect(success_message).to_contain_text("Registration successful")

def test_register_password_mismatch(page: Page):
    """Test registration with password mismatch."""
    page.goto(f"{BASE_URL}/static/register.html")
    
    page.fill("#username", "testuser")
    page.fill("#email", "test@example.com")
    page.fill("#password", "password123")
    page.fill("#confirmPassword", "password456")
    
    page.click("button[type='submit']")
    
    error_message = page.locator(".alert-danger")
    expect(error_message).to_be_visible()
    expect(error_message).to_contain_text("Passwords do not match")

def test_register_short_password(page: Page):
    """Test registration with short password."""
    page.goto(f"{BASE_URL}/static/register.html")
    
    page.fill("#username", "testuser")
    page.fill("#email", "test@example.com")
    page.fill("#password", "short")
    page.fill("#confirmPassword", "short")
    
    page.click("button[type='submit']")
    
    error_message = page.locator(".alert-danger")
    expect(error_message).to_be_visible()
    expect(error_message).to_contain_text("Password must be at least 8 characters")

def test_login_success(page: Page):
    """Test successful login."""
    # First register a user
    timestamp = int(time.time())
    username = f"login_user_{timestamp}"
    email = f"login_{timestamp}@example.com"
    password = "securepassword123"
    
    # Register via API to speed up
    import requests
    requests.post(f"{BASE_URL}/users/register", json={
        "username": username,
        "email": email,
        "password": password
    })
    
    page.goto(f"{BASE_URL}/static/login.html")
    
    page.fill("#username", username)
    page.fill("#password", password)
    
    page.click("button[type='submit']")
    
    success_message = page.locator(".alert-success")
    expect(success_message).to_be_visible()
    expect(success_message).to_contain_text("Login successful")

def test_login_failure(page: Page):
    """Test login with invalid credentials."""
    page.goto(f"{BASE_URL}/static/login.html")
    
    page.fill("#username", "nonexistentuser")
    page.fill("#password", "wrongpassword")
    
    page.click("button[type='submit']")
    
    error_message = page.locator(".alert-danger")
    expect(error_message).to_be_visible()
    expect(error_message).to_contain_text("Invalid credentials")
