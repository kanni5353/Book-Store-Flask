# KANNI'S BOOK STORE - Flask Web Application

A complete Book Store Management System built with Flask, MySQL, and Bootstrap 5. This web application provides a modern, user-friendly interface for managing book inventory, processing sales, and tracking business performance.

![Flask](https://img.shields.io/badge/Flask-3.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3.0-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 📋 Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [Usage Guide](#usage-guide)
- [Project Structure](#project-structure)
- [Deployment](#deployment)
- [Technologies Used](#technologies-used)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)
- [Author](#author)

## ✨ Features

### User Authentication
- **Secure Signup**: Create accounts with password hashing using werkzeug
- **Login System**: Session-based authentication with Flask-Login
- **Protected Routes**: Secure access to sensitive operations

### Sales Management
- **Record Sales**: Process book sales with customer information
- **Inventory Validation**: Automatic stock checking before sales
- **Real-time Updates**: Inventory automatically updated after each sale
- **Sales History**: Complete transaction records with timestamps

### Stock Management
- **View Inventory**: Display all books with complete details
- **Add New Books**: Add books to inventory with all metadata
- **Update Stock**: Add or subtract stock quantities easily
- **Low Stock Alerts**: Visual warnings for books running low
- **Genre Organization**: Books sorted by genre for easy management

### Dashboard & Analytics
- **Statistics Overview**: Total books, total sales amount, low stock count
- **Quick Actions**: Easy access to all major features
- **Responsive Design**: Works seamlessly on desktop and mobile devices

### Security Features
- **Password Hashing**: Secure password storage with werkzeug
- **SQL Injection Prevention**: Parameterized queries throughout
- **Session Management**: Secure session handling with Flask-Login
- **Environment Variables**: Sensitive credentials stored securely

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8 or higher**
  ```bash
  python --version
  ```

- **MySQL 8.0 or higher**
  ```bash
  mysql --version
  ```

- **pip** (Python package manager)
  ```bash
  pip --version
  ```

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/kanni5353/Book-Store-Flask.git
cd Book-Store-Flask
```

### 2. Create Virtual Environment

**On Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

### 1. Set Up Environment Variables

Create a `.env` file in the project root directory:

```bash
cp .env.example .env
```

### 2. Edit the `.env` File

Open `.env` and configure your database credentials:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=store
SECRET_KEY=your-secret-key-here-change-this-in-production
```

**Important**: 
- Replace `your_mysql_password` with your actual MySQL password
- Generate a strong `SECRET_KEY` for production use
- Never commit the `.env` file to version control

## 🗄️ Database Setup

The application will automatically create the database and tables on first run. However, ensure:

1. **MySQL Server is Running**
   ```bash
   # On Linux
   sudo systemctl start mysql
   
   # On macOS (with Homebrew)
   brew services start mysql
   
   # On Windows
   # MySQL runs as a service - check Services app
   ```

2. **MySQL User Has Proper Permissions**
   ```sql
   GRANT ALL PRIVILEGES ON store.* TO 'root'@'localhost';
   FLUSH PRIVILEGES;
   ```

The application creates three tables:
- `signup` - User authentication data
- `Available_Books` - Book inventory
- `Sales` - Sales transaction records

## 🏃 Running the Application

### Development Mode

```bash
python app.py
```

The application will be available at: `http://localhost:5000`

### Production Mode

For production, use a WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 📖 Usage Guide

### 1. Create an Account

1. Navigate to `http://localhost:5000`
2. Click **Sign Up**
3. Enter a username and password
4. Click **Sign Up** to create your account

### 2. Login

1. Click **Login** on the homepage
2. Enter your credentials
3. Click **Login** to access the dashboard

### 3. Add Books to Inventory

1. From the dashboard, click **Manage Stock**
2. Click **Add New Book**
3. Fill in the book details:
   - Book ID (unique identifier)
   - Book Name
   - Genre
   - Author
   - Publication
   - Quantity
   - Price
4. Click **Add Book**

### 4. Sell Books

1. From the dashboard, click **Sell Books**
2. Enter customer information:
   - Customer Name
   - Phone Number (10 digits)
3. Select a book from the available list or enter Book ID
4. Enter quantity to sell
5. Click **Complete Sale**
6. The system will validate stock and process the sale

### 5. Manage Stock

1. Click **Manage Stock** from the dashboard
2. View all books in inventory
3. Use **+** button to add stock
4. Use **-** button to subtract stock
5. Click **Add New Book** to add more books

### 6. View Sales Records

1. Click **View Sales** from the dashboard
2. View all transaction history
3. See total sales amount at the bottom

### 7. Logout

Click **Logout** in the navigation bar to end your session

## 📁 Project Structure

```
Book-Store-Flask/
├── app.py                      # Main Flask application
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── .env.example                # Example environment variables
├── .gitignore                  # Git ignore file
├── README.md                   # This file
│
├── templates/                  # HTML templates
│   ├── base.html              # Base template with navigation
│   ├── index.html             # Home page
│   ├── signup.html            # User registration
│   ├── login.html             # User login
│   ├── dashboard.html         # Main dashboard
│   ├── sell.html              # Sell books interface
│   ├── stock.html             # Stock management
│   ├── add_book.html          # Add new book form
│   └── sales.html             # Sales records
│
└── static/                     # Static files
    ├── css/
    │   └── style.css          # Custom styles
    └── js/
        └── script.js          # JavaScript functionality
```

## 🌐 Deployment

### 📝 Pre-deployment Checklist

Before deploying to any platform, ensure you complete these steps:

- [ ] Set environment variable `FLASK_ENV=production`
- [ ] Generate a strong `SECRET_KEY` (see below)
- [ ] Configure `DATABASE_URL` or individual database credentials
- [ ] Update `.env` file with production values (never commit this file!)
- [ ] Test application locally first
- [ ] Review security settings in `config.py`
- [ ] Ensure all dependencies are in `requirements.txt`

**Generate a Strong SECRET_KEY:**
```bash
python -c 'import secrets; print(secrets.token_hex(32))'
```

---

### 🚀 Deploy to Heroku

Complete step-by-step guide for Heroku deployment:

#### 1. Install Heroku CLI

```bash
# macOS (with Homebrew)
brew tap heroku/brew && brew install heroku

# Ubuntu/Debian
curl https://cli-assets.heroku.com/install-ubuntu.sh | sh

# Windows
# Download installer from https://devcenter.heroku.com/articles/heroku-cli
```

#### 2. Login to Heroku

```bash
heroku login
```

#### 3. Create Heroku App

```bash
heroku create your-bookstore-app
# Replace 'your-bookstore-app' with your desired app name
```

#### 4. Add JawsDB MySQL Add-on (Free Tier)

```bash
heroku addons:create jawsdb:kitefin
```

#### 5. Get Database Credentials

```bash
# View the DATABASE_URL
heroku config:get JAWSDB_URL

# The app will automatically use this as DATABASE_URL
```

#### 6. Set Environment Variables

```bash
# Set Flask environment to production
heroku config:set FLASK_ENV=production

# Generate and set a strong secret key
heroku config:set SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')

# View all config
heroku config
```

#### 7. Deploy to Heroku

```bash
# Push your code
git push heroku main

# If you're on a different branch
git push heroku your-branch:main
```

#### 8. Initialize Database

```bash
# Run the database initialization script
heroku run python init_db.py

# Optionally add sample data
heroku run python sample_data.py
```

#### 9. Open Your Application

```bash
heroku open
```

#### 10. View Logs (for debugging)

```bash
# Stream logs
heroku logs --tail

# View recent logs
heroku logs --num=100
```

---

### 🚂 Deploy to Railway

Railway provides easy deployment with automatic HTTPS:

#### 1. Install Railway CLI

```bash
npm i -g @railway/cli
```

#### 2. Login to Railway

```bash
railway login
```

#### 3. Initialize Project

```bash
cd Book-Store-Flask
railway init
```

#### 4. Add MySQL Database

```bash
railway add
# Select MySQL from the list
```

#### 5. Link Database to Service

Railway automatically provides a `DATABASE_URL` environment variable. You can view it:

```bash
railway variables
```

#### 6. Set Environment Variables

Through the Railway dashboard:
- Go to your project
- Click on "Variables"
- Add:
  - `FLASK_ENV=production`
  - `SECRET_KEY=your-generated-secret-key`

Or via CLI:
```bash
railway variables set FLASK_ENV=production
railway variables set SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
```

#### 7. Deploy

```bash
railway up
```

#### 8. Initialize Database

```bash
railway run python init_db.py
railway run python sample_data.py
```

#### 9. Open Application

```bash
railway open
```

---

### 🎨 Deploy to Render

Render offers free hosting for web services:

#### 1. Create Account

Visit [render.com](https://render.com) and sign up

#### 2. Create MySQL Database

1. From Render dashboard, click **New +**
2. Select **MySQL**
3. Choose a name (e.g., `bookstore-db`)
4. Select free tier
5. Click **Create Database**
6. Copy the **Internal Database URL** from database details

#### 3. Create Web Service

1. Click **New +** → **Web Service**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `bookstore-app`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
4. Click **Create Web Service**

#### 4. Set Environment Variables

In the web service dashboard, go to **Environment**:

```
FLASK_ENV=production
SECRET_KEY=your-generated-secret-key
DATABASE_URL=internal-database-url-from-step-2
```

#### 5. Initialize Database

After deployment:
1. Go to **Shell** tab
2. Run:
```bash
python init_db.py
python sample_data.py  # Optional
```

#### 6. Access Application

Your app will be available at: `https://bookstore-app.onrender.com`

---

### 🐍 Deploy to PythonAnywhere

PythonAnywhere is great for Python web apps:

#### 1. Create Account

Visit [pythonanywhere.com](https://www.pythonanywhere.com) and sign up for free account

#### 2. Open Bash Console

From your dashboard, start a new Bash console

#### 3. Clone Repository

```bash
git clone https://github.com/kanni5353/Book-Store-Flask.git
cd Book-Store-Flask
```

#### 4. Create Virtual Environment

```bash
mkvirtualenv --python=/usr/bin/python3.10 bookstore-env
pip install -r requirements.txt
```

#### 5. Create MySQL Database

1. Go to **Databases** tab
2. Set a MySQL password if not already done
3. Create a new database (e.g., `yourusername$store`)
4. Note the hostname

#### 6. Configure Environment Variables

Create `.env` file:
```bash
nano .env
```

Add:
```env
DB_HOST=yourusername.mysql.pythonanywhere-services.com
DB_USER=yourusername
DB_PASSWORD=your-mysql-password
DB_NAME=yourusername$store
SECRET_KEY=your-generated-secret-key
FLASK_ENV=production
```

#### 7. Initialize Database

```bash
python init_db.py
python sample_data.py  # Optional
```

#### 8. Configure Web App

1. Go to **Web** tab
2. Click **Add a new web app**
3. Choose **Manual configuration** (not Flask wizard)
4. Select **Python 3.10**

#### 9. Configure WSGI File

Click on WSGI configuration file link and replace contents:

```python
import sys
import os

# Add your project directory to the sys.path
project_home = '/home/yourusername/Book-Store-Flask'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(project_home, '.env'))

# Import flask app
from app import app as application
```

#### 10. Configure Virtual Environment

In the **Web** tab:
- Enter virtualenv path: `/home/yourusername/.virtualenvs/bookstore-env`

#### 11. Configure Static Files

In **Static files** section:
- URL: `/static/`
- Directory: `/home/yourusername/Book-Store-Flask/static/`

#### 12. Reload Web App

Click the **Reload** button

Your app will be available at: `https://yourusername.pythonanywhere.com`

---

### 🐳 Deploy with Docker (Optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
```

Build and run:
```bash
docker build -t bookstore-app .
docker run -p 5000:5000 --env-file .env bookstore-app
```

---

### 🔧 Troubleshooting Deployment Issues

#### Database Connection Errors

**Problem**: "Can't connect to MySQL server"

**Solutions**:
1. Verify database credentials in environment variables
2. Check if `DATABASE_URL` is properly formatted
3. Ensure database server is running and accessible
4. Check firewall rules
5. Verify connection timeout settings

```bash
# Test database connection
python -c "from app import get_db_connection; conn = get_db_connection(); print('Connected!' if conn else 'Failed')"
```

#### Import Errors

**Problem**: "ModuleNotFoundError: No module named 'xxx'"

**Solutions**:
1. Ensure virtual environment is activated
2. Install all requirements:
```bash
pip install -r requirements.txt
```
3. Check Python version compatibility
4. Verify all dependencies are listed in `requirements.txt`

#### Static Files Not Loading

**Problem**: CSS/JS files not loading (404 errors)

**Solutions**:
1. Check static file paths in templates
2. Ensure static folder is included in deployment
3. Configure static file serving in platform settings
4. Clear browser cache
5. Check file permissions

#### Session Issues

**Problem**: Users logged out unexpectedly

**Solutions**:
1. Set strong `SECRET_KEY` that doesn't change
2. Enable `SESSION_COOKIE_SECURE` only with HTTPS
3. Check session timeout settings
4. Verify cookie settings in `config.py`

#### Health Check Failing

**Problem**: `/health` endpoint returns 503

**Solutions**:
1. Check database connection
2. Verify database credentials
3. Check application logs:
```bash
# Heroku
heroku logs --tail

# Railway
railway logs

# PythonAnywhere
Check error logs in web app configuration
```

#### Port Already in Use (Local Development)

**Problem**: "Address already in use"

**Solutions**:
```bash
# Find process using port 5000
lsof -i :5000

# Kill the process
kill -9 <PID>

# Or use a different port
export PORT=5001
python app.py
```

#### Database Tables Not Created

**Problem**: Tables don't exist

**Solutions**:
```bash
# Run initialization script
python init_db.py

# Or run app once in development mode (auto-creates tables)
FLASK_ENV=development python app.py
```

---

### 🔒 Security Best Practices

#### Essential Security Measures

1. **Never Commit Sensitive Data**
   ```bash
   # Ensure .env is in .gitignore
   echo ".env" >> .gitignore
   ```

2. **Use Strong SECRET_KEY**
   ```bash
   # Generate new key for production
   python -c 'import secrets; print(secrets.token_hex(32))'
   ```

3. **Enable HTTPS in Production**
   - Most platforms provide automatic HTTPS
   - Ensure `SESSION_COOKIE_SECURE=True` in production

4. **Keep Dependencies Updated**
   ```bash
   pip list --outdated
   pip install --upgrade package-name
   ```

5. **Regular Security Audits**
   ```bash
   # Check for known vulnerabilities
   pip install safety
   safety check
   ```

6. **Use Environment Variables**
   - Never hardcode credentials
   - Use platform-specific secrets management
   - Rotate keys regularly

7. **Database Security**
   - Use strong database passwords
   - Enable SSL for database connections
   - Limit database user permissions
   - Regular backups

8. **Monitor Application**
   - Set up logging
   - Monitor health check endpoint
   - Set up alerts for errors
   - Review logs regularly

#### Security Headers (Advanced)

Add to `app.py`:
```python
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
```

---

### 📊 Monitoring and Maintenance

#### Health Check Endpoint

The application includes a `/health` endpoint for monitoring:

```bash
curl https://your-app.com/health
```

Response:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

#### Log Monitoring

**Heroku:**
```bash
heroku logs --tail --app your-app-name
```

**Railway:**
```bash
railway logs
```

**Render:**
- View logs in dashboard under "Logs" tab

**PythonAnywhere:**
- Check error log in web app configuration

#### Database Backups

**Regular Backups:**
```bash
# Export database
mysqldump -h hostname -u username -p database_name > backup.sql

# Import database
mysql -h hostname -u username -p database_name < backup.sql
```

#### Performance Monitoring

1. Monitor response times
2. Check database query performance
3. Monitor memory usage
4. Track error rates
5. Set up uptime monitoring (e.g., UptimeRobot)

## 🛠️ Technologies Used

- **Backend Framework**: Flask 3.0.0
- **Database**: MySQL 8.0+
- **Authentication**: Flask-Login 0.6.3
- **Password Hashing**: Werkzeug 3.0.0
- **Environment Variables**: python-dotenv 1.0.0
- **Database Connector**: mysql-connector-python 8.2.0
- **Frontend Framework**: Bootstrap 5.3.0
- **Icons**: Bootstrap Icons 1.11.0
- **JavaScript**: Vanilla JS for interactivity

## 📸 Screenshots

> *Screenshots will be added here once the application is deployed*

### Home Page
![Home Page - Coming Soon]

### Dashboard
![Dashboard - Coming Soon]

### Stock Management
![Stock Management - Coming Soon]

### Sales Interface
![Sales Interface - Coming Soon]

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
5. Push to the branch (`git push origin feature/AmazingFeature`)
6. Open a Pull Request

### Contribution Guidelines

- Follow PEP 8 style guidelines for Python code
- Write clear commit messages
- Add comments for complex logic
- Test your changes thoroughly
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**kanni5353**

- GitHub: [@kanni5353](https://github.com/kanni5353)
- Project Link: [https://github.com/kanni5353/Book-Store-Flask](https://github.com/kanni5353/Book-Store-Flask)

## 🙏 Acknowledgments

- Original command-line version: [Book-Store-Management-System](https://github.com/kanni5353/Book-Store-Management-System)
- Flask documentation: [flask.palletsprojects.com](https://flask.palletsprojects.com/)
- Bootstrap documentation: [getbootstrap.com](https://getbootstrap.com/)

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/kanni5353/Book-Store-Flask/issues) page
2. Create a new issue if your problem isn't already listed
3. Provide detailed information about your environment and the issue

## 🔄 Version History

- **v1.0.0** (2024) - Initial release
  - User authentication
  - Book sales management
  - Stock management
  - Sales tracking
  - Responsive UI with Bootstrap 5

---

<p align="center">Made with ❤️ by kanni5353</p>
<p align="center">KANNI'S BOOK STORE © 2024</p>