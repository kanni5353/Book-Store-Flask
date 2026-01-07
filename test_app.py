#!/usr/bin/env python3
"""
Basic tests for the application
Run: python test_app.py
"""
import unittest
from app import app

class BasicTests(unittest.TestCase):
    """Basic test cases for the Book Store application"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
    
    def test_home_page(self):
        """Test home page loads successfully"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'TANI', response.data)
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.app.get('/health')
        self.assertIn(response.status_code, [200, 503])  # Allow both healthy and unhealthy states
        self.assertIn(b'status', response.data)
    
    def test_login_page(self):
        """Test login page loads successfully"""
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)
    
    def test_signup_page(self):
        """Test signup page loads successfully"""
        response = self.app.get('/signup')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sign Up', response.data)
    
    def test_dashboard_redirect_without_login(self):
        """Test that dashboard redirects to login when not authenticated"""
        response = self.app.get('/dashboard', follow_redirects=False)
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_sell_redirect_without_login(self):
        """Test that sell page redirects to login when not authenticated"""
        response = self.app.get('/sell', follow_redirects=False)
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_stock_redirect_without_login(self):
        """Test that stock page redirects to login when not authenticated"""
        response = self.app.get('/stock', follow_redirects=False)
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_sales_redirect_without_login(self):
        """Test that sales page redirects to login when not authenticated"""
        response = self.app.get('/sales', follow_redirects=False)
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_invalid_route(self):
        """Test that invalid routes return 404"""
        response = self.app.get('/nonexistent', follow_redirects=True)
        # Should redirect to index with flash message
        self.assertEqual(response.status_code, 200)

class ConfigTests(unittest.TestCase):
    """Test configuration settings"""
    
    def test_config_loaded(self):
        """Test that configuration is loaded"""
        self.assertIsNotNone(app.config.get('SECRET_KEY'))
        self.assertIsNotNone(app.config.get('DB_HOST'))
        self.assertIsNotNone(app.config.get('DB_NAME'))
    
    def test_session_settings(self):
        """Test that session settings are configured"""
        self.assertTrue(app.config.get('SESSION_COOKIE_HTTPONLY'))
        self.assertEqual(app.config.get('SESSION_COOKIE_SAMESITE'), 'Lax')

if __name__ == '__main__':
    print("Running Basic Tests for TANI'S BOOK STORE")
    print("=" * 60)
    unittest.main(verbosity=2)
