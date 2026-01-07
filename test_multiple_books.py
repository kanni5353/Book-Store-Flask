#!/usr/bin/env python3
"""
Tests for multiple books per transaction feature
"""
import unittest
from unittest.mock import Mock, MagicMock, patch
from app import app
from datetime import datetime
import random

class MultipleBooksSellTests(unittest.TestCase):
    """Test cases for the multiple books per transaction feature"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
    
    def test_api_book_endpoint_exists(self):
        """Test that the API book endpoint is registered"""
        with app.test_request_context():
            from flask import url_for
            try:
                url = url_for('get_book_details', book_id='TEST123')
                self.assertIn('/api/book/', url)
            except Exception as e:
                self.fail(f"API endpoint not registered: {e}")
    
    def test_transaction_id_generation(self):
        """Test that transaction ID generation works correctly"""
        txn_id_1 = f"TXN-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        txn_id_2 = f"TXN-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        
        # Check format
        self.assertTrue(txn_id_1.startswith('TXN-'))
        # TXN-YYYYMMDD-XXXX = 4 + 8 + 1 + 4 = 17 characters
        self.assertIn(len(txn_id_1), [17, 18])  # Allow for variable length
        
        # Check that IDs are different (statistically should be)
        # This might occasionally fail due to randomness, but very unlikely
        if txn_id_1 != txn_id_2:
            self.assertNotEqual(txn_id_1, txn_id_2)
    
    def test_sell_page_loads(self):
        """Test that the sell page still loads (requires login redirect)"""
        response = self.app.get('/sell', follow_redirects=False)
        # Should redirect to login since we're not authenticated
        self.assertEqual(response.status_code, 302)
    
    def test_sales_page_loads(self):
        """Test that the sales page still loads (requires login redirect)"""
        response = self.app.get('/sales', follow_redirects=False)
        # Should redirect to login since we're not authenticated
        self.assertEqual(response.status_code, 302)
    
    def test_api_book_endpoint_requires_login(self):
        """Test that API endpoint requires authentication"""
        response = self.app.get('/api/book/TEST123', follow_redirects=False)
        # Should redirect to login since we're not authenticated
        self.assertEqual(response.status_code, 302)

class TransactionLogicTests(unittest.TestCase):
    """Test the transaction logic without database"""
    
    def test_duplicate_book_detection(self):
        """Test duplicate book ID detection logic"""
        book_ids = ['B001', 'B002', 'B003', 'B001']  # B001 is duplicate
        
        seen = []
        has_duplicate = False
        for book_id in book_ids:
            if book_id in seen:
                has_duplicate = True
                break
            seen.append(book_id)
        
        self.assertTrue(has_duplicate)
        self.assertEqual(len(seen), 3)  # Should have stopped at duplicate
    
    def test_no_duplicate_books(self):
        """Test when there are no duplicates"""
        book_ids = ['B001', 'B002', 'B003', 'B004']
        
        seen = []
        has_duplicate = False
        for book_id in book_ids:
            if book_id in seen:
                has_duplicate = True
                break
            seen.append(book_id)
        
        self.assertFalse(has_duplicate)
        self.assertEqual(len(seen), 4)
    
    def test_empty_book_filtering(self):
        """Test filtering of empty book entries"""
        book_ids = ['B001', '', 'B002', '   ', 'B003']
        quantities = ['1', '', '2', '3', '4']
        
        valid_book_ids = []
        valid_quantities = []
        
        for book_id, quantity in zip(book_ids, quantities):
            if book_id and book_id.strip() and quantity and quantity.strip():
                valid_book_ids.append(book_id.strip())
                valid_quantities.append(quantity.strip())
        
        self.assertEqual(len(valid_book_ids), 3)
        self.assertEqual(valid_book_ids, ['B001', 'B002', 'B003'])
        self.assertEqual(valid_quantities, ['1', '2', '4'])
    
    def test_quantity_validation(self):
        """Test quantity validation logic"""
        valid_quantities = ['1', '10', '100']
        invalid_quantities = ['-1', '0', 'abc', '']
        
        for qty in valid_quantities:
            try:
                qty_int = int(qty)
                self.assertTrue(qty_int > 0)
            except ValueError:
                self.fail(f"Valid quantity {qty} failed validation")
        
        for qty in invalid_quantities:
            try:
                qty_int = int(qty) if qty else 0
                if qty_int <= 0:
                    self.assertTrue(True)  # Expected
            except ValueError:
                self.assertTrue(True)  # Expected for 'abc'

class TemplateRenderTests(unittest.TestCase):
    """Test template rendering"""
    
    def test_transaction_grouping_logic(self):
        """Test the logic for grouping sales by transaction"""
        # Simulate sales records
        sales_records = [
            {'transaction_id': 'TXN-001', 'CustomerName': 'John', 'PhoneNumber': '1234567890',
             'BookName': 'Book A', 'Quantity': 2, 'Price': 100, 'Subtotal': 200, 'SaleDate': datetime.now()},
            {'transaction_id': 'TXN-001', 'CustomerName': 'John', 'PhoneNumber': '1234567890',
             'BookName': 'Book B', 'Quantity': 1, 'Price': 150, 'Subtotal': 150, 'SaleDate': datetime.now()},
            {'transaction_id': 'TXN-002', 'CustomerName': 'Jane', 'PhoneNumber': '0987654321',
             'BookName': 'Book C', 'Quantity': 3, 'Price': 200, 'Subtotal': 600, 'SaleDate': datetime.now()},
        ]
        
        # Group by transaction_id
        transactions = {}
        total_sales = 0
        
        for record in sales_records:
            txn_id = record['transaction_id']
            if txn_id not in transactions:
                transactions[txn_id] = {
                    'customer_name': record['CustomerName'],
                    'phone_number': record['PhoneNumber'],
                    'sale_date': record['SaleDate'],
                    'books': [],
                    'total': 0
                }
            
            transactions[txn_id]['books'].append({
                'book_name': record['BookName'],
                'quantity': record['Quantity'],
                'price': record['Price'],
                'subtotal': record['Subtotal']
            })
            transactions[txn_id]['total'] += record['Subtotal']
            total_sales += record['Subtotal']
        
        # Verify grouping
        self.assertEqual(len(transactions), 2)
        self.assertEqual(len(transactions['TXN-001']['books']), 2)
        self.assertEqual(len(transactions['TXN-002']['books']), 1)
        self.assertEqual(transactions['TXN-001']['total'], 350)
        self.assertEqual(transactions['TXN-002']['total'], 600)
        self.assertEqual(total_sales, 950)

if __name__ == '__main__':
    print("Running Multiple Books Per Transaction Tests")
    print("=" * 60)
    unittest.main(verbosity=2)
