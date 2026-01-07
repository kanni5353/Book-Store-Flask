from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from mysql.connector import Error
from config import Config
import sys
import os
import time
import logging
from logging.handlers import RotatingFileHandler
from urllib.parse import urlparse

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

# Database connection function with retry logic
def get_db_connection(retries=3):
    """Create and return a MySQL database connection with retry logic"""
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
    
    for attempt in range(retries):
        try:
            connection = mysql.connector.connect(
                **db_config,
                connect_timeout=10,
                autocommit=False
            )
            return connection
        except Error as e:
            if attempt < retries - 1:
                time.sleep(2)
                continue
            else:
                app.logger.error(f"Database connection failed after {retries} attempts: {e}")
                return None

def create_database():
    """Create database if it doesn't exist"""
    try:
        connection = mysql.connector.connect(
            host=app.config['DB_HOST'],
            user=app.config['DB_USER'],
            password=app.config['DB_PASSWORD']
        )
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {app.config['DB_NAME']}")
        cursor.close()
        connection.close()
        print(f"Database '{app.config['DB_NAME']}' created or already exists.")
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
        
        # Create Sales table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Sales (
                id INT AUTO_INCREMENT PRIMARY KEY,
                CustomerName VARCHAR(20) NOT NULL,
                PhoneNumber CHAR(10) NOT NULL,
                Bookid VARCHAR(10),
                BookName VARCHAR(30),
                Quantity INT NOT NULL,
                Price INT NOT NULL,
                SaleDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (Bookid) REFERENCES Available_Books(Bookid) ON DELETE SET NULL
            )
        """)
        
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
        book_id = request.form.get('book_id', '').strip()
        quantity = request.form.get('quantity', '').strip()
        
        # Validation
        if not all([customer_name, phone_number, book_id, quantity]):
            flash('All fields are required.', 'error')
            return redirect(url_for('sell'))
        
        if not phone_number.isdigit() or len(phone_number) != 10:
            flash('Phone number must be exactly 10 digits.', 'error')
            return redirect(url_for('sell'))
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                flash('Quantity must be greater than 0.', 'error')
                return redirect(url_for('sell'))
        except ValueError:
            flash('Invalid quantity.', 'error')
            return redirect(url_for('sell'))
        
        if not conn:
            flash('Database connection error. Please try again.', 'error')
            return redirect(url_for('sell'))
        
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Check if book exists and has sufficient stock
            cursor.execute("SELECT * FROM Available_Books WHERE Bookid = %s", (book_id,))
            book = cursor.fetchone()
            
            if not book:
                flash(f'Book with ID {book_id} not found.', 'error')
                cursor.close()
                conn.close()
                return redirect(url_for('sell'))
            
            if book['Quantity'] < quantity:
                flash(f'Insufficient stock. Available: {book["Quantity"]}, Requested: {quantity}', 'error')
                cursor.close()
                conn.close()
                return redirect(url_for('sell'))
            
            # Insert sale record
            cursor.execute("""
                INSERT INTO Sales (CustomerName, PhoneNumber, Bookid, BookName, Quantity, Price)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (customer_name, phone_number, book_id, book['BookName'], quantity, book['Price']))
            
            # Update book quantity
            new_quantity = book['Quantity'] - quantity
            cursor.execute("UPDATE Available_Books SET Quantity = %s WHERE Bookid = %s", 
                         (new_quantity, book_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash(f'Sale completed successfully! Total: ₹{book["Price"] * quantity}', 'success')
            return redirect(url_for('sell'))
            
        except Error as e:
            flash(f'Error processing sale: {str(e)}', 'error')
            if conn:
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
    """View all sales records"""
    conn = get_db_connection()
    sales_records = []
    total_sales = 0
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT CustomerName, PhoneNumber, BookName, Quantity, Price, 
                       (Quantity * Price) as Total, SaleDate
                FROM Sales 
                ORDER BY SaleDate DESC
            """)
            sales_records = cursor.fetchall()
            
            # Calculate total sales
            cursor.execute("SELECT COALESCE(SUM(Price * Quantity), 0) as total FROM Sales")
            total_sales = cursor.fetchone()['total']
            
            cursor.close()
            conn.close()
        except Error as e:
            flash(f'Error fetching sales: {str(e)}', 'error')
    
    return render_template('sales.html', sales=sales_records, total_sales=total_sales)

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
