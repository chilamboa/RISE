# generate_data.py
# Version: 2025.07.08.57 - Added explicit column rename to 'schoolid' after reading schools_df from DB
#                          to ensure consistent lowercase column name and resolve KeyError.

import re  # Import re module for regular expressions

print(
    "--- generate_data.py script started/reloaded - Version: 2025.07.08.57 ---"
)  # Updated: Prominent version indicator

from flask import Flask, render_template, request, jsonify
import pandas as pd
from sqlalchemy import create_engine, text
import sys
import io
import threading
import time
import uuid
import string
import numpy as np
import random
from datetime import datetime, timedelta
import calendar
import os  # Import the os module
import traceback  # New: Import traceback for detailed error logging
import logging  # New: Import logging module
import psutil  # For memory usage monitoring

# Suppress Werkzeug (Flask's development server) access logs
# This will prevent messages like "127.0.0.1 - - [date time] \"GET /api/get_status HTTP/1.1\" 200 -"
log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)  # Set to ERROR or CRITICAL to suppress most messages

# New imports for prediction models and evaluation
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    classification_report,
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)
from sklearn.model_selection import train_test_split
import joblib  # For saving/loading models


# --- Global Application State (Singleton Pattern) ---
# This class manages the shared state of the application,
# including database connection, data readiness, model status,
# and console output. It ensures only one instance exists.
class AppState:
    _instance = None
    _lock = threading.Lock()  # For thread-safe singleton initialization

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                # Double-checked locking to prevent race conditions
                if not cls._instance:
                    cls._instance = super(AppState, cls).__new__(cls)
                    cls._instance._initialized = (
                        False  # Flag to ensure one-time initialization
                    )
        return cls._instance

    def __init__(self):
        if self._initialized:
            return  # Already initialized

        self.db_engine = None
        self.db_connected = False
        self.dataset_ready = False
        self.model_trained = False
        self.model = None
        self.model_metrics = {}
        self.console_output_buffer = io.StringIO()  # In-memory buffer for console logs
        self.response_queue = []  # Queue for async task responses to send to frontend
        self.error_count = 0
        self.last_error = None
        self.app_version = "2025.07.08.57"  # Centralized version
        self._initialized = True  # Mark as initialized

        # Set up a custom logger to capture print statements and log messages
        self._setup_logging()
        self.log_info(f"Application State Initialized. Version: {self.app_version}")

        # Start a background thread for database connection if not already connected
        # This prevents blocking the main Flask thread on startup
        if not self.db_connected:
            self.log_info("Attempting to connect to database in background...")
            threading.Thread(target=self.connect_db_background).start()

    def _setup_logging(self):
        # Remove default handlers to prevent duplicate messages
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        # Set up basic logging to capture everything
        logging.basicConfig(
            level=logging.INFO,
            stream=self.console_output_buffer,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )

        # Also add a stream handler to stdout for real-time console visibility
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        console_handler.setFormatter(formatter)
        logging.getLogger().addHandler(console_handler)

    def log_message(self, message, level="info"):
        # Use the logging module to write to the buffer and stdout
        if level == "info":
            logging.info(message)
        elif level == "warning":
            logging.warning(message)
        elif level == "error":
            logging.error(message)
        elif level == "debug":
            logging.debug(message)

    def log_info(self, message):
        self.log_message(message, "info")

    def log_warning(self, message):
        self.log_message(message, "warning")

    def log_error(self, message, exc_info=True):
        self.log_message(message, "error")  # exc_info=True will log traceback

    def log_debug(self, message):
        self.log_message(message, "debug")

    def connect_db_background(self):
        try:
            # Using a SQLite in-memory database for simplicity and portability
            # For persistent storage, change to a file path: 'sqlite:///./test.db'
            # Changed from in-memory to a file-based SQLite database
            self.db_engine = create_engine("sqlite:///student_marks.db")
            self.db_connected = True
            self.log_info("Database connected successfully.")
            self.queue_response("Database connected successfully.", "success")
            # Automatically create tables if connected
            self.create_tables()
        except Exception as e:
            self.db_connected = False
            self.log_error(f"Failed to connect to database: {e}")
            self.queue_response(f"Failed to connect to database: {e}", "error")

    def disconnect_db(self):
        if self.db_engine:
            self.db_engine.dispose()
            self.db_engine = None
        self.db_connected = False
        self.dataset_ready = False
        self.model_trained = False
        self.model = None
        self.model_metrics = {}
        self.log_info("Database disconnected.")
        self.queue_response("Database disconnected.", "success")

    def create_tables(self):
        if not self.db_connected:
            self.log_error("Cannot create tables: Database not connected.")
            self.queue_response(
                "Cannot create tables: Database not connected.", "error"
            )
            return

        self.log_info("Creating database schema and lookup tables...")
        try:
            with self.db_engine.connect() as connection:
                # Define table creation SQL commands
                table_creation_commands = [
                    """
                    CREATE TABLE IF NOT EXISTS schools (
                        school_id VARCHAR(50) PRIMARY KEY,
                        school_name NVARCHAR(255),
                        school_type NVARCHAR(50),
                        province NVARCHAR(50),
                        district NVARCHAR(50),
                        quintile INT
                    );
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS parents (
                        parent_id VARCHAR(50) PRIMARY KEY,
                        first_name NVARCHAR(100),
                        last_name NVARCHAR(100),
                        contact_number NVARCHAR(20),
                        email NVARCHAR(255)
                    );
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS students (
                        student_id VARCHAR(50) PRIMARY KEY,
                        first_name NVARCHAR(100),
                        last_name NVARCHAR(100),
                        date_of_birth DATE,
                        gender NVARCHAR(10),
                        grade_level INT,
                        school_id VARCHAR(50),
                        parent_id VARCHAR(50),
                        enrollment_date DATE,
                        FOREIGN KEY (school_id) REFERENCES schools(school_id),
                        FOREIGN KEY (parent_id) REFERENCES parents(parent_id)
                    );
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS academic_records (
                        record_id VARCHAR(50) PRIMARY KEY,
                        student_id VARCHAR(50),
                        subject_name NVARCHAR(100),
                        assessment_type NVARCHAR(50),
                        mark DECIMAL(5, 2),
                        assessment_date DATE,
                        academic_year INT,
                        FOREIGN KEY (student_id) REFERENCES students(student_id)
                    );
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS attendance_records (
                        attendance_id VARCHAR(50) PRIMARY KEY,
                        student_id VARCHAR(50),
                        record_date DATE,
                        status NVARCHAR(50), -- Present, Absent, Late
                        reason NVARCHAR(255),
                        FOREIGN KEY (student_id) REFERENCES students(student_id)
                    );
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS student_years (
                        student_year_id VARCHAR(50) PRIMARY KEY,
                        student_id VARCHAR(50),
                        academic_year INT,
                        grade_level INT,
                        final_mark DECIMAL(5, 2),
                        dropout_risk DECIMAL(5, 2),
                        socio_economic_score DECIMAL(5, 2),
                        home_environment_score DECIMAL(5, 2),
                        internet_access_score DECIMAL(5, 2),
                        study_habits_score DECIMAL(5, 2),
                        extracurricular_engagement_score DECIMAL(5, 2),
                        health_nutrition_score DECIMAL(5, 2),
                        special_needs_support_score DECIMAL(5, 2),
                        FOREIGN KEY (student_id) REFERENCES students(student_id)
                    );
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS intervention_recommendations (
                        recommendation_id VARCHAR(50) PRIMARY KEY,
                        student_id VARCHAR(50),
                        intervention_type NVARCHAR(100),
                        recommendation_date DATE,
                        effectiveness_score DECIMAL(5, 2),
                        cost DECIMAL(10, 2),
                        FOREIGN KEY (student_id) REFERENCES students(student_id)
                    );
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS chatbot_knowledge_base (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category NVARCHAR(100),
                        question_keywords NVARCHAR(255),
                        answer TEXT,
                        confidence_threshold DECIMAL(3, 2)
                    );
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        user_id VARCHAR(50) PRIMARY KEY,
                        username NVARCHAR(50) UNIQUE NOT NULL,
                        password_hash NVARCHAR(255) NOT NULL,
                        role NVARCHAR(50) NOT NULL -- e.g., 'admin', 'teacher', 'parent'
                    );
                    """,
                    # Lookup tables
                    """
                    CREATE TABLE IF NOT EXISTS gender_lookup (id INT PRIMARY KEY, name NVARCHAR(50));
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS school_type_lookup (id INT PRIMARY KEY, name NVARCHAR(50));
                    """,
                    # Corrected: Split DROP TABLE and CREATE TABLE for province_lookup into two separate strings
                    """
                    DROP TABLE IF EXISTS province_lookup;
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS province_lookup (id INT PRIMARY KEY, province_name NVARCHAR(50));
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS district_lookup (id INT PRIMARY KEY, name NVARCHAR(50));
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS quintile_lookup (id INT PRIMARY KEY, name NVARCHAR(50));
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS subject_lookup (id INT PRIMARY KEY, name NVARCHAR(100));
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS academic_assessment_type_lookup (id INT PRIMARY KEY, name NVARCHAR(50));
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS attendance_status_lookup (id INT PRIMARY KEY, name NVARCHAR(50));
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS socio_economic_status_lookup (id INT PRIMARY KEY, name NVARCHAR(50));
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS home_environment_lookup (id INT PRIMARY KEY, name NVARCHAR(50));
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS internet_access_lookup (id INT PRIMARY KEY, name NVARCHAR(50));
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS study_habits_lookup (id INT PRIMARY KEY, name NVARCHAR(50));
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS extracurricular_engagement_lookup (id INT PRIMARY KEY, name NVARCHAR(50));
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS health_nutrition_lookup (id INT PRIMARY KEY, name NVARCHAR(50));
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS special_needs_support_lookup (id INT PRIMARY KEY, name NVARCHAR(50));
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS intervention_type_lookup (
                        id INT PRIMARY KEY,
                        name NVARCHAR(100),
                        description TEXT,
                        potential_impact_score DECIMAL(5, 2),
                        cost DECIMAL(10, 2)
                    );
                    """,
                ]

                # Execute table creation commands
                for command in table_creation_commands:
                    connection.execute(text(command))
                connection.commit()
            self.log_info("Database schema created successfully.")
            self.queue_response("Database schema created successfully.", "success")

            # Populate lookup tables
            self._populate_lookup_tables()

            # Populate initial chatbot knowledge base
            self._populate_chatbot_knowledge_base()

            # Add a default admin user if not exists
            self._add_default_admin_user()

        except Exception as e:
            self.log_error(
                f"Error creating tables or populating lookups: {e}", exc_info=True
            )
            self.queue_response(
                f"Error creating tables or populating lookups: {e}", "error"
            )

    def _populate_lookup_tables(self):
        self.log_info("Populating lookup tables...")
        try:
            with self.db_engine.connect() as connection:
                # Gender
                connection.execute(
                    text(
                        "INSERT OR IGNORE INTO gender_lookup (id, name) VALUES (0, 'Male');"
                    )
                )
                connection.execute(
                    text(
                        "INSERT OR IGNORE INTO gender_lookup (id, name) VALUES (1, 'Female');"
                    )
                )

                # School Type
                connection.execute(
                    text(
                        "INSERT OR IGNORE INTO school_type_lookup (id, name) VALUES (1, 'Primary');"
                    )
                )
                connection.execute(
                    text(
                        "INSERT OR IGNORE INTO school_type_lookup (id, name) VALUES (2, 'Secondary');"
                    )
                )
                connection.execute(
                    text(
                        "INSERT OR IGNORE INTO school_type_lookup (id, name) VALUES (3, 'Combined');"
                    )
                )

                # Province
                provinces = [
                    "Gauteng",
                    "Western Cape",
                    "KwaZulu-Natal",
                    "Eastern Cape",
                    "Limpopo",
                    "Mpumalanga",
                    "North West",
                    "Northern Cape",
                    "Free State",
                ]
                for i, p in enumerate(provinces):
                    # Changed column name to 'province_name'
                    connection.execute(
                        text(
                            f"INSERT OR IGNORE INTO province_lookup (id, province_name) VALUES ({i+1}, '{p}');"
                        )
                    )

                # District (Example for Gauteng)
                districts = [
                    "Johannesburg",
                    "Tshwane",
                    "Ekurhuleni",
                    "Sedibeng",
                    "West Rand",
                ]
                for i, d in enumerate(districts):
                    connection.execute(
                        text(
                            f"INSERT OR IGNORE INTO district_lookup (id, name) VALUES ({i+1}, '{d}');"
                        )
                    )

                # Quintile
                for i in range(1, 6):
                    connection.execute(
                        text(
                            f"INSERT OR IGNORE INTO quintile_lookup (id, name) VALUES ({i}, 'Quintile {i}');"
                        )
                    )

                # Subject
                subjects = [
                    "Mathematics",
                    "English",
                    "Life Sciences",
                    "Physical Sciences",
                    "History",
                    "Geography",
                    "Afrikaans",
                    "IsiZulu",
                ]
                for i, s in enumerate(subjects):
                    connection.execute(
                        text(
                            f"INSERT OR IGNORE INTO subject_lookup (id, name) VALUES ({i+1}, '{s}');"
                        )
                    )

                # Academic Assessment Type
                connection.execute(
                    text(
                        "INSERT OR IGNORE INTO academic_assessment_type_lookup (id, name) VALUES (1, 'Test');"
                    )
                )
                connection.execute(
                    text(
                        "INSERT OR IGNORE INTO academic_assessment_type_lookup (id, name) VALUES (2, 'Assignment');"
                    )
                )
                connection.execute(
                    text(
                        "INSERT OR IGNORE INTO academic_assessment_type_lookup (id, name) VALUES (3, 'Exam');"
                    )
                )

                # Attendance Status
                connection.execute(
                    text(
                        "INSERT OR IGNORE INTO attendance_status_lookup (id, name) VALUES (1, 'Present');"
                    )
                )
                connection.execute(
                    text(
                        "INSERT OR IGNORE INTO attendance_status_lookup (id, name) VALUES (2, 'Absent');"
                    )
                )
                connection.execute(
                    text(
                        "INSERT OR IGNORE INTO attendance_status_lookup (id, name) VALUES (3, 'Late');"
                    )
                )

                # Socio-Economic Status
                connection.execute(
                    text(
                        "INSERT OR IGNORE INTO socio_economic_status_lookup (id, name) VALUES (1, 'Low');"
                    )
                )
                connection.execute(
                    text(
                        "INSERT OR IGNORE INTO socio_economic_status_lookup (id, name) VALUES (2, 'Medium');"
                    )
                )
                connection.execute(
                    text(
                        "INSERT OR IGNORE INTO socio_economic_status_lookup (id, name) VALUES (3, 'High');"
                    )
                )

                # Home Environment
                connection.execute(
                    text(
                        "INSERT OR IGNORE INTO home_environment_lookup (id, name) VALUES (1, 'Supportive');"
                    )
                )
                connection.execute(
                    text(
                        "INSERT OR IGNORE INTO home_environment_lookup (id, name) VALUES (2, 'Neutral');"
                    )
                )
                connection.execute(
                    text(
                        "INSERT OR IGNORE INTO home_environment_lookup (id, name) VALUES (3, 'Challenging');"
                    )
                )

                # Internet Access
                connection.execute(
                    text(
                        "INSERT OR IGNORE INTO internet_access_lookup (id, name) VALUES (1, 'No Access');"
                    )
                )
                connection.execute(
                    text(
                        "INSERT OR IGNORE INTO internet_access_lookup (id, name) VALUES (2, 'Limited Access');"
                    )
                )
                connection.execute(
                    text(
                        "INSERT OR IGNORE INTO internet_access_lookup (id, name) VALUES (3, 'Reliable Access');"
                    )
                )

                # Study Habits
                connection.execute(
                    text(
                        "INSERT OR IGNORE INTO study_habits_lookup (id, name) VALUES (1, 'Poor');"
                    )
                )
                connection.execute(
                    text(
                        "INSERT OR IGNORE INTO study_habits_lookup (id, name) VALUES (2, 'Average');"
                    )
                )
                connection.execute(
                    text(
                        "INSERT OR IGNORE INTO study_habits_lookup (id, name) VALUES (3, 'Excellent');"
                    )
                )

                # Extracurricular Engagement
                connection.execute(
                    text(
                        "INSERT OR IGNORE INTO extracurricular_engagement_lookup (id, name) VALUES (1, 'None');"
                    )
                )
                connection.execute(
                    text(
                        "INSERT OR IGNORE INTO extracurricular_engagement_lookup (id, name) VALUES (2, 'Low');"
                    )
                )
                connection.execute(
                    text(
                        "INSERT OR IGNORE INTO extracurricular_engagement_lookup (id, name) VALUES (3, 'Medium');"
                    )
                )
                connection.execute(
                    text(
                        "INSERT OR IGNORE INTO extracurricular_engagement_lookup (id, name) VALUES (4, 'High');"
                    )
                )

                # Health & Nutrition
                connection.execute(
                    text(
                        "INSERT OR IGNORE INTO health_nutrition_lookup (id, name) VALUES (1, 'Poor');"
                    )
                )
                connection.execute(
                    text(
                        "INSERT OR IGNORE INTO health_nutrition_lookup (id, name) VALUES (2, 'Average');"
                    )
                )
                connection.execute(
                    text(
                        "INSERT OR IGNORE INTO health_nutrition_lookup (id, name) VALUES (3, 'Good');"
                    )
                )

                # Special Needs Support
                connection.execute(
                    text(
                        "INSERT OR IGNORE INTO special_needs_support_lookup (id, name) VALUES (1, 'No Support');"
                    )
                )
                connection.execute(
                    text(
                        "INSERT OR IGNORE INTO special_needs_support_lookup (id, name) VALUES (2, 'Partial Support');"
                    )
                )
                connection.execute(
                    text(
                        "INSERT OR IGNORE INTO special_needs_support_lookup (id, name) VALUES (3, 'Full Support');"
                    )
                )

                # Intervention Type
                connection.execute(
                    text(
                        "INSERT OR IGNORE INTO intervention_type_lookup (id, name, description, potential_impact_score, cost) VALUES (1, 'Tutoring', 'One-on-one academic support', 7.5, 500.00);"
                    )
                )
                connection.execute(
                    text(
                        "INSERT OR IGNORE INTO intervention_type_lookup (id, name, description, potential_impact_score, cost) VALUES (2, 'Counseling', 'Emotional and psychological support', 6.0, 300.00);"
                    )
                )
                connection.execute(
                    text(
                        "INSERT OR IGNORE INTO intervention_type_lookup (id, name, description, potential_impact_score, cost) VALUES (3, 'Mentorship Program', 'Guidance from an experienced mentor', 8.0, 200.00);"
                    )
                )
                connection.execute(
                    text(
                        "INSERT OR IGNORE INTO intervention_type_lookup (id, name, description, potential_impact_score, cost) VALUES (4, 'After-school Program', 'Structured academic and recreational activities', 6.5, 150.00);"
                    )
                )
                connection.execute(
                    text(
                        "INSERT OR IGNORE INTO intervention_type_lookup (id, name, description, potential_impact_score, cost) VALUES (5, 'Parental Engagement Workshop', 'Workshops to involve parents in student education', 7.0, 100.00);"
                    )
                )

                connection.commit()
            self.log_info("Lookup tables populated successfully.")
        except Exception as e:
            self.log_error(f"Error populating lookup tables: {e}", exc_info=True)
            self.queue_response(f"Error populating lookup tables: {e}", "error")

    def _populate_chatbot_knowledge_base(self):
        self.log_info("Populating chatbot knowledge base...")
        try:
            with self.db_engine.connect() as connection:
                # Clear existing entries to prevent duplicates on re-run
                connection.execute(text("DELETE FROM chatbot_knowledge_base;"))

                # Insert initial knowledge entries
                knowledge_entries = [
                    (
                        "Greeting",
                        "hi,hello,hey",
                        "Hi there! I'm Naledi, your AI assistant. How can I help you today?",
                        0.8,
                    ),
                    (
                        "Grades",
                        "grades,marks,results,academic performance",
                        "You can check your grades on the 'Academic Records' section of your student profile.",
                        0.7,
                    ),
                    (
                        "Attendance",
                        "attendance,absent,present,late",
                        "Your attendance records are available in the 'Attendance' section of your student profile.",
                        0.7,
                    ),
                    (
                        "Support Options",
                        "support,help,assistance,intervention",
                        "We offer various support options including tutoring, counseling, and mentorship programs. You can find more details under 'Interventions Management'.",
                        0.75,
                    ),
                    (
                        "Contact",
                        "contact,reach out,talk to,speak to",
                        "For further assistance, please contact your school administrator or teacher.",
                        0.6,
                    ),
                    (
                        "About RISE",
                        "about,what is rise,platform,purpose",
                        "RISE is a predictive analytics platform designed to forecast student academic performance and recommend interventions.",
                        0.85,
                    ),
                    (
                        "Login Issues",
                        "login,access,cannot log in,password",
                        "If you're having trouble logging in, please ensure your username and password are correct. You can also contact your school's IT support.",
                        0.65,
                    ),
                    (
                        "Data Privacy",
                        "privacy,data,security,confidentiality",
                        "We are committed to protecting your data privacy. Please refer to our Privacy Policy for detailed information on how we handle your data.",
                        0.8,
                    ),
                    (
                        "Features",
                        "features,what can you do,capabilities",
                        "I can help you with academic performance predictions, intervention recommendations, and provide insights into student data.",
                        0.7,
                    ),
                    (
                        "Feedback",
                        "feedback,suggestion,improve",
                        "We appreciate your feedback! Please use the 'Contact Us' section to send us your suggestions.",
                        0.6,
                    ),
                ]

                for entry in knowledge_entries:
                    connection.execute(
                        text(
                            "INSERT INTO chatbot_knowledge_base (category, question_keywords, answer, confidence_threshold) VALUES (:category, :keywords, :answer, :threshold)"
                        ),
                        {
                            "category": entry[0],
                            "keywords": entry[1],
                            "answer": entry[2],
                            "threshold": entry[3],
                        },
                    )
                connection.commit()
            self.log_info("Chatbot knowledge base populated successfully.")
        except Exception as e:
            self.log_error(
                f"Error populating chatbot knowledge base: {e}", exc_info=True
            )
            self.queue_response(
                f"Error populating chatbot knowledge base: {e}", "error"
            )

    def _add_default_admin_user(self):
        self.log_info("Adding default admin user if not exists...")
        try:
            with self.db_engine.connect() as connection:
                # Check if admin user already exists
                result = connection.execute(
                    text("SELECT COUNT(*) FROM users WHERE username = 'admin';")
                ).scalar()
                if result == 0:
                    # In a real application, hash the password securely
                    hashed_password = "pwd12345"  # Placeholder: Use a proper hashing library like bcrypt in production
                    connection.execute(
                        text(
                            "INSERT INTO users (user_id, username, password_hash, role) VALUES (:user_id, :username, :password_hash, :role);"
                        ),
                        {
                            "user_id": str(uuid.uuid4()),
                            "username": "admin",
                            "password_hash": hashed_password,
                            "role": "admin",
                        },
                    )
                    connection.commit()
                    self.log_info("Default admin user 'admin' added.")
                else:
                    self.log_info("Default admin user 'admin' already exists.")
        except Exception as e:
            self.log_error(f"Error adding default admin user: {e}", exc_info=True)
            self.queue_response(f"Error adding default admin user: {e}", "error")

    def clear_all_tables(self):
        if not self.db_connected:
            self.log_error("Cannot clear tables: Database not connected.")
            self.queue_response("Cannot clear tables: Database not connected.", "error")
            return

        self.log_info("Clearing all data from tables...")
        try:
            with self.db_engine.connect() as connection:
                # Get all table names
                inspector = connection.dialect.inspector(connection)
                table_names = inspector.get_table_names()

                # Drop tables in reverse order of dependency if possible, or just clear data
                # For simplicity, we'll just delete all rows from all tables.
                # If there are foreign key constraints, this might require specific ordering
                # or temporarily disabling constraints (SQLite handles this gracefully).
                tables_to_clear = [
                    "intervention_recommendations",
                    "student_years",
                    "academic_records",
                    "attendance_records",
                    "students",
                    "parents",
                    "schools",
                    "chatbot_knowledge_base",
                    "users",
                    # Lookup tables - usually not cleared unless re-populating definitions
                    # "gender_lookup", "school_type_lookup", "province_lookup", "district_lookup",
                    # "quintile_lookup", "subject_lookup", "academic_assessment_type_lookup",
                    # "attendance_status_lookup", "socio_economic_status_lookup",
                    # "home_environment_lookup", "internet_access_lookup", "study_habits_lookup",
                    # "extracurricular_engagement_lookup", "health_nutrition_lookup",
                    # "special_needs_support_lookup", "intervention_type_lookup"
                ]

                for table_name in tables_to_clear:
                    connection.execute(text(f"DELETE FROM {table_name};"))
                connection.commit()
            self.log_info("All data cleared successfully.")
            self.queue_response("All data cleared successfully.", "success")
            self.dataset_ready = False
            self.model_trained = False
            self.model_metrics = {}
        except Exception as e:
            self.log_error(f"Error clearing tables: {e}", exc_info=True)
            self.queue_response(f"Error clearing tables: {e}", "error")

    def queue_response(
        self, message, status, data=None, columns=None, title=None, data_preview=None
    ):
        """Adds a response to the queue to be sent to the frontend."""
        self.response_queue.append(
            {
                "message": message,
                "status": status,
                "data": data,
                "columns": columns,
                "title": title,
                "data_preview": data_preview,  # For predicted data or specific previews
            }
        )

    def get_queued_responses(self):
        """Retrieves and clears the current queue of responses."""
        responses = list(self.response_queue)
        self.response_queue.clear()
        return responses

    # --- Data Generation Functions ---

    def generate_schools(self, num_schools=10):
        self.log_info(f"Generating {num_schools} schools...")
        schools_data = []
        try:
            with self.db_engine.connect() as connection:
                # Changed to pd.read_sql_query for more robust lookup table access
                # Updated to use 'province_name' instead of 'name' for province_lookup
                provinces_df = pd.read_sql_query(
                    text("SELECT province_name FROM province_lookup"), connection
                )
                districts_df = pd.read_sql_query(
                    text("SELECT name FROM district_lookup"), connection
                )
                school_types_df = pd.read_sql_query(
                    text("SELECT name FROM school_type_lookup"), connection
                )
                quintiles_df = pd.read_sql_query(
                    text("SELECT name FROM quintile_lookup"), connection
                )

                provinces = provinces_df[
                    "province_name"
                ].tolist()  # Changed to 'province_name'
                districts = districts_df["name"].tolist()
                school_types = school_types_df["name"].tolist()
                quintiles = quintiles_df["name"].tolist()

                for i in range(num_schools):
                    school_id = f"SCH{uuid.uuid4().hex[:8].upper()}"
                    school_name = f"{random.choice(['Beacon', 'Summit', 'Harmony', 'Global', 'Future'])} {random.choice(['High', 'Primary', 'Combined'])} School"
                    school_type = random.choice(school_types)
                    province = random.choice(provinces)
                    district = random.choice(districts)
                    quintile = int(
                        random.choice(quintiles).split(" ")[1]
                    )  # Extract number from "Quintile X"

                    schools_data.append(
                        {
                            "school_id": school_id,
                            "school_name": school_name,
                            "school_type": school_type,
                            "province": province,
                            "district": district,
                            "quintile": quintile,
                        }
                    )

                schools_df = pd.DataFrame(schools_data)
                schools_df.to_sql(
                    "schools", connection, if_exists="append", index=False
                )
                connection.commit()
            self.log_info(f"Successfully generated {num_schools} schools.")
            self.queue_response(
                f"Successfully generated {num_schools} schools.",
                "success",
                data=schools_df.to_dict(orient="records"),
                columns=schools_df.columns.tolist(),
                title="Generated Schools",
            )
        except Exception as e:
            self.log_error(f"Error generating schools: {e}", exc_info=True)
            self.queue_response(f"Error generating schools: {e}", "error")

    def generate_parents(self, num_parents=50):
        self.log_info(f"Generating {num_parents} parents...")
        parents_data = []
        try:
            with self.db_engine.connect() as connection:
                for i in range(num_parents):
                    parent_id = f"PAR{uuid.uuid4().hex[:8].upper()}"
                    first_name = "".join(
                        random.choice(string.ascii_letters)
                        for _ in range(random.randint(5, 10))
                    ).capitalize()
                    last_name = "".join(
                        random.choice(string.ascii_letters)
                        for _ in range(random.randint(5, 10))
                    ).capitalize()
                    contact_number = (
                        f"0{random.randint(60, 89)}{random.randint(1000000, 9999999)}"
                    )
                    email = f"{first_name.lower()}.{last_name.lower()}@{random.choice(['example.com', 'mail.org', 'test.net'])}"

                    parents_data.append(
                        {
                            "parent_id": parent_id,
                            "first_name": first_name,
                            "last_name": last_name,
                            "contact_number": contact_number,
                            "email": email,
                        }
                    )

                parents_df = pd.DataFrame(parents_data)
                parents_df.to_sql(
                    "parents", connection, if_exists="append", index=False
                )
                connection.commit()
            self.log_info(f"Successfully generated {num_parents} parents.")
            self.queue_response(
                f"Successfully generated {num_parents} parents.",
                "success",
                data=parents_df.to_dict(orient="records"),
                columns=parents_df.columns.tolist(),
                title="Generated Parents",
            )
        except Exception as e:
            self.log_error(f"Error generating parents: {e}", exc_info=True)
            self.queue_response(f"Error generating parents: {e}", "error")

    def generate_students_and_initial_enrollments(self, num_students=100):
        self.log_info(f"Generating {num_students} students and initial enrollments...")
        students_data = []
        student_years_data = []
        try:
            with self.db_engine.connect() as connection:
                schools_df = pd.read_sql_table("schools", connection)
                parents_df = pd.read_sql_table("parents", connection)
                gender_lookup_df = pd.read_sql_table("gender_lookup", connection)

                if schools_df.empty or parents_df.empty:
                    self.log_warning(
                        "Cannot generate students: No schools or parents found. Please generate them first."
                    )
                    self.queue_response(
                        "Cannot generate students: No schools or parents found. Please generate them first.",
                        "warning",
                    )
                    return

                school_ids = schools_df["school_id"].tolist()
                parent_ids = parents_df["parent_id"].tolist()
                genders = gender_lookup_df["name"].tolist()

                current_year = datetime.now().year

                for i in range(num_students):
                    student_id = f"STU{uuid.uuid4().hex[:8].upper()}"
                    first_name = "".join(
                        random.choice(string.ascii_letters)
                        for _ in range(random.randint(5, 10))
                    ).capitalize()
                    last_name = "".join(
                        random.choice(string.ascii_letters)
                        for _ in range(random.randint(5, 10))
                    ).capitalize()

                    dob = datetime.now() - timedelta(
                        days=random.randint(14 * 365, 18 * 365)
                    )  # Age 14-18
                    gender = random.choice(genders)
                    grade_level = random.randint(8, 12)  # High school grades
                    school_id = random.choice(school_ids)
                    parent_id = random.choice(parent_ids)
                    enrollment_date = datetime(
                        current_year - random.randint(0, 3),
                        random.randint(1, 12),
                        random.randint(1, 28),
                    ).date()

                    students_data.append(
                        {
                            "student_id": student_id,
                            "first_name": first_name,
                            "last_name": last_name,
                            "date_of_birth": dob.date(),
                            "gender": gender,
                            "grade_level": grade_level,
                            "school_id": school_id,
                            "parent_id": parent_id,
                            "enrollment_date": enrollment_date,
                        }
                    )

                    # Initial student_years entry for the current year
                    student_years_data.append(
                        {
                            "student_year_id": f"SY{uuid.uuid4().hex[:8].upper()}",
                            "student_id": student_id,
                            "academic_year": current_year,
                            "grade_level": grade_level,
                            "final_mark": float(
                                random.randint(40, 95)
                            ),  # Dummy initial mark
                            "dropout_risk": round(random.uniform(0.01, 0.5), 2),
                            "socio_economic_score": round(random.uniform(1.0, 10.0), 2),
                            "home_environment_score": round(
                                random.uniform(1.0, 10.0), 2
                            ),
                            "internet_access_score": round(
                                random.uniform(1.0, 10.0), 2
                            ),
                            "study_habits_score": round(random.uniform(1.0, 10.0), 2),
                            "extracurricular_engagement_score": round(
                                random.uniform(1.0, 10.0), 2
                            ),
                            "health_nutrition_score": round(
                                random.uniform(1.0, 10.0), 2
                            ),
                            "special_needs_support_score": round(
                                random.uniform(1.0, 10.0), 2
                            ),
                        }
                    )

                students_df = pd.DataFrame(students_data)
                students_df.to_sql(
                    "students", connection, if_exists="append", index=False
                )

                student_years_df = pd.DataFrame(student_years_data)
                student_years_df.to_sql(
                    "student_years", connection, if_exists="append", index=False
                )

                connection.commit()
            self.log_info(
                f"Successfully generated {num_students} students and initial enrollments."
            )
            self.queue_response(
                f"Successfully generated {num_students} students and initial enrollments.",
                "success",
                data=students_df.to_dict(orient="records"),
                columns=students_df.columns.tolist(),
                title="Generated Students",
            )
        except Exception as e:
            self.log_error(
                f"Error generating students and initial enrollments: {e}", exc_info=True
            )
            self.queue_response(
                f"Error generating students and initial enrollments: {e}", "error"
            )

    def generate_academic_records(self, num_records_per_student=10):
        self.log_info(f"Generating academic records...")
        academic_records_data = []
        try:
            with self.db_engine.connect() as connection:
                students_df = pd.read_sql_table("students", connection)
                subjects_df = pd.read_sql_table("subject_lookup", connection)
                assessment_types_df = pd.read_sql_table(
                    "academic_assessment_type_lookup", connection
                )

                if students_df.empty:
                    self.log_warning(
                        "Cannot generate academic records: No students found. Please generate students first."
                    )
                    self.queue_response(
                        "Cannot generate academic records: No students found. Please generate students first.",
                        "warning",
                    )
                    return

                student_ids = students_df["student_id"].tolist()
                subject_names = subjects_df["name"].tolist()
                assessment_types = assessment_types_df["name"].tolist()

                current_year = datetime.now().year

                for student_id in student_ids:
                    for _ in range(num_records_per_student):
                        record_id = f"ACD{uuid.uuid4().hex[:8].upper()}"
                        subject_name = random.choice(subject_names)
                        assessment_type = random.choice(assessment_types)
                        mark = round(random.uniform(30.0, 100.0), 2)

                        # Random date within the last year or current year
                        assessment_date = datetime(
                            current_year - random.randint(0, 1),
                            random.randint(1, 12),
                            random.randint(1, 28),
                        ).date()
                        academic_year = assessment_date.year

                        academic_records_data.append(
                            {
                                "record_id": record_id,
                                "student_id": student_id,
                                "subject_name": subject_name,
                                "assessment_type": assessment_type,
                                "mark": mark,
                                "assessment_date": assessment_date,
                                "academic_year": academic_year,
                            }
                        )

                academic_records_df = pd.DataFrame(academic_records_data)
                academic_records_df.to_sql(
                    "academic_records", connection, if_exists="append", index=False
                )
                connection.commit()
            self.log_info(
                f"Successfully generated academic records for {len(student_ids)} students."
            )
            self.queue_response(
                f"Successfully generated academic records.",
                "success",
                data=academic_records_df.to_dict(orient="records"),
                columns=academic_records_df.columns.tolist(),
                title="Generated Academic Records",
            )
        except Exception as e:
            self.log_error(f"Error generating academic records: {e}", exc_info=True)
            self.queue_response(f"Error generating academic records: {e}", "error")

    def generate_attendance_records(self, num_days_per_student=60):
        self.log_info(f"Generating attendance records...")
        attendance_records_data = []
        try:
            with self.db_engine.connect() as connection:
                students_df = pd.read_sql_table("students", connection)
                attendance_status_df = pd.read_sql_table(
                    "attendance_status_lookup", connection
                )

                if students_df.empty:
                    self.log_warning(
                        "Cannot generate attendance records: No students found. Please generate students first."
                    )
                    self.queue_response(
                        "Cannot generate attendance records: No students found. Please generate students first.",
                        "warning",
                    )
                    return

                student_ids = students_df["student_id"].tolist()
                attendance_statuses = attendance_status_df["name"].tolist()

                current_date = datetime.now().date()

                for student_id in student_ids:
                    for i in range(num_days_per_student):
                        record_date = current_date - timedelta(days=i)
                        status = random.choices(
                            attendance_statuses, weights=[0.85, 0.10, 0.05], k=1
                        )[
                            0
                        ]  # 85% present, 10% absent, 5% late
                        reason = ""
                        if status == "Absent":
                            reason = random.choice(
                                ["Illness", "Family emergency", "Other"]
                            )
                        elif status == "Late":
                            reason = random.choice(["Traffic", "Overslept", "Other"])

                        attendance_records_data.append(
                            {
                                "attendance_id": f"ATT{uuid.uuid4().hex[:8].upper()}",
                                "student_id": student_id,
                                "record_date": record_date,
                                "status": status,
                                "reason": reason,
                            }
                        )

                attendance_records_df = pd.DataFrame(attendance_records_data)
                attendance_records_df.to_sql(
                    "attendance_records", connection, if_exists="append", index=False
                )
                connection.commit()
            self.log_info(
                f"Successfully generated attendance records for {len(student_ids)} students."
            )
            self.queue_response(
                f"Successfully generated attendance records.",
                "success",
                data=attendance_records_df.to_dict(orient="records"),
                columns=attendance_records_df.columns.tolist(),
                title="Generated Attendance Records",
            )
        except Exception as e:
            self.log_error(f"Error generating attendance records: {e}", exc_info=True)
            self.queue_response(f"Error generating attendance records: {e}", "error")

    def generate_all_data(self):
        self.log_info(
            "Generating all data: schools, parents, students, academic history, and attendance..."
        )
        self.clear_all_tables()  # Clear existing data first
        self.generate_schools()
        self.generate_parents()
        self.generate_students_and_initial_enrollments()
        self.generate_academic_records()
        self.generate_attendance_records()
        self.log_info("All data generation complete.")
        self.dataset_ready = True
        self.queue_response("All data generation complete.", "success")

    # --- Data Retrieval Functions ---

    def get_table_data(self, table_name):
        if not self.db_connected:
            return {"status": "error", "message": "Database not connected."}
        try:
            with self.db_engine.connect() as connection:
                query = text(f"SELECT * FROM {table_name};")
                df = pd.read_sql(query, connection)
                if df.empty:
                    return {
                        "status": "info",
                        "message": f"No data found in {table_name}.",
                        "data": [],
                        "columns": [],
                    }

                # Convert dates to string for JSON serialization
                for col in df.columns:
                    if pd.api.types.is_datetime64_any_dtype(df[col]):
                        df[col] = df[col].dt.strftime("%Y-%m-%d")

                return {
                    "status": "success",
                    "message": f"Data from {table_name} retrieved.",
                    "data": df.to_dict(orient="records"),
                    "columns": df.columns.tolist(),
                }
        except Exception as e:
            self.log_error(
                f"Error retrieving data from {table_name}: {e}", exc_info=True
            )
            return {
                "status": "error",
                "message": f"Error retrieving data from {table_name}: {e}",
            }

    # --- Model Training and Prediction Functions ---

    def train_model(self):
        self.log_info("Starting model training process...")
        if not self.db_connected:
            self.log_error("Cannot train model: Database not connected.")
            self.queue_response("Cannot train model: Database not connected.", "error")
            return

        try:
            with self.db_engine.connect() as connection:
                # Fetch data from student_years table
                # Ensure 'school_id' is fetched and handled if it's a feature
                df = pd.read_sql_table("student_years", connection)
                schools_df = pd.read_sql_table("schools", connection)
                students_df = pd.read_sql_table("students", connection)

                if df.empty or schools_df.empty or students_df.empty:
                    self.log_warning(
                        "Insufficient data for training. Please generate all data first."
                    )
                    self.queue_response(
                        "Insufficient data for training. Please generate all data first.",
                        "warning",
                    )
                    self.model_trained = False
                    return

                # Merge to get school_id and gender for encoding
                df = pd.merge(
                    df,
                    students_df[["student_id", "school_id", "gender"]],
                    on="student_id",
                    how="left",
                )
                df = pd.merge(
                    df,
                    schools_df[["school_id", "quintile"]],
                    on="school_id",
                    how="left",
                )

                # Feature Engineering (simplified for this example)
                df["gender_encoded"] = (
                    df["gender"].map({"Male": 0, "Female": 1}).fillna(-1)
                )  # Handle missing

                # Drop non-numeric or target columns
                features = [
                    "grade_level",
                    "dropout_risk",
                    "socio_economic_score",
                    "home_environment_score",
                    "internet_access_score",
                    "study_habits_score",
                    "extracurricular_engagement_score",
                    "health_nutrition_score",
                    "special_needs_support_score",
                    "gender_encoded",
                    "quintile",
                ]

                # Ensure all features exist and handle potential NaNs
                for col in features:
                    if col not in df.columns:
                        self.log_warning(
                            f"Feature '{col}' not found in dataset. Skipping or imputing."
                        )
                        df[col] = 0  # Simple imputation for missing columns
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(
                        df[col].mean()
                    )  # Ensure numeric and fill NaNs

                # Define features (X) and target (y)
                X = df[features]
                y = df["final_mark"]

                if X.empty or y.empty:
                    self.log_warning(
                        "Features or target are empty after preprocessing. Cannot train model."
                    )
                    self.queue_response(
                        "Features or target are empty after preprocessing. Cannot train model.",
                        "warning",
                    )
                    self.model_trained = False
                    return

                # Split data
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42
                )

                # Initialize and train a RandomForestRegressor model
                self.model = RandomForestRegressor(n_estimators=100, random_state=42)
                self.model.fit(X_train, y_train)

                # Evaluate the model
                predictions = self.model.predict(X_test)
                mse = mean_squared_error(y_test, predictions)
                r2 = r2_score(y_test, predictions)

                self.model_metrics = {"MSE": round(mse, 2), "R2_Score": round(r2, 2)}
                self.log_info(
                    f"Model trained successfully. Metrics: MSE={mse:.2f}, R2={r2:.2f}"
                )
                self.queue_response(
                    "Model trained successfully.", "success", metrics=self.model_metrics
                )
                self.model_trained = True

                # Save the trained model and features for later use
                model_dir = "models"
                os.makedirs(model_dir, exist_ok=True)
                joblib.dump(
                    self.model,
                    os.path.join(model_dir, "student_performance_model.joblib"),
                )
                joblib.dump(features, os.path.join(model_dir, "model_features.joblib"))
                self.log_info("Model and features saved.")

        except Exception as e:
            self.log_error(f"Error during model training: {e}", exc_info=True)
            self.queue_response(f"Error during model training: {e}", "error")
            self.model_trained = False

    def predict_marks(self):
        self.log_info("Starting student marks prediction...")
        if not self.model_trained or self.model is None:
            self.log_warning("Model not trained. Please train the model first.")
            self.queue_response(
                "Model not trained. Please train the model first.", "warning"
            )
            return

        if not self.db_connected:
            self.log_error("Cannot predict marks: Database not connected.")
            self.queue_response(
                "Cannot predict marks: Database not connected.", "error"
            )
            return

        try:
            with self.db_engine.connect() as connection:
                # Load the features used during training
                model_dir = "models"
                features_path = os.path.join(model_dir, "model_features.joblib")
                if not os.path.exists(features_path):
                    self.log_error("Model features not found. Cannot predict.")
                    self.queue_response(
                        "Model features not found. Cannot predict.", "error"
                    )
                    return
                loaded_features = joblib.load(features_path)

                # Fetch the latest student data for prediction
                # For simplicity, we'll predict for all students in student_years
                df = pd.read_sql_table("student_years", connection)
                schools_df = pd.read_sql_table("schools", connection)
                students_df = pd.read_sql_table("students", connection)

                if df.empty or schools_df.empty or students_df.empty:
                    self.log_warning("No student data available for prediction.")
                    self.queue_response(
                        "No student data available for prediction.", "warning"
                    )
                    return

                # Merge to get school_id and gender for encoding
                df = pd.merge(
                    df,
                    students_df[["student_id", "school_id", "gender"]],
                    on="student_id",
                    how="left",
                )
                df = pd.merge(
                    df,
                    schools_df[["school_id", "quintile"]],
                    on="school_id",
                    how="left",
                )

                # Preprocess data for prediction, ensuring columns match training data
                prediction_df = df.copy()
                prediction_df["gender_encoded"] = (
                    prediction_df["gender"].map({"Male": 0, "Female": 1}).fillna(-1)
                )

                # Select only the features the model was trained on
                X_predict = prediction_df[loaded_features]

                # Ensure all columns are numeric and handle NaNs
                for col in X_predict.columns:
                    X_predict[col] = pd.to_numeric(
                        X_predict[col], errors="coerce"
                    ).fillna(X_predict[col].mean())

                # Make predictions
                predicted_marks = self.model.predict(X_predict)
                prediction_df["predicted_mark"] = np.round(predicted_marks, 2)

                # Calculate confidence (simple example: based on inverse of distance to mean/std dev of predictions)
                # In a real scenario, this would involve more sophisticated methods like prediction intervals
                mean_pred = prediction_df["predicted_mark"].mean()
                std_pred = prediction_df["predicted_mark"].std()

                if std_pred > 0:
                    prediction_df["confidence"] = np.round(
                        1
                        - (
                            np.abs(prediction_df["predicted_mark"] - mean_pred)
                            / (3 * std_pred)
                        ),
                        2,
                    )
                    prediction_df["confidence"] = prediction_df["confidence"].clip(
                        0, 1
                    )  # Clip between 0 and 1
                else:
                    prediction_df["confidence"] = (
                        1.0  # If std dev is 0, all predictions are the same, max confidence
                    )

                # Prepare data for frontend
                results = prediction_df[
                    [
                        "student_id",
                        "academic_year",
                        "grade_level",
                        "final_mark",
                        "predicted_mark",
                        "confidence",
                    ]
                ].to_dict(orient="records")
                columns = [
                    "student_id",
                    "academic_year",
                    "grade_level",
                    "final_mark",
                    "predicted_mark",
                    "confidence",
                ]

                self.log_info(
                    f"Successfully predicted marks for {len(results)} students."
                )
                self.queue_response(
                    "Student marks predicted successfully.",
                    "success",
                    data_preview=results,
                    columns=columns,
                    title="Predicted Student Marks",
                )

        except Exception as e:
            self.log_error(f"Error during prediction: {e}", exc_info=True)
            self.queue_response(f"Error during prediction: {e}", "error")


# --- Flask App Setup ---
app = Flask(__name__, static_folder="static", static_url_path="/static")
app_state = AppState()  # Initialize the singleton AppState


# Route for the main admin page
@app.route("/")
def index():
    app_state.log_info("Admin page requested.")  # Added log
    return render_template("admin.html")


# Route for static files (e.g., Naledi.png)
# This is already handled by `static_folder` and `static_url_path` in Flask app initialization
# @app.route("/static/<path:filename>")
# def static_files(filename):
#     return send_from_directory("static", filename)


@app.route("/api/get_status", methods=["GET"])
def get_status():
    app_state.log_debug(
        "GET /api/get_status called."
    )  # Debug log for every status request
    # Read the current console output
    console_content = app_state.console_output_buffer.getvalue()

    # Get and clear queued responses
    queued_responses = app_state.get_queued_responses()

    # Get memory usage
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    memory_usage_mb = memory_info.rss / (1024 * 1024)  # Resident Set Size in MB

    return jsonify(
        {
            "status": "connected" if app_state.db_connected else "disconnected",
            "dataset_ready": app_state.dataset_ready,
            "model_trained": app_state.model_trained,
            "metrics": app_state.model_metrics,
            "console_output": console_content,
            "response_queue": queued_responses,  # Send queued responses
            "error_count": app_state.error_count,
            "last_error": app_state.last_error,
            "app_version": app_state.app_version,
            "memory_usage_mb": round(memory_usage_mb, 2),
        }
    )


@app.route("/api/clear_console", methods=["POST"])
def clear_console():
    app_state.console_output_buffer.truncate(0)  # Clear the buffer
    app_state.console_output_buffer.seek(0)  # Reset buffer position
    app_state.log_info("Console output cleared by user.")
    return jsonify({"status": "success", "message": "Console output cleared."})


@app.route("/api/clear_response_queue", methods=["POST"])
def clear_response_queue_api():
    """API to clear the response queue on the backend after frontend has processed them."""
    app_state.response_queue.clear()
    return jsonify({"status": "success", "message": "Response queue cleared."})


@app.route("/api/connect_db", methods=["POST"])
def connect_db():
    if app_state.db_connected:
        return jsonify({"status": "info", "message": "Database already connected."})

    app_state.log_info("Connect DB API called.")
    # Run connection in a separate thread to avoid blocking the API response
    threading.Thread(target=app_state.connect_db_background).start()
    return jsonify(
        {"status": "success", "message": "Attempting to connect to database..."}
    )


@app.route("/api/disconnect_db", methods=["POST"])
def disconnect_db():
    if not app_state.db_connected:
        return jsonify({"status": "info", "message": "Database already disconnected."})

    app_state.log_info("Disconnect DB API called.")
    app_state.disconnect_db()
    return jsonify(
        {"status": "success", "message": "Database disconnection initiated."}
    )


@app.route("/api/create_tables", methods=["POST"])
def create_tables_api():
    if not app_state.db_connected:
        return jsonify({"status": "error", "message": "Database not connected."})

    app_state.log_info("Create Tables API called.")
    threading.Thread(target=app_state.create_tables).start()
    return jsonify({"status": "success", "message": "Schema creation initiated."})


@app.route("/api/clear_all_tables", methods=["POST"])
def clear_all_tables_api():
    if not app_state.db_connected:
        return jsonify({"status": "error", "message": "Database not connected."})

    app_state.log_info("Clear All Tables API called.")
    threading.Thread(target=app_state.clear_all_tables).start()
    return jsonify({"status": "success", "message": "Clearing all data initiated."})


@app.route("/api/generate_schools", methods=["POST"])
def generate_schools_api():
    if not app_state.db_connected:
        return jsonify({"status": "error", "message": "Database not connected."})
    app_state.log_info("Generate Schools API called.")
    threading.Thread(target=app_state.generate_schools).start()
    return jsonify({"status": "success", "message": "School generation initiated."})


@app.route("/api/generate_parents", methods=["POST"])
def generate_parents_api():
    if not app_state.db_connected:
        return jsonify({"status": "error", "message": "Database not connected."})
    app_state.log_info("Generate Parents API called.")
    threading.Thread(target=app_state.generate_parents).start()
    return jsonify({"status": "success", "message": "Parent generation initiated."})


@app.route("/api/generate_students_and_initial_enrollments", methods=["POST"])
def generate_students_api():
    if not app_state.db_connected:
        return jsonify({"status": "error", "message": "Database not connected."})
    app_state.log_info("Generate Students API called.")
    threading.Thread(target=app_state.generate_students_and_initial_enrollments).start()
    return jsonify({"status": "success", "message": "Student generation initiated."})


@app.route("/api/generate_academic_records", methods=["POST"])
def generate_academic_records_api():
    if not app_state.db_connected:
        return jsonify({"status": "error", "message": "Database not connected."})
    app_state.log_info("Generate Academic Records API called.")
    threading.Thread(target=app_state.generate_academic_records).start()
    return jsonify(
        {"status": "success", "message": "Academic record generation initiated."}
    )


@app.route("/api/generate_attendance_records", methods=["POST"])
def generate_attendance_records_api():
    if not app_state.db_connected:
        return jsonify({"status": "error", "message": "Database not connected."})
    app_state.log_info("Generate Attendance Records API called.")
    threading.Thread(target=app_state.generate_attendance_records).start()
    return jsonify(
        {"status": "success", "message": "Attendance record generation initiated."}
    )


@app.route("/api/generate_all_data", methods=["POST"])
def generate_all_data_api():
    if not app_state.db_connected:
        return jsonify({"status": "error", "message": "Database not connected."})
    app_state.log_info("Generate All Data API called.")
    threading.Thread(target=app_state.generate_all_data).start()
    return jsonify({"status": "success", "message": "All data generation initiated."})


@app.route("/api/train_model", methods=["POST"])
def train_model_api():
    if not app_state.db_connected:
        return jsonify({"status": "error", "message": "Database not connected."})
    app_state.log_info("Train Model API called.")
    threading.Thread(target=app_state.train_model).start()
    return jsonify({"status": "success", "message": "Model training initiated."})


@app.route("/api/predict_marks", methods=["POST"])
def predict_marks_api():
    if not app_state.db_connected:
        return jsonify({"status": "error", "message": "Database not connected."})
    app_state.log_info("Predict Marks API called.")
    threading.Thread(target=app_state.predict_marks).start()
    return jsonify({"status": "success", "message": "Prediction initiated."})


@app.route("/api/get_table_data/<table_name>", methods=["GET"])
def get_table_data_api(table_name):
    app_state.log_info(f"Get Table Data API called for {table_name}.")
    response = app_state.get_table_data(table_name)
    return jsonify(response)


@app.errorhandler(404)
def resource_not_found(e):
    app_state.last_error = str(e)
    app_state.error_count += 1
    return (
        jsonify(
            error="Not Found", message="The requested URL was not found on the server."
        ),
        404,
    )


@app.errorhandler(500)
def internal_server_error(error):
    error_details = traceback.format_exc()
    app_state.log_error(f"Internal Server Error: {error}\n{error_details}")

    app_state.last_error = str(error)
    app_state.error_count += 1

    return (
        jsonify(
            {
                "status": "error",
                "message": "Internal Server Error. The application encountered an issue.",
                "details": str(error),
            }
        ),
        500,
    )


@app.errorhandler(Exception)
def handle_unhandled_exception(error):
    """
    Handle any unhandled exceptions and provide a friendly response
    """
    error_details = traceback.format_exc()
    app_state.log_error(f"Unhandled Exception: {error}\n{error_details}")

    # Update app state error tracking
    app_state.last_error = str(error)
    app_state.error_count += 1

    return (
        jsonify(
            {
                "status": "error",
                "message": "An unexpected error occurred",
                "details": str(error),
            }
        ),
        500,
    )


if __name__ == "__main__":
    # Initialize app_state here, ensuring it runs only once.
    # The AppState class is a singleton, so subsequent calls to AppState()
    # will return the same instance.
    app_state = AppState()
    # This explicit call ensures engine initialization starts immediately on app startup
    # app_state.initialize_engine_async() # Called inside AppState.__init__ now.

    # Start the Flask development server
    # In a production environment, use a production-ready WSGI server like Gunicorn or uWSGI
    app_state.log_info(f"Attempting to start Flask app on port 8000...")
    try:
        app.run(debug=False, port=8000, host="0.0.0.0")
        print("Flask app finished running or encountered an unhandled error.")
    except Exception as e:
        app_state.log_error(f"Failed to start Flask app: {e}", exc_info=True)
        print(f"CRITICAL ERROR: Flask app failed to start: {e}", file=sys.stderr)
