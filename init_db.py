#!/usr/bin/env python3
"""
Database initialization script for production deployment
Run this once after deploying to create database tables
"""

from app import app, init_db

if __name__ == '__main__':
    with app.app_context():
        print("Creating database and tables...")
        init_db()
        print("Database initialization complete!")
