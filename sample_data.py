#!/usr/bin/env python3
"""
Add sample book data for testing
"""
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def add_sample_books():
    """Add sample books to the database for testing"""
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'store')
        )
        
        cursor = conn.cursor()
        
        sample_books = [
            ('B001', 'Python Crash Course', 'Programming', 25, 'Eric Matthes', 'No Starch Press', 599),
            ('B002', 'Clean Code', 'Programming', 15, 'Robert Martin', 'Prentice Hall', 799),
            ('B003', 'The Pragmatic Programmer', 'Programming', 20, 'Hunt & Thomas', 'Addison-Wesley', 899),
            ('B004', 'Harry Potter', 'Fiction', 30, 'J.K. Rowling', 'Bloomsbury', 399),
            ('B005', 'The Hobbit', 'Fiction', 18, 'J.R.R. Tolkien', 'Allen & Unwin', 450),
            ('B006', 'Introduction to Algorithms', 'Programming', 12, 'CLRS', 'MIT Press', 1299),
            ('B007', 'Design Patterns', 'Programming', 10, 'Gang of Four', 'Addison-Wesley', 699),
            ('B008', '1984', 'Fiction', 22, 'George Orwell', 'Secker & Warburg', 299),
        ]
        
        added_count = 0
        for book in sample_books:
            try:
                cursor.execute("""
                    INSERT INTO Available_Books 
                    (Bookid, BookName, Genre, Quantity, Author, Publication, Price)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, book)
                added_count += 1
                print(f"Added: {book[1]}")
            except mysql.connector.Error as e:
                if 'Duplicate entry' in str(e):
                    print(f"Skipped (already exists): {book[1]}")
                else:
                    print(f"Error adding {book[1]}: {e}")
        
        conn.commit()
        cursor.close()
        conn.close()
        print(f"\nSample data script completed! Added {added_count} new books.")
        
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        print("Make sure the database exists and credentials are correct.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    print("Adding sample books to database...")
    print("-" * 50)
    add_sample_books()
