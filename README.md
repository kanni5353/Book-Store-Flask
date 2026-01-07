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

### Deploy to PythonAnywhere

1. **Create a PythonAnywhere Account**
   - Visit [PythonAnywhere](https://www.pythonanywhere.com)
   - Sign up for a free account

2. **Upload Your Code**
   ```bash
   # From PythonAnywhere Bash console
   git clone https://github.com/kanni5353/Book-Store-Flask.git
   cd Book-Store-Flask
   ```

3. **Set Up Virtual Environment**
   ```bash
   mkvirtualenv --python=/usr/bin/python3.8 bookstore
   pip install -r requirements.txt
   ```

4. **Configure MySQL**
   - Create a MySQL database from the Databases tab
   - Update `.env` with PythonAnywhere database credentials

5. **Configure WSGI**
   - Edit WSGI configuration file
   - Point to your Flask app

6. **Reload the Application**

### Deploy to Heroku

1. **Install Heroku CLI**
   ```bash
   # Install from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Create Heroku App**
   ```bash
   heroku create your-bookstore-app
   ```

3. **Add MySQL Addon**
   ```bash
   heroku addons:create jawsdb:kitefin
   ```

4. **Configure Environment Variables**
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   ```

5. **Deploy**
   ```bash
   git push heroku main
   ```

### Deploy to Render

1. **Create Account** at [Render](https://render.com)

2. **Create MySQL Database**
   - Follow Render's database setup

3. **Create Web Service**
   - Connect your GitHub repository
   - Set environment variables
   - Deploy

### Deploy to Railway

1. **Create Account** at [Railway](https://railway.app)

2. **Deploy from GitHub**
   - Connect repository
   - Add MySQL plugin
   - Configure environment variables
   - Deploy automatically

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