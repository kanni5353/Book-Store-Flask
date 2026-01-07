from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from mysql.connector import Error, pooling
from config import Config
import sys
import os
import time
import logging
from logging.handlers import RotatingFileHandler
from urllib.parse import urlparse
from datetime import datetime, timedelta
import random
import threading

# Initialize Flask app
app = Flask(__name__)

# Load configuration based on environment
env = os.getenv('FLASK_ENV', 'development')
if env == 'production':
    app.config.from_object('config.ProductionConfig')
else:
    app.config.from_object('config.DevelopmentConfig')

# Configure logging
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/bookstore.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Book Store Management System startup')

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(username):
    """Load user by username for Flask-Login"""
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT username FROM signup WHERE username = %s", (username,))
            user_data = cursor.fetchone()
            cursor.close()
            conn.close()
            if user_data:
                return User(user_data['username'])
    except Error as e:
        app.logger.error(f"Error loading user: {e}")
    return None

def parse_database_url(url):
    """Parse DATABASE_URL for cloud deployments"""
    if url:
        parsed = urlparse(url)
        return {
            'host': parsed.hostname,
            'user': parsed.username,
            'password': parsed.password,
            'database': parsed.path[1:],  # Remove leading slash
            'port': parsed.port or 3306
        }
    return None

# Global connection pool (singleton pattern)
_connection_pool = None
_pool_lock = threading.Lock()

def get_connection_pool():
    """Get or create connection pool (singleton pattern)"""
    global _connection_pool
    
    if _connection_pool is None:
        with _pool_lock:
            if _connection_pool is None:  # Double-check locking
                try:
                    db_config = None
                    if app.config.get('DATABASE_URL'):
                        db_config = parse_database_url(app.config['DATABASE_URL'])
                    else:
                        db_config = {
                            'host': app.config['DB_HOST'],
                            'user': app.config['DB_USER'],
                            'password': app.config['DB_PASSWORD'],
                            'database': app.config['DB_NAME']
                        }
                    
                    # Create connection pool with configurable pool size
                    try:
                        pool_size = int(os.getenv('DB_POOL_SIZE', '10'))
                        if pool_size < 1 or pool_size > 100:
                            app.logger.warning(f"Invalid DB_POOL_SIZE {pool_size}, using default 10")
                            pool_size = 10
                    except (ValueError, TypeError):
                        app.logger.warning("DB_POOL_SIZE must be a number, using default 10")
                        pool_size = 10
                    
                    _connection_pool = pooling.MySQLConnectionPool(
                        pool_name="bookstore_pool",
                        pool_size=pool_size,
                        pool_reset_session=True,
                        **db_config,
                        connect_timeout=10,
                        autocommit=False
                    )
                    app.logger.info(f"MySQL connection pool created successfully with size {pool_size}")
                except Exception as e:
                    app.logger.error(f"Failed to create connection pool: {e}")
                    app.logger.error("Please check your database configuration (host, user, password, database name)")
                    # Don't set _connection_pool, let it remain None so get_db_connection can handle it
                    raise
    
    return _connection_pool

# Cache for book details (expires after 5 minutes)
_book_cache = {}
_cache_lock_book = threading.Lock()
CACHE_DURATION = timedelta(minutes=5)

def get_cached_book(book_id):
    """Get book from cache if available and not expired"""
    with _cache_lock_book:
        if book_id in _book_cache:
            book, timestamp = _book_cache[book_id]
            if datetime.now() - timestamp < CACHE_DURATION:
                return book
            else:
                # Cache expired, remove it
                del _book_cache[book_id]
    return None

def cache_book(book_id, book_data):
    """Store book in cache"""
    with _cache_lock_book:
        _book_cache[book_id] = (book_data, datetime.now())

def clear_book_cache():
    """Clear all cached books (call when stock is updated)"""
    with _cache_lock_book:
        _book_cache.clear()

# Database connection function with retry logic
def get_db_connection(retries=3):
    """Get a connection from the pool with retry logic"""
    pool = get_connection_pool()
    
    for attempt in range(retries):
        try:
            connection = pool.get_connection()
            return connection
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(0.5)  # Short delay before retry
                continue
            else:
                app.logger.error(f"Failed to get connection from pool: {e}")
                return None

def create_database():
    """Create database if it doesn't exist"""
    try:
        db_config = None
        db_name = None
        
        if app.config.get('DATABASE_URL'):
            parsed = parse_database_url(app.config['DATABASE_URL'])
            db_name = parsed['database']
            db_config = {
                'host': parsed['host'],
                'user': parsed['user'],
                'password': parsed['password'],
                'port': parsed.get('port', 3306)
            }
        else:
            db_name = app.config['DB_NAME']
            db_config = {
                'host': app.config['DB_HOST'],
                'user': app.config['DB_USER'],
                'password': app.config['DB_PASSWORD']
            }
        
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        cursor.close()
        connection.close()
        print(f"Database '{db_name}' created or already exists.")
    except Error as e:
        print(f"Error creating database: {e}")
        sys.exit(1)

def init_db():
    """Initialize database tables"""
    create_database()
    
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database. Please check your configuration.")
        sys.exit(1)
    
    cursor = conn.cursor()
    
    try:
        # Create signup table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS signup (
                username VARCHAR(20) PRIMARY KEY,
                password VARCHAR(255) NOT NULL
            )
        """)
        
        # Create Available_Books table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Available_Books (
                Bookid VARCHAR(10) PRIMARY KEY,
                BookName VARCHAR(30) NOT NULL,
                Genre VARCHAR(20),
                Quantity INT NOT NULL DEFAULT 0,
                Author VARCHAR(20),
                Publication VARCHAR(30),
                Price INT NOT NULL
            )
        """)
        
        # Create Sales table with transaction_id
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Sales (
                id INT AUTO_INCREMENT PRIMARY KEY,
                transaction_id VARCHAR(50) NOT NULL,
                CustomerName VARCHAR(20) NOT NULL,
                PhoneNumber CHAR(10) NOT NULL,
                Bookid VARCHAR(10),
                BookName VARCHAR(30),
                Quantity INT NOT NULL,
                Price INT NOT NULL,
                SaleDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (Bookid) REFERENCES Available_Books(Bookid) ON DELETE SET NULL,
                INDEX idx_transaction (transaction_id)
            )
        """)
        
        # Check if transaction_id column exists in existing Sales table
        cursor.execute("SHOW COLUMNS FROM Sales LIKE 'transaction_id'")
        result = cursor.fetchone()
        
        # If transaction_id doesn't exist, add it
        if not result:
            print("Adding transaction_id column to Sales table...")
            cursor.execute("""
                ALTER TABLE Sales 
                ADD COLUMN transaction_id VARCHAR(50) NOT NULL DEFAULT '' AFTER id
            """)
            
            # Add index for transaction_id
            cursor.execute("""
                ALTER TABLE Sales 
                ADD INDEX idx_transaction (transaction_id)
            """)
            
            # Update existing records with legacy transaction IDs
            cursor.execute("""
                UPDATE Sales 
                SET transaction_id = CONCAT('TXN-LEGACY-', LPAD(id, 6, '0'))
                WHERE transaction_id = '' OR transaction_id IS NULL
            """)
            print("Transaction ID column added successfully.")
        
        conn.commit()
        print("Database tables initialized successfully.")
        
    except Error as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()

# Routes

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint for deployment monitoring"""
    try:
        conn = get_db_connection()
        if conn:
            conn.close()
            return jsonify({'status': 'healthy', 'database': 'connected'}), 200
        else:
            return jsonify({'status': 'unhealthy', 'database': 'disconnected'}), 503
    except Exception as e:
        app.logger.error(f"Health check failed: {e}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 503

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        # Validation
        if not username or not password:
            flash('Username and password are required.', 'error')
            return render_template('signup.html')
        
        if len(username) > 20:
            flash('Username must be 20 characters or less.', 'error')
            return render_template('signup.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('signup.html')
        
        # Hash password
        hashed_password = generate_password_hash(password)
        
        # Insert into database
        conn = get_db_connection()
        if not conn:
            flash('Database connection error. Please try again.', 'error')
            return render_template('signup.html')
        
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO signup (username, password) VALUES (%s, %s)", 
                         (username, hashed_password))
            conn.commit()
            cursor.close()
            conn.close()
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        except Error as e:
            if 'Duplicate entry' in str(e):
                flash('Username already exists. Please choose another.', 'error')
            else:
                flash('An error occurred. Please try again.', 'error')
            return render_template('signup.html')
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            flash('Username and password are required.', 'error')
            return render_template('login.html')
        
        conn = get_db_connection()
        if not conn:
            flash('Database connection error. Please try again.', 'error')
            return render_template('login.html')
        
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM signup WHERE username = %s", (username,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if user and check_password_hash(user['password'], password):
                user_obj = User(username)
                login_user(user_obj)
                flash(f'Welcome back, {username}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password.', 'error')
                return render_template('login.html')
        except Error as e:
            flash('An error occurred. Please try again.', 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard after login"""
    conn = get_db_connection()
    stats = {
        'total_books': 0,
        'total_sales': 0,
        'low_stock': 0
    }
    
    if conn:
        try:
            cursor = conn.cursor()
            
            # Get total books count
            cursor.execute("SELECT COUNT(*) FROM Available_Books")
            stats['total_books'] = cursor.fetchone()[0]
            
            # Get total sales amount
            cursor.execute("SELECT COALESCE(SUM(Price * Quantity), 0) FROM Sales")
            stats['total_sales'] = cursor.fetchone()[0]
            
            # Get low stock count (less than 10)
            cursor.execute("SELECT COUNT(*) FROM Available_Books WHERE Quantity < 10")
            stats['low_stock'] = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
        except Error as e:
            print(f"Error fetching stats: {e}")
    
    return render_template('dashboard.html', stats=stats)

@app.route('/sell', methods=['GET', 'POST'])
@login_required
def sell():
    """Sell books interface"""
    conn = get_db_connection()
    
    if request.method == 'POST':
        customer_name = request.form.get('customer_name', '').strip()
        phone_number = request.form.get('phone_number', '').strip()
        
        # Get all book entries (multiple books)
        book_ids = request.form.getlist('book_id[]')
        quantities = request.form.getlist('quantity[]')
        
        # Validation
        if not all([customer_name, phone_number, book_ids]):
            flash('Customer details and at least one book are required.', 'error')
            return redirect(url_for('sell'))
        
        if not phone_number.isdigit() or len(phone_number) != 10:
            flash('Phone number must be exactly 10 digits.', 'error')
            return redirect(url_for('sell'))
        
        # Generate unique transaction ID
        transaction_id = f"TXN-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"
        
        if not conn:
            flash('Database connection error. Please try again.', 'error')
            return redirect(url_for('sell'))
        
        try:
            cursor = conn.cursor(dictionary=True)
            total_amount = 0
            books_to_sell = []
            
            # Filter out empty book entries and check for duplicates
            valid_book_ids = []
            valid_quantities = []
            for book_id, quantity in zip(book_ids, quantities):
                if book_id and book_id.strip() and quantity and quantity.strip():
                    book_id = book_id.strip()
                    if book_id in valid_book_ids:
                        flash(f'Duplicate book ID {book_id} detected. Each book can only be added once per transaction.', 'error')
                        cursor.close()
                        conn.close()
                        return redirect(url_for('sell'))
                    valid_book_ids.append(book_id)
                    valid_quantities.append(quantity.strip())
            
            if not valid_book_ids:
                flash('At least one book is required.', 'error')
                cursor.close()
                conn.close()
                return redirect(url_for('sell'))
            
            # Validate all books first
            for book_id, quantity in zip(valid_book_ids, valid_quantities):
                try:
                    quantity = int(quantity)
                    if quantity <= 0:
                        flash(f'Quantity for Book ID {book_id} must be greater than 0.', 'error')
                        cursor.close()
                        conn.close()
                        return redirect(url_for('sell'))
                except ValueError:
                    flash(f'Invalid quantity for Book ID {book_id}.', 'error')
                    cursor.close()
                    conn.close()
                    return redirect(url_for('sell'))
                
                # Check stock
                cursor.execute("SELECT * FROM Available_Books WHERE Bookid = %s", (book_id,))
                book = cursor.fetchone()
                
                if not book:
                    flash(f'Book ID {book_id} not found.', 'error')
                    cursor.close()
                    conn.close()
                    return redirect(url_for('sell'))
                
                if book['Quantity'] < quantity:
                    flash(f'Insufficient stock for {book["BookName"]}. Available: {book["Quantity"]}, Requested: {quantity}', 'error')
                    cursor.close()
                    conn.close()
                    return redirect(url_for('sell'))
                
                books_to_sell.append({
                    'book_id': book_id,
                    'book_name': book['BookName'],
                    'quantity': quantity,
                    'price': book['Price']
                })
                total_amount += book['Price'] * quantity
            
            # Insert all sales records with same transaction_id
            for book in books_to_sell:
                cursor.execute("""
                    INSERT INTO Sales (transaction_id, CustomerName, PhoneNumber, Bookid, BookName, Quantity, Price)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (transaction_id, customer_name, phone_number, book['book_id'], 
                      book['book_name'], book['quantity'], book['price']))
                
                # Update stock
                cursor.execute("""
                    UPDATE Available_Books 
                    SET Quantity = Quantity - %s 
                    WHERE Bookid = %s
                """, (book['quantity'], book['book_id']))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            # Clear cache after sale
            clear_book_cache()
            
            flash(f'Sale completed! Transaction ID: {transaction_id}. Total: ₹{total_amount}', 'success')
            return redirect(url_for('sell'))
            
        except Exception as e:
            flash(f'Error processing sale: {str(e)}', 'error')
            if conn:
                conn.rollback()
                conn.close()
            return redirect(url_for('sell'))
    
    # GET request - display form with available books
    books = []
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Available_Books WHERE Quantity > 0 ORDER BY Genre, BookName")
            books = cursor.fetchall()
            cursor.close()
            conn.close()
        except Error as e:
            flash(f'Error fetching books: {str(e)}', 'error')
    
    return render_template('sell.html', books=books)

@app.route('/stock')
@login_required
def stock():
    """View all books in stock"""
    conn = get_db_connection()
    books = []
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Available_Books ORDER BY Genre, BookName")
            books = cursor.fetchall()
            cursor.close()
            conn.close()
        except Error as e:
            flash(f'Error fetching stock: {str(e)}', 'error')
    
    return render_template('stock.html', books=books)

@app.route('/stock/add', methods=['GET', 'POST'])
@login_required
def add_book():
    """Add new book to inventory"""
    if request.method == 'POST':
        book_id = request.form.get('book_id', '').strip()
        book_name = request.form.get('book_name', '').strip()
        genre = request.form.get('genre', '').strip()
        author = request.form.get('author', '').strip()
        publication = request.form.get('publication', '').strip()
        quantity = request.form.get('quantity', '').strip()
        price = request.form.get('price', '').strip()
        
        # Validation
        if not all([book_id, book_name, quantity, price]):
            flash('Book ID, Name, Quantity, and Price are required.', 'error')
            return render_template('add_book.html')
        
        try:
            quantity = int(quantity)
            price = int(price)
            if quantity < 0 or price < 0:
                flash('Quantity and Price must be non-negative.', 'error')
                return render_template('add_book.html')
        except ValueError:
            flash('Invalid quantity or price.', 'error')
            return render_template('add_book.html')
        
        conn = get_db_connection()
        if not conn:
            flash('Database connection error. Please try again.', 'error')
            return render_template('add_book.html')
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Available_Books (Bookid, BookName, Genre, Quantity, Author, Publication, Price)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (book_id, book_name, genre, quantity, author, publication, price))
            conn.commit()
            cursor.close()
            conn.close()
            
            # Clear cache after adding new book
            clear_book_cache()
            
            flash(f'Book "{book_name}" added successfully!', 'success')
            return redirect(url_for('stock'))
        except Error as e:
            if 'Duplicate entry' in str(e):
                flash(f'Book with ID {book_id} already exists.', 'error')
            else:
                flash(f'Error adding book: {str(e)}', 'error')
            return render_template('add_book.html')
    
    return render_template('add_book.html')

@app.route('/stock/update', methods=['POST'])
@login_required
def update_stock():
    """Update stock quantity (add or subtract)"""
    book_id = request.form.get('book_id', '').strip()
    action = request.form.get('action', '').strip()
    quantity = request.form.get('quantity', '').strip()
    
    # Validation
    if not all([book_id, action, quantity]):
        flash('All fields are required.', 'error')
        return redirect(url_for('stock'))
    
    if action not in ['add', 'subtract']:
        flash('Invalid action.', 'error')
        return redirect(url_for('stock'))
    
    try:
        quantity = int(quantity)
        if quantity <= 0:
            flash('Quantity must be greater than 0.', 'error')
            return redirect(url_for('stock'))
    except ValueError:
        flash('Invalid quantity.', 'error')
        return redirect(url_for('stock'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error. Please try again.', 'error')
        return redirect(url_for('stock'))
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Get current quantity
        cursor.execute("SELECT * FROM Available_Books WHERE Bookid = %s", (book_id,))
        book = cursor.fetchone()
        
        if not book:
            flash(f'Book with ID {book_id} not found.', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('stock'))
        
        # Calculate new quantity
        if action == 'add':
            new_quantity = book['Quantity'] + quantity
        else:  # subtract
            new_quantity = book['Quantity'] - quantity
            if new_quantity < 0:
                flash('Cannot subtract more than available quantity.', 'error')
                cursor.close()
                conn.close()
                return redirect(url_for('stock'))
        
        # Update quantity
        cursor.execute("UPDATE Available_Books SET Quantity = %s WHERE Bookid = %s", 
                     (new_quantity, book_id))
        conn.commit()
        cursor.close()
        conn.close()
        
        # Clear cache after stock update
        clear_book_cache()
        
        action_text = 'added to' if action == 'add' else 'subtracted from'
        flash(f'{quantity} units {action_text} "{book["BookName"]}" successfully!', 'success')
        return redirect(url_for('stock'))
        
    except Error as e:
        flash(f'Error updating stock: {str(e)}', 'error')
        if conn:
            conn.close()
        return redirect(url_for('stock'))

@app.route('/sales')
@login_required
def sales():
    """View all sales records grouped by transaction"""
    conn = get_db_connection()
    transactions = {}
    total_sales = 0
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT transaction_id, CustomerName, PhoneNumber, BookName, 
                       Quantity, Price, (Quantity * Price) as Subtotal, SaleDate
                FROM Sales 
                ORDER BY SaleDate DESC, transaction_id DESC
            """)
            sales_records = cursor.fetchall()
            
            # Group by transaction_id
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
            
            cursor.close()
            conn.close()
        except Error as e:
            flash(f'Error fetching sales: {str(e)}', 'error')
    
    return render_template('sales.html', transactions=transactions, total_sales=total_sales)

@app.route('/api/book/<book_id>')
@login_required
def get_book_details(book_id):
    """API endpoint to fetch book details for AJAX requests - OPTIMIZED"""
    
    # Check cache first
    cached_book = get_cached_book(book_id)
    if cached_book:
        return jsonify({
            'success': True,
            'book_name': cached_book['BookName'],
            'price': cached_book['Price'],
            'available_quantity': cached_book['Quantity'],
            'cached': True  # For debugging
        })
    
    # Not in cache, fetch from database
    conn = get_db_connection()
    if not conn:
        app.logger.error(f"Database connection failed for book {book_id}")
        return jsonify({
            'success': False, 
            'message': 'Database connection error. Please try again.',
            'error_type': 'connection'
        }), 503
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT BookName, Price, Quantity FROM Available_Books WHERE Bookid = %s", 
            (book_id,)
        )
        book = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if book:
            # Cache the result
            cache_book(book_id, book)
            
            return jsonify({
                'success': True,
                'book_name': book['BookName'],
                'price': book['Price'],
                'available_quantity': book['Quantity'],
                'cached': False
            })
        else:
            return jsonify({
                'success': False, 
                'message': f'Book ID {book_id} not found in inventory.',
                'error_type': 'not_found'
            }), 404
            
    except Exception as e:
        app.logger.error(f"Error fetching book {book_id}: {e}")
        return jsonify({
            'success': False, 
            'message': f'Error fetching book details: {str(e)}',
            'error_type': 'query_error'
        }), 500

@app.route('/api/books/all')
@login_required
def get_all_books():
    """Fetch all books at once for prefetching/caching"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'}), 503
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT Bookid, BookName, Price, Quantity FROM Available_Books WHERE Quantity > 0")
        books = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Cache all books
        for book in books:
            cache_book(book['Bookid'], book)
        
        return jsonify({
            'success': True,
            'books': books,
            'count': len(books)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    flash('Page not found.', 'error')
    return redirect(url_for('index'))

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    flash('An internal error occurred. Please try again later.', 'error')
    return redirect(url_for('index'))

if __name__ == '__main__':
    print("Initializing Book Store Management System...")
    if os.getenv('FLASK_ENV') != 'production':
        init_db()
    print("Starting Flask application...")
    port = int(os.getenv('PORT', 5000))
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=port)
