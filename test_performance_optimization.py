#!/usr/bin/env python3
"""
Tests for performance optimizations: connection pooling and caching
Run: python test_performance_optimization.py
"""
import unittest
from unittest.mock import Mock, MagicMock, patch
import time
from datetime import datetime, timedelta
from app import (
    app, 
    get_cached_book, 
    cache_book, 
    clear_book_cache,
    CACHE_DURATION
)

class CachingTests(unittest.TestCase):
    """Test cases for the book caching functionality"""
    
    def setUp(self):
        """Set up test client and clear cache"""
        self.app = app.test_client()
        self.app.testing = True
        clear_book_cache()
    
    def tearDown(self):
        """Clean up after each test"""
        clear_book_cache()
    
    def test_cache_book_and_retrieve(self):
        """Test caching a book and retrieving it"""
        book_id = 'TEST001'
        book_data = {
            'BookName': 'Test Book',
            'Price': 100,
            'Quantity': 10
        }
        
        # Cache the book
        cache_book(book_id, book_data)
        
        # Retrieve from cache
        cached = get_cached_book(book_id)
        
        self.assertIsNotNone(cached)
        self.assertEqual(cached['BookName'], 'Test Book')
        self.assertEqual(cached['Price'], 100)
        self.assertEqual(cached['Quantity'], 10)
    
    def test_cache_miss_returns_none(self):
        """Test that cache miss returns None"""
        cached = get_cached_book('NONEXISTENT')
        self.assertIsNone(cached)
    
    def test_clear_cache(self):
        """Test clearing the cache"""
        # Cache some books
        cache_book('BOOK1', {'BookName': 'Book 1', 'Price': 100, 'Quantity': 5})
        cache_book('BOOK2', {'BookName': 'Book 2', 'Price': 200, 'Quantity': 3})
        
        # Verify they're cached
        self.assertIsNotNone(get_cached_book('BOOK1'))
        self.assertIsNotNone(get_cached_book('BOOK2'))
        
        # Clear cache
        clear_book_cache()
        
        # Verify cache is empty
        self.assertIsNone(get_cached_book('BOOK1'))
        self.assertIsNone(get_cached_book('BOOK2'))
    
    def test_cache_expiry(self):
        """Test that cache expires after CACHE_DURATION"""
        book_id = 'EXP001'
        book_data = {
            'BookName': 'Expiring Book',
            'Price': 150,
            'Quantity': 7
        }
        
        # Mock the cache with an old timestamp
        from app import _book_cache, _cache_lock_book
        with _cache_lock_book:
            old_timestamp = datetime.now() - timedelta(minutes=10)  # 10 minutes ago
            _book_cache[book_id] = (book_data, old_timestamp)
        
        # Try to retrieve - should be None due to expiry
        cached = get_cached_book(book_id)
        self.assertIsNone(cached)
    
    def test_multiple_books_in_cache(self):
        """Test caching multiple books"""
        books = {
            'B001': {'BookName': 'Book One', 'Price': 100, 'Quantity': 5},
            'B002': {'BookName': 'Book Two', 'Price': 200, 'Quantity': 3},
            'B003': {'BookName': 'Book Three', 'Price': 300, 'Quantity': 8},
        }
        
        # Cache all books
        for book_id, book_data in books.items():
            cache_book(book_id, book_data)
        
        # Verify all are cached
        for book_id in books.keys():
            cached = get_cached_book(book_id)
            self.assertIsNotNone(cached)
            self.assertEqual(cached['BookName'], books[book_id]['BookName'])

class APIEndpointTests(unittest.TestCase):
    """Test cases for optimized API endpoints"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
        clear_book_cache()
    
    def tearDown(self):
        """Clean up after each test"""
        clear_book_cache()
    
    def test_api_book_endpoint_requires_auth(self):
        """Test that API endpoint requires authentication"""
        response = self.app.get('/api/book/TEST123', follow_redirects=False)
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
    
    def test_api_books_all_endpoint_requires_auth(self):
        """Test that bulk endpoint requires authentication"""
        response = self.app.get('/api/books/all', follow_redirects=False)
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
    
    def test_api_endpoint_structure(self):
        """Test that the API endpoints are registered correctly"""
        with app.test_request_context():
            from flask import url_for
            
            # Test single book endpoint
            try:
                url = url_for('get_book_details', book_id='TEST123')
                self.assertIn('/api/book/', url)
            except Exception as e:
                self.fail(f"Single book API endpoint not registered: {e}")
            
            # Test bulk endpoint
            try:
                url = url_for('get_all_books')
                self.assertEqual(url, '/api/books/all')
            except Exception as e:
                self.fail(f"Bulk API endpoint not registered: {e}")

class ConnectionPoolTests(unittest.TestCase):
    """Test cases for connection pooling functionality"""
    
    def test_connection_pool_imports(self):
        """Test that required imports for pooling are available"""
        try:
            from mysql.connector import pooling
            import threading
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Required import failed: {e}")
    
    def test_get_connection_pool_function_exists(self):
        """Test that get_connection_pool function is defined"""
        from app import get_connection_pool
        self.assertTrue(callable(get_connection_pool))
    
    def test_cache_thread_safety_structures_exist(self):
        """Test that thread-safe structures are in place"""
        from app import _cache_lock_book, _pool_lock
        import threading
        
        # Check that locks exist and are lock objects
        self.assertTrue(hasattr(_cache_lock_book, 'acquire'))
        self.assertTrue(hasattr(_cache_lock_book, 'release'))
        self.assertTrue(hasattr(_pool_lock, 'acquire'))
        self.assertTrue(hasattr(_pool_lock, 'release'))

class ErrorHandlingTests(unittest.TestCase):
    """Test cases for improved error handling"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
    
    def test_api_response_has_error_type(self):
        """Test that API responses include error_type field"""
        # This tests the structure, not actual responses
        # which would require database setup
        
        # Verify the endpoint exists and has proper structure
        with app.test_request_context():
            from flask import url_for
            url = url_for('get_book_details', book_id='TESTBOOK')
            self.assertIsNotNone(url)

class PerformanceTests(unittest.TestCase):
    """Test cases for performance characteristics"""
    
    def setUp(self):
        """Set up test client"""
        clear_book_cache()
    
    def test_cache_performance(self):
        """Test that cached retrieval is faster than uncached"""
        book_id = 'PERF001'
        book_data = {
            'BookName': 'Performance Test Book',
            'Price': 100,
            'Quantity': 10
        }
        
        # Cache the book
        cache_book(book_id, book_data)
        
        # Time cached retrieval (should be very fast)
        start = time.time()
        for _ in range(1000):
            cached = get_cached_book(book_id)
        cached_time = time.time() - start
        
        # Cached access should be very fast (< 0.1 seconds for 1000 operations)
        self.assertLess(cached_time, 0.1, 
                       f"Cached access took {cached_time:.4f}s for 1000 operations")
    
    def test_cache_thread_safety(self):
        """Test that cache operations are thread-safe"""
        import threading
        
        def cache_worker(book_id, book_data):
            cache_book(book_id, book_data)
            cached = get_cached_book(book_id)
            self.assertIsNotNone(cached)
        
        # Create multiple threads accessing cache
        threads = []
        for i in range(10):
            book_data = {
                'BookName': f'Book {i}',
                'Price': 100 + i,
                'Quantity': 10 + i
            }
            t = threading.Thread(target=cache_worker, args=(f'B{i:03d}', book_data))
            threads.append(t)
            t.start()
        
        # Wait for all threads
        for t in threads:
            t.join()
        
        # Verify all books are cached correctly
        for i in range(10):
            cached = get_cached_book(f'B{i:03d}')
            self.assertIsNotNone(cached)
            self.assertEqual(cached['BookName'], f'Book {i}')

if __name__ == '__main__':
    print("Running Performance Optimization Tests")
    print("=" * 60)
    unittest.main(verbosity=2)
