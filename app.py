import os
import pandas as pd
from flask import (
    Flask,
    request,
    jsonify,
    send_from_directory,
    session,
    redirect,
    url_for,
    flash,
)
from flask_cors import CORS
from datetime import datetime, timedelta
import random
import numpy as np
import uuid
import logging

logging.basicConfig(level=logging.DEBUG)
from collections import deque
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
from starlette.middleware.wsgi import WSGIMiddleware
import sys
import threading
import re
import string  # For generating random strings
from sqlalchemy import create_engine, text
import urllib.parse
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
import configparser  # Ensure configparser is imported

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# In-memory console log and response queue for frontend communication
console_output_log = deque(maxlen=500)
response_queue = deque()

# --- Constants for Data Generation (from appl.py) ---
NUM_SCHOOLS_TO_GENERATE = 12
NUM_PARENTS_TO_GENERATE = 300
TOTAL_UNIQUE_STUDENTS_TO_GENERATE = 1100  # Adjusted for reasonable generation
START_YEAR = 2017
END_YEAR = 2025
MAX_YEARS_IN_SCHOOL = 12
DROPOUT_RATE_PER_YEAR = 0.05
PROGRESSION_RATE_PER_YEAR = 0.95
REPEATING_GRADE_CHANCE = 0.02
MAX_REPEATS_PER_GRADE = 1

# --- Utility Functions ---


def mask_sensitive_data(text):
    """
    Masks sensitive information like IP addresses, database UIDs, and PWDs
    in a given string.
    """
    text = re.sub(
        r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(:\d+)?\b", "***.***.***.***:****", text
    )
    text = re.sub(r"\[([0-9a-fA-F:]+)\](:\d+)?", "[::*]:****", text)
    text = re.sub(
        r"(UID|User ID|User|Username)=[^;]+", r"\1=***", text, flags=re.IGNORECASE
    )
    text = re.sub(r"(PWD|Password)=[^;]+", r"\1=***", text, flags=re.IGNORECASE)
    text = re.sub(r"password=([^\s&]+)", "password=***", text, flags=re.IGNORECASE)
    text = re.sub(r"pwd=([^\s&]+)", "pwd=***", text, flags=re.IGNORECASE)
    return text


def log_to_console(message, level="INFO", sensitive=False):
    """
    Adds a message to the in-memory console log and prints to stdout.
    If 'sensitive' is True, the message content will be masked.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
    if sensitive:
        message = mask_sensitive_data(message)
    log_entry = f"{timestamp} - {level} - {message}"
    console_output_log.append(log_entry)
    print(log_entry)
    sys.stdout.flush()


def add_response_to_queue(
    message, status="info", data=None, columns=None, title=None, data_preview=None
):
    """Adds a response to the queue for the frontend to pick up."""
    response_item = {
        "message": message,
        "status": status,
        "timestamp": datetime.now().isoformat(),
    }
    if data is not None:
        response_item["data"] = data
    if columns is not None:
        response_item["columns"] = columns
    if title is not None:
        response_item["title"] = title
    if data_preview is not None:
        response_item["data_preview"] = data_preview
    response_queue.append(response_item)


# --- Database Connection and Utility Functions ---

sqlalchemy_engine = None


def get_db_connection():
    """Returns an SQLAlchemy engine, creating it if it doesn't exist."""
    global sqlalchemy_engine
    if sqlalchemy_engine is None:
        log_to_console("Attempting to establish SQLAlchemy engine...", "INFO")
        try:
            config = configparser.ConfigParser()
            config_file_path = "config.ini"

            # Check if config.ini exists
            if not os.path.exists(config_file_path):
                log_to_console(
                    f"Error: config.ini not found at {os.path.abspath(config_file_path)}",
                    "CRITICAL",
                )
                add_response_to_queue(
                    "Critical: config.ini file not found. Database connection failed.",
                    "error",
                )
                update_app_state("db_connected", False)
                sqlalchemy_engine = None
                return None

            # Read config.ini
            try:
                config.read(config_file_path)
                log_to_console(
                    f"Successfully read config.ini from {os.path.abspath(config_file_path)}",
                    "DEBUG",
                )
            except configparser.Error as e:
                log_to_console(
                    f"ConfigParser error reading config.ini: {e}", "CRITICAL"
                )
                add_response_to_queue(
                    f"Configuration error: {e}. Please check config.ini format.",
                    "error",
                )
                update_app_state("db_connected", False)
                sqlalchemy_engine = None
                return None

            ODBC_CONNECTION_STRING = config.get(
                "Database",
                "connection_string",
                fallback="DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=StudentMarks;Trusted_Connection=yes;",
            )
            log_to_console(
                f"ODBC Connection String (masked): {mask_sensitive_data(ODBC_CONNECTION_STRING)}",
                "DEBUG",
                sensitive=True,
            )

            quoted_odbc_string = urllib.parse.quote_plus(ODBC_CONNECTION_STRING)
            db_url = f"mssql+pyodbc:///?odbc_connect={quoted_odbc_string}"

            log_to_console("Creating SQLAlchemy engine...", "INFO")
            sqlalchemy_engine = create_engine(db_url, pool_pre_ping=True)

            log_to_console("Testing database connection...", "INFO")
            with sqlalchemy_engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            log_to_console(
                "SQLAlchemy engine established and tested successfully.", "INFO"
            )
            update_app_state("db_connected", True)
        except Exception as e:
            log_to_console(
                f"An error occurred creating or testing SQLAlchemy engine: {e}",
                "CRITICAL",
            )
            update_app_state("db_connected", False)
            sqlalchemy_engine = None
            return None
    return sqlalchemy_engine


def read_table_to_dataframe(engine, table_name):
    """Reads a SQL table into a Pandas DataFrame."""
    try:
        df = pd.read_sql_table(table_name, engine)
        log_to_console(
            f"Successfully read table '{table_name}' into DataFrame.", "DEBUG"
        )
        return df
    except Exception as e:
        log_to_console(
            f"Error reading table '{table_name}' into DataFrame: {e}", "ERROR"
        )
        return pd.DataFrame()  # Return empty DataFrame on error


def write_dataframe_to_sql(engine, df, table_name, if_exists="append"):
    """Writes a Pandas DataFrame to a SQL table."""
    try:
        with engine.connect() as connection:
            with connection.begin():
                df.to_sql(table_name, connection, if_exists=if_exists, index=False)
        log_to_console(
            f"Successfully wrote DataFrame to table '{table_name}'.", "DEBUG"
        )
        return True
    except Exception as e:
        log_to_console(f"Error writing DataFrame to table '{table_name}': {e}", "ERROR")
        return False


def execute_sql_query(engine, query):
    """Executes a raw SQL query."""
    try:
        with engine.connect() as connection:
            with connection.begin():
                connection.execute(text(query))
        log_to_console(f"Successfully executed SQL query.", "DEBUG")
        return True
    except Exception as e:
        log_to_console(f"Error executing SQL query: {e}", "ERROR")
        return False


# Application State
application_state = {
    "db_connected": False,
    "dataset_ready": False,
    "model_trained": False,
    "metrics": {},
    "app_version": "2025.07.27.2",  # Updated version for this change
    "model_features": [],
    "model_features_mean": {},
    "schools_df": pd.DataFrame(),
    "parents_df": pd.DataFrame(),
    "students_df": pd.DataFrame(),
    "student_years_df": pd.DataFrame(),
    "subjects_df": pd.DataFrame(),
    "academic_records_df": pd.DataFrame(),
    "attendance_df": pd.DataFrame(),
    "combined_dataset": pd.DataFrame(),
    "first_names": [],  # For parent/student generation
    "last_names": [],  # For parent/student generation
}


def update_app_state(key, value):
    """Updates a key in the application state and logs the change."""
    old_value = application_state.get(key)
    application_state[key] = value
    if old_value != value:
        log_to_console(f"Application State Updated: {key}={value}", "INFO")


# --- Database Schema and Data Management ---
def create_tables_if_not_exist(engine):
    """
    Ensures all necessary tables exist by creating them only if they do not already exist.
    This version uses SQL Server's OBJECT_ID to check for existence before creating.
    """
    log_to_console("Checking and creating database tables (if not exist)...", "INFO")

    table_schemas = {
        "gender_lookup": """
            CREATE TABLE gender_lookup (
                gender_id INT PRIMARY KEY IDENTITY(1,1),
                gender_name NVARCHAR(50) NOT NULL UNIQUE,
                last_update_date DATETIME DEFAULT GETDATE(),
                last_update_userid NVARCHAR(50) NOT NULL
            );
        """,
        "school_type_lookup": """
            CREATE TABLE school_type_lookup (
                type_id INT PRIMARY KEY IDENTITY(1,1),
                type_name NVARCHAR(50) NOT NULL UNIQUE,
                last_update_date DATETIME DEFAULT GETDATE(),
                last_update_userid NVARCHAR(50) NOT NULL
            );
        """,
        "province_lookup": """
            CREATE TABLE province_lookup (
                province_id INT PRIMARY KEY IDENTITY(1,1),
                province_name NVARCHAR(100) NOT NULL UNIQUE,
                last_update_date DATETIME DEFAULT GETDATE(),
                last_update_userid NVARCHAR(50) NOT NULL
            );
        """,
        "district_lookup": """
            CREATE TABLE district_lookup (
                district_id INT PRIMARY KEY IDENTITY(1,1),
                district_name NVARCHAR(100) NOT NULL UNIQUE,
                last_update_date DATETIME DEFAULT GETDATE(),
                last_update_userid NVARCHAR(50) NOT NULL
            );
        """,
        "quintile_lookup": """
            CREATE TABLE quintile_lookup (
                quintile_id INT PRIMARY KEY IDENTITY(1,1),
                quintile_value INT NOT NULL UNIQUE,
                last_update_date DATETIME DEFAULT GETDATE(),
                last_update_userid NVARCHAR(50) NOT NULL
            );
        """,
        "subject_lookup": """
            CREATE TABLE subject_lookup (
                subject_id INT PRIMARY KEY IDENTITY(1,1),
                subject_name NVARCHAR(100) NOT NULL UNIQUE,
                last_update_date DATETIME DEFAULT GETDATE(),
                last_update_userid NVARCHAR(50) NOT NULL
            );
        """,
        "academic_assessment_type_lookup": """
            CREATE TABLE academic_assessment_type_lookup (
                type_id INT PRIMARY KEY IDENTITY(1,1),
                type_name NVARCHAR(100) NOT NULL UNIQUE,
                last_update_date DATETIME DEFAULT GETDATE(),
                last_update_userid NVARCHAR(50) NOT NULL
            );
        """,
        "attendance_status_lookup": """
            CREATE TABLE attendance_status_lookup (
                status_id INT PRIMARY KEY IDENTITY(1,1),
                status_name NVARCHAR(50) NOT NULL UNIQUE,
                last_update_date DATETIME DEFAULT GETDATE(),
                last_update_userid NVARCHAR(50) NOT NULL
            );
        """,
        "socio_economic_status_lookup": """
            CREATE TABLE socio_economic_status_lookup (
                status_id INT PRIMARY KEY IDENTITY(1,1),
                status_name NVARCHAR(50) NOT NULL UNIQUE,
                last_update_date DATETIME DEFAULT GETDATE(),
                last_update_userid NVARCHAR(50) NOT NULL
            );
        """,
        "home_environment_lookup": """
            CREATE TABLE home_environment_lookup (
                environment_id INT PRIMARY KEY IDENTITY(1,1),
                environment_name NVARCHAR(100) NOT NULL UNIQUE,
                last_update_date DATETIME DEFAULT GETDATE(),
                last_update_userid NVARCHAR(50) NOT NULL
            );
        """,
        "internet_access_lookup": """
            CREATE TABLE internet_access_lookup (
                access_id INT PRIMARY KEY IDENTITY(1,1),
                access_type NVARCHAR(100) NOT NULL UNIQUE,
                last_update_date DATETIME DEFAULT GETDATE(),
                last_update_userid NVARCHAR(50) NOT NULL
            );
        """,
        "study_habits_lookup": """
            CREATE TABLE study_habits_lookup (
                habit_id INT PRIMARY KEY IDENTITY(1,1),
                habit_name NVARCHAR(100) NOT NULL UNIQUE,
                last_update_date DATETIME DEFAULT GETDATE(),
                last_update_userid NVARCHAR(50) NOT NULL
            );
        """,
        "extracurricular_engagement_lookup": """
            CREATE TABLE extracurricular_engagement_lookup (
                engagement_id INT PRIMARY KEY IDENTITY(1,1),
                engagement_type NVARCHAR(100) NOT NULL UNIQUE,
                last_update_date DATETIME DEFAULT GETDATE(),
                last_update_userid NVARCHAR(50) NOT NULL
            );
        """,
        "health_nutrition_lookup": """
            CREATE TABLE health_nutrition_lookup (
                status_id INT PRIMARY KEY IDENTITY(1,1),
                status_name NVARCHAR(100) NOT NULL UNIQUE,
                last_update_date DATETIME DEFAULT GETDATE(),
                last_update_userid NVARCHAR(50) NOT NULL
            );
        """,
        "special_needs_support_lookup": """
            CREATE TABLE special_needs_support_lookup (
                support_id INT PRIMARY KEY IDENTITY(1,1),
                support_type NVARCHAR(50) NOT NULL UNIQUE,
                last_update_date DATETIME DEFAULT GETDATE(),
                last_update_userid NVARCHAR(50) NOT NULL
            );
        """,
        "intervention_type_lookup": """
            CREATE TABLE intervention_type_lookup (
                type_id INT PRIMARY KEY IDENTITY(1,1),
                type_name NVARCHAR(100) NOT NULL UNIQUE,
                last_update_date DATETIME DEFAULT GETDATE(),
                last_update_userid NVARCHAR(50) NOT NULL
            );
        """,
        "first_names_lookup": """
            CREATE TABLE first_names_lookup (
                id INT PRIMARY KEY IDENTITY(1,1),
                first_name NVARCHAR(100) NOT NULL UNIQUE
            );
        """,
        "last_names_lookup": """
            CREATE TABLE last_names_lookup (
                id INT PRIMARY KEY IDENTITY(1,1),
                last_name NVARCHAR(100) NOT NULL UNIQUE
            );
        """,
        # Core tables
        "schools": """
            CREATE TABLE schools (
                school_id NVARCHAR(50) PRIMARY KEY, -- Changed to NVARCHAR(50) for UUID
                school_name NVARCHAR(255) NOT NULL,
                school_type NVARCHAR(50),
                province NVARCHAR(100),
                district NVARCHAR(100),
                quintile INT,
                contact_person NVARCHAR(255),
                contact_email NVARCHAR(255),
                contact_phone NVARCHAR(50),
                InfrastructureScore INT, -- Added from appl.py
                TeacherAbsenteeismRate DECIMAL(5,2), -- Added from appl.py
                last_update_date DATETIME DEFAULT GETDATE(),
                last_update_userid NVARCHAR(50) NOT NULL
            );
        """,
        "parents": """
            CREATE TABLE parents (
                parent_id NVARCHAR(50) PRIMARY KEY, -- Changed to NVARCHAR(50) for UUID
                first_name NVARCHAR(100) NOT NULL,
                last_name NVARCHAR(100) NOT NULL,
                contact_email NVARCHAR(255),
                contact_phone NVARCHAR(50),
                address NVARCHAR(255),
                city NVARCHAR(100), -- Added from appl.py
                state NVARCHAR(100), -- Added from appl.py
                zip_code NVARCHAR(20), -- Added from appl.py
                socio_economic_status NVARCHAR(50), -- Existing in app.py
                last_update_date DATETIME DEFAULT GETDATE(),
                last_update_userid NVARCHAR(50) NOT NULL
            );
        """,
        "users": """
            CREATE TABLE users (
                user_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                username NVARCHAR(255) NOT NULL UNIQUE,
                password NVARCHAR(255) NOT NULL,
                role NVARCHAR(50) NOT NULL,
                last_update_date DATETIME DEFAULT GETDATE(),
                last_update_userid NVARCHAR(50) NOT NULL
            );
        """,
        "chatbot_knowledge_base": """
            CREATE TABLE chatbot_knowledge_base (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                question_category NVARCHAR(50),
                question NVARCHAR(MAX) NOT NULL,
                answer NVARCHAR(MAX) NOT NULL,
                last_update_date DATETIME DEFAULT GETDATE(),
                last_update_userid NVARCHAR(50) NOT NULL
            );
        """,
        "students": """
            CREATE TABLE students (
                student_id NVARCHAR(50) PRIMARY KEY,
                first_name NVARCHAR(100) NOT NULL,
                last_name NVARCHAR(100) NOT NULL,
                date_of_birth DATE,
                gender NVARCHAR(50),
                race NVARCHAR(50), -- Added from appl.py
                has_social_grant BIT, -- Added from appl.py
                enrollment_date DATE,
                school_id NVARCHAR(50), -- Changed to NVARCHAR(50)
                parent_id NVARCHAR(50), -- Changed to NVARCHAR(50)
                current_grade INT,
                home_environment NVARCHAR(100),
                internet_access NVARCHAR(100),
                study_habits NVARCHAR(100),
                extracurricular_engagement NVARCHAR(100),
                health_nutrition NVARCHAR(100),
                special_needs_support NVARCHAR(50),
                last_update_date DATETIME DEFAULT GETDATE(),
                last_update_userid NVARCHAR(50) NOT NULL,
                FOREIGN KEY (school_id) REFERENCES schools(school_id),
                FOREIGN KEY (parent_id) REFERENCES parents(parent_id)
            );
        """,
        "student_years": """
            CREATE TABLE student_years (
                student_year_id NVARCHAR(50) PRIMARY KEY,
                student_id NVARCHAR(50) NOT NULL,
                academic_year INT NOT NULL,
                grade INT,
                school_id NVARCHAR(50), -- Changed to NVARCHAR(50)
                enrollment_date DATE, -- Added from appl.py
                status NVARCHAR(50), -- Added from appl.py
                last_update_date DATETIME DEFAULT GETDATE(),
                last_update_userid NVARCHAR(50) NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                FOREIGN KEY (school_id) REFERENCES schools(school_id)
            );
        """,
        "academic_records": """
            CREATE TABLE academic_records (
                record_id NVARCHAR(50) PRIMARY KEY, -- Changed to NVARCHAR(50) for UUID
                student_id NVARCHAR(50) NOT NULL,
                school_id NVARCHAR(50), -- Added from appl.py (FK to schools)
                subject_name NVARCHAR(100), -- Existing in app.py
                assessment_type NVARCHAR(100), -- Existing in app.py (maps to Term in appl.py
                mark DECIMAL(5,2), -- Existing in app.py (maps to Result in appl.py)
                assessment_date DATE,
                academic_year INT,
                last_update_date DATETIME DEFAULT GETDATE(),
                last_update_userid NVARCHAR(50) NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                FOREIGN KEY (school_id) REFERENCES schools(school_id)
            );
        """,
        "attendance_records": """
            CREATE TABLE attendance_records (
                attendance_id NVARCHAR(50) PRIMARY KEY, -- Changed to NVARCHAR(50) for UUID
                student_id NVARCHAR(50) NOT NULL,
                school_id NVARCHAR(50), -- Added from appl.py (FK to schools)
                record_date DATE NOT NULL, -- Existing in app.py (maps to AttendanceDate)
                status NVARCHAR(50), -- Existing in app.py (maps to Status BIT)
                reason NVARCHAR(255), -- Existing in app.py
                last_update_date DATETIME DEFAULT GETDATE(),
                last_update_userid NVARCHAR(50) NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                FOREIGN KEY (school_id) REFERENCES schools(school_id)
            );
        """,
        "intervention_recommendations": """
            CREATE TABLE intervention_recommendations (
                recommendation_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                student_id NVARCHAR(50) NOT NULL,
                recommended_action NVARCHAR(500) NOT NULL,
                reason NVARCHAR(MAX),
                recommendation_date DATETIME DEFAULT GETDATE(),
                last_update_date DATETIME DEFAULT GETDATE(),
                last_update_userid NVARCHAR(50) NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students(student_id)
            );
        """,
    }

    ordered_tables = [
        "gender_lookup",
        "school_type_lookup",
        "province_lookup",
        "district_lookup",
        "quintile_lookup",
        "subject_lookup",
        "academic_assessment_type_lookup",
        "attendance_status_lookup",
        "socio_economic_status_lookup",
        "home_environment_lookup",
        "internet_access_lookup",
        "study_habits_lookup",
        "extracurricular_engagement_lookup",
        "health_nutrition_lookup",
        "special_needs_support_lookup",
        "intervention_type_lookup",
        "first_names_lookup",
        "last_names_lookup",  # New lookup tables
        "schools",
        "parents",
        "users",
        "chatbot_knowledge_base",
        "students",
        "student_years",
        "academic_records",
        "attendance_records",
        "intervention_recommendations",
    ]

    with engine.connect() as connection:
        with connection.begin():
            cursor = connection.connection.cursor()
            try:
                for table_name in ordered_tables:
                    try:
                        cursor.execute(f"SELECT OBJECT_ID(N'{table_name}', 'U');")
                        table_exists = cursor.fetchone()[0] is not None
                        if not table_exists:
                            log_to_console(f"Creating table: {table_name}", "INFO")
                            schema = table_schemas[table_name]
                            cursor.execute(schema)
                            log_to_console(
                                f"Table {table_name} created successfully.", "INFO"
                            )
                        else:
                            log_to_console(
                                f"Table {table_name} already exists, skipping creation.",
                                "INFO",
                            )
                    except Exception as e:
                        log_to_console(
                            f"Error creating table {table_name}: {e}", "ERROR"
                        )
                        raise
            finally:
                cursor.close()


def populate_lookup_tables(engine):
    """Populates all lookup tables with predefined data using SQLAlchemy engine."""
    log_to_console("Checking and populating lookup tables on startup...", "INFO")
    default_userid_system = "system"

    lookups = {
        "gender_lookup": {
            "column": "gender_name",
            "values": ["Male", "Female", "Other"],
        },
        "school_type_lookup": {
            "column": "type_name",
            "values": ["Primary", "Secondary", "Combined"],
        },
        "province_lookup": {
            "column": "province_name",
            "values": [
                "Gauteng",
                "Western Cape",
                "KwaZulu-Natal",
                "Eastern Cape",
                "Limpopo",
                "Mpumalanga",
                "North West",
                "Northern Cape",
                "Free State",
            ],
        },
        "district_lookup": {
            "column": "district_name",
            "values": [
                "Johannesburg North",
                "Cape Winelands",
                "eThekwini",
                "Nelson Mandela Bay",
                "Capricorn",
                "Ehlanzeni",
                "Dr Kenneth Kaunda",
                "Frances Baard",
                "Mangaung",
            ],
        },
        "quintile_lookup": {"column": "quintile_value", "values": [1, 2, 3, 4, 5]},
        "subject_lookup": {
            "column": "subject_name",
            "values": [
                "Mathematics",
                "English Home Language",
                "Afrikaans",
                "IsiZulu",
                "Physical Sciences",
                "Life Sciences",
                "History",
                "Geography",
                "Accounting",
                "Business Studies",
                "Computer Applications Technology",
            ],
        },
        "academic_assessment_type_lookup": {
            "column": "type_name",
            "values": ["Assignment", "Test", "Exam", "Project"],
        },
        "attendance_status_lookup": {
            "column": "status_name",
            "values": ["Present", "Absent", "Late"],
        },
        "socio_economic_status_lookup": {
            "column": "status_name",
            "values": ["Low", "Medium", "High"],
        },
        "home_environment_lookup": {
            "column": "environment_name",
            "values": ["Supportive", "Challenging", "Neutral"],
        },
        "internet_access_lookup": {
            "column": "access_type",
            "values": ["No Access", "Limited Access", "Reliable Access"],
        },
        "study_habits_lookup": {
            "column": "habit_name",
            "values": ["Excellent", "Good", "Average", "Poor"],
        },
        "extracurricular_engagement_lookup": {
            "column": "engagement_type",
            "values": ["High", "Medium", "Low", "None"],
        },
        "health_nutrition_lookup": {
            "column": "status_name",
            "values": ["Good", "Average", "Poor"],
        },
        "special_needs_support_lookup": {
            "column": "support_type",
            "values": ["Yes", "No"],
        },
        "intervention_type_lookup": {
            "column": "type_name",
            "values": [
                "Academic Support",
                "Behavioral Intervention",
                "Health Support",
                "Counseling",
            ],
        },
        "first_names_lookup": {
            "column": "first_name",
            "values": [
                "Alice",
                "Bob",
                "Charlie",
                "Diana",
                "Eve",
                "Frank",
                "Grace",
                "Heidi",
                "Nomusa",
                "Sipho",
                "Thandi",
                "Lebo",
                "Khaya",
                "Zodwa",
                "Bongani",
                "Ayanda",
            ],
        },
        "last_names_lookup": {
            "column": "last_name",
            "values": [
                "Smith",
                "Jones",
                "Williams",
                "Brown",
                "Davis",
                "Miller",
                "Wilson",
                "Moore",
                "Dlamini",
                "Zulu",
                "Mokoena",
                "Khumalo",
                "Nxumalo",
                "Sithole",
                "Ndlovu",
                "Gumede",
            ],
        },
    }

    with engine.connect() as connection:
        with connection.begin():
            cursor = connection.connection.cursor()
            try:
                for table, info in lookups.items():
                    column_name = info["column"]
                    values = info["values"]
                    for value in values:
                        try:
                            cursor.execute(f"SELECT OBJECT_ID(N'{table}', 'U');")
                            table_exists = cursor.fetchone()[0] is not None
                            if not table_exists:
                                log_to_console(
                                    f"Table {table} does not exist, skipping lookup population.",
                                    "WARNING",
                                )
                                continue
                            cursor.execute(
                                f"SELECT COUNT(*) FROM {table} WHERE {column_name} = ?",
                                (value,),
                            )
                            exists = cursor.fetchone()[0]
                            if exists == 0:
                                cursor.execute(
                                    f"INSERT INTO {table} ({column_name}, last_update_date, last_update_userid) VALUES (?, GETDATE(), ?)",
                                    (value, default_userid_system),
                                )
                                log_to_console(
                                    f"Inserted into {table} ({column_name}): {value}",
                                    "INFO",
                                )
                            else:
                                log_to_console(
                                    f"Skipping existing entry in {table} ({column_name}): {value}",
                                    "INFO",
                                )
                        except Exception as e:
                            log_to_console(
                                f"Error inserting into {table} ({column_name}): {e}",
                                "ERROR",
                            )
                            raise
            finally:
                cursor.close()


def populate_chatbot_knowledge_base(engine):
    """Checks if the chatbot knowledge base is populated."""
    log_to_console("Checking chatbot knowledge base status...", "INFO")
    with engine.connect() as connection:
        cursor = connection.connection.cursor()
        try:
            cursor.execute(f"SELECT OBJECT_ID(N'chatbot_knowledge_base', 'U');")
            table_exists = cursor.fetchone()[0] is not None
            if not table_exists:
                log_to_console(
                    f"Table chatbot_knowledge_base does not exist, skipping chatbot knowledge base check.",
                    "WARNING",
                )
                return
            cursor.execute("SELECT COUNT(*) FROM chatbot_knowledge_base;")
            count = cursor.fetchone()[0]
            if count == 0:
                log_to_console(
                    "Chatbot knowledge base table is empty. Please populate it with questions and answers.",
                    "WARNING",
                )
                add_response_to_queue(
                    "Chatbot knowledge base is empty. Please populate the 'chatbot_knowledge_base' table directly with questions and answers.",
                    "warning",
                )
            else:
                log_to_console(
                    f"Chatbot knowledge base has {count} entries and is ready.", "INFO"
                )
        except Exception as e:
            log_to_console(f"Error checking chatbot knowledge base table: {e}", "ERROR")
            add_response_to_queue(f"Chatbot knowledge base error: {e}", "error")
        finally:
            cursor.close()


def get_foreign_keys_on_tables(cursor, table_names):
    """Gets foreign keys defined ON the given tables."""
    fk_list = []
    for table_name in table_names:
        query = f"""
            SELECT
                fk.name AS foreign_key_name,
                OBJECT_NAME(fk.parent_object_id) AS table_name
            FROM sys.foreign_keys AS fk
            WHERE OBJECT_NAME(fk.parent_object_id) = '{table_name}';
        """
        cursor.execute(query)
        fks = cursor.fetchall()
        fk_list.extend(fks)
    return fk_list


def get_foreign_keys_referencing_tables(cursor, referenced_table_names):
    """Gets foreign keys that REFERENCE the given tables."""
    fk_list = []
    for referenced_table_name in referenced_table_names:
        query = f"""
            SELECT
                fk.name AS foreign_key_name,
                OBJECT_NAME(fk.parent_object_id) AS table_name
            FROM sys.foreign_keys AS fk
            WHERE OBJECT_NAME(fk.referenced_object_id) = '{referenced_table_name}';
        """
        cursor.execute(query)
        fks = cursor.fetchall()
        fk_list.extend(fks)
    return fk_list


def disable_foreign_key(cursor, table_name, fk_name):
    """Disables a specific foreign key constraint."""
    try:
        sql = f"ALTER TABLE {table_name} NOCHECK CONSTRAINT {fk_name};"
        cursor.execute(sql)
        log_to_console(f"Disabled foreign key: {fk_name} on {table_name}", "INFO")
    except Exception as e:
        log_to_console(
            f"Error disabling foreign key {fk_name} on {table_name}: {e}", "ERROR"
        )
        raise


def enable_foreign_key(cursor, table_name, fk_name):
    """Enables a specific foreign key constraint."""
    try:
        sql = f"ALTER TABLE {table_name} CHECK CONSTRAINT {fk_name};"
        cursor.execute(sql)
        log_to_console(f"Enabled foreign key: {fk_name} on {table_name}", "INFO")
    except Exception as e:
        log_to_console(
            f"Error enabling foreign key {fk_name} on {table_name}: {e}", "ERROR"
        )
        raise


def clear_all_data_internal():
    log_to_console("Starting clear_all_data_internal...", "DEBUG")
    engine = get_db_connection()
    if engine is None:
        return {"status": "error", "message": "Database connection not available."}

    with engine.connect() as connection:
        with connection.begin():
            cursor = connection.connection.cursor()
            fk_names_to_manage = []
            try:
                tables_to_clear_order = [
                    "academic_records",
                    "attendance_records",
                    "student_years",
                    "students",
                    "parents",
                    "schools",
                ]

                fk_names_on_cleared_tables = get_foreign_keys_on_tables(
                    cursor, tables_to_clear_order
                )
                fk_names_to_manage.extend(fk_names_on_cleared_tables)

                fk_names_referencing_cleared_tables = (
                    get_foreign_keys_referencing_tables(cursor, ["students"])
                )
                fk_names_to_manage.extend(fk_names_referencing_cleared_tables)

                fk_names_to_manage = list(set(fk_names_to_manage))

                log_to_console(f"Foreign keys to disable: {fk_names_to_manage}", "INFO")
                for fk_name, table_name in fk_names_to_manage:
                    disable_foreign_key(cursor, table_name, fk_name)

                for table_name in tables_to_clear_order:
                    cursor.execute(f"SELECT OBJECT_ID(N'{table_name}', 'U');")
                    table_exists = cursor.fetchone()[0] is not None
                    if table_exists:
                        cursor.execute(f"TRUNCATE TABLE {table_name}")
                        log_to_console(f"Truncated table: {table_name}", "INFO")
                    else:
                        log_to_console(
                            f"Table {table_name} does not exist, skipping truncation.",
                            "WARNING",
                        )

                log_to_console(f"Foreign keys to enable: {fk_names_to_manage}", "INFO")
                for fk_name, table_name in fk_names_to_manage:
                    enable_foreign_key(cursor, table_name, fk_name)

            except Exception as e:
                log_to_console(f"Error during clear_all_data_internal: {e}", "ERROR")
                for fk_name, table_name in fk_names_to_manage:
                    try:
                        enable_foreign_key(cursor, table_name, fk_name)
                    except Exception as re_enable_e:
                        log_to_console(
                            f"Error re-enabling FK {fk_name} on {table_name} during error handling: {re_enable_e}",
                            "CRITICAL",
                        )
                raise
            finally:
                cursor.close()
    update_app_state("dataset_ready", False)
    update_app_state("model_trained", False)
    application_state["metrics"] = {}
    application_state["schools_df"] = pd.DataFrame()
    application_state["parents_df"] = pd.DataFrame()
    application_state["students_df"] = pd.DataFrame()
    application_state["student_years_df"] = pd.DataFrame()
    application_state["academic_records_df"] = pd.DataFrame()
    application_state["attendance_df"] = pd.DataFrame()
    application_state["combined_dataset"] = pd.DataFrame()
    return {
        "status": "success",
        "message": "Selected generated data cleared and schema reset (other tables preserved).",
    }


# --- Data Generation Functions (Adapted from appl.py) ---


def generate_schools(num_schools, app_state_instance):
    log_to_console(f"Generating {num_schools} school records...", "INFO")
    schools = []
    quintile_distribution = {1: 0.25, 2: 0.25, 3: 0.20, 4: 0.15, 5: 0.15}
    quintiles = random.choices(
        list(quintile_distribution.keys()),
        weights=list(quintile_distribution.values()),
        k=num_schools,
    )

    provinces = {
        "KwaZulu-Natal": 0.20,
        "Gauteng": 0.15,
        "Limpopo": 0.15,
        "Eastern Cape": 0.15,
        "Western Cape": 0.10,
        "Mpumalanga": 0.10,
        "North West": 0.05,
        "Free State": 0.05,
        "Northern Cape": 0.05,
    }
    province_names = list(provinces.keys())
    province_weights = list(provinces.values())

    for i in range(num_schools):
        school_id = f"SCH{str(uuid.uuid4()).replace('-', '')[:10].upper()}"  # Use UUID for consistency with app.py
        school_name = (
            f"School {i+1} {random.choice(['Primary', 'Secondary', 'High', 'College'])}"
        )
        school_type = "Primary" if i % 2 == 0 else "Secondary"
        province = np.random.choice(province_names, p=province_weights)
        district_lookup = read_table_to_dataframe(
            app_state_instance.engine, "district_lookup"
        )
        districts = (
            district_lookup["district_name"].tolist()
            if not district_lookup.empty
            else ["Unknown District"]
        )
        district = random.choice(districts)
        quintile = quintiles[i]
        contact_person = f"Admin {i+1}"
        contact_email = f"info.school{i+1}@example.com"
        contact_phone = f"0{random.randint(100000000, 999999999)}"

        if quintile in [1, 2]:
            infrastructure_score = random.randint(40, 65)
            teacher_absenteeism_rate = round(random.uniform(0.05, 0.15), 2)
        elif quintile == 3:
            infrastructure_score = random.randint(60, 80)
            teacher_absenteeism_rate = round(random.uniform(0.03, 0.08), 2)
        else:
            infrastructure_score = random.randint(75, 95)
            teacher_absenteeism_rate = round(random.uniform(0.01, 0.05), 2)

        schools.append(
            {
                "school_id": school_id,
                "school_name": school_name,
                "school_type": school_type,
                "province": province,
                "district": district,
                "quintile": quintile,
                "contact_person": contact_person,
                "contact_email": contact_email,
                "contact_phone": contact_phone,
                "InfrastructureScore": infrastructure_score,
                "TeacherAbsenteeismRate": teacher_absenteeism_rate,
                "last_update_date": datetime.now(),
                "last_update_userid": "system_gen",
            }
        )
    log_to_console(f"Generated {num_schools} school records.", "INFO")
    return pd.DataFrame(schools)


def generate_parents(num_parents, app_state_instance):
    log_to_console(f"Generating {num_parents} parent records...", "INFO")
    parents = []

    first_names_list = app_state_instance.first_names
    last_names_list = app_state_instance.last_names

    if not first_names_list:
        log_to_console(
            "First names list is empty. Using a very limited fallback for parent generation.",
            "WARNING",
        )
        first_names_list = ["John", "Jane"]
    if not last_names_list:
        log_to_console(
            "Last names list is empty. Using a very limited fallback for parent generation.",
            "WARNING",
        )
        last_names_list = ["Doe", "Smith"]

    socio_economic_statuses_lookup = read_table_to_dataframe(
        app_state_instance.engine, "socio_economic_status_lookup"
    )
    socio_economic_statuses = (
        socio_economic_statuses_lookup["status_name"].tolist()
        if not socio_economic_statuses_lookup.empty
        else ["Medium"]
    )

    for i in range(num_parents):
        parent_id = f"PAR{str(uuid.uuid4()).replace('-', '')[:10].upper()}"  # Use UUID for consistency with app.py
        first_name = random.choice(first_names_list)
        last_name = random.choice(last_names_list)
        contact_email = f"{first_name.lower()}.{last_name.lower()}{i}@example.com"
        contact_phone = f"0{random.randint(100000000, 999999999)}"
        address = f"{random.randint(1, 999)} Oak Ave"
        city = random.choice(["Johannesburg", "Cape Town", "Durban", "Pretoria"])
        state = random.choice(["GP", "WC", "KZN", "EC", "LP", "MP", "NW", "NC", "FS"])
        zip_code = f"{random.randint(1000, 9999)}"
        socio_economic_status = random.choice(socio_economic_statuses)

        parents.append(
            {
                "parent_id": parent_id,
                "first_name": first_name,
                "last_name": last_name,
                "contact_email": contact_email,
                "contact_phone": contact_phone,
                "address": address,
                "city": city,
                "state": state,
                "zip_code": zip_code,
                "socio_economic_status": socio_economic_status,
                "last_update_date": datetime.now(),
                "last_update_userid": "system_gen",
            }
        )
    log_to_console(f"Generated {num_parents} parent records.", "INFO")
    return pd.DataFrame(parents)


def generate_students_and_initial_enrollments(
    schools_df, parents_df, num_students, app_state_instance
):
    log_to_console(
        f"Generating {num_students} student records and initial enrollments...", "INFO"
    )
    students_data = []
    student_years_data = []
    current_year = datetime.now().year

    if schools_df.empty:
        log_to_console("Schools DataFrame is empty. Cannot generate students.", "ERROR")
        return pd.DataFrame(), pd.DataFrame()
    if parents_df.empty:
        log_to_console("Parents DataFrame is empty. Cannot generate students.", "ERROR")
        return pd.DataFrame(), pd.DataFrame()

    school_ids = schools_df["school_id"].tolist()
    parent_ids = parents_df["parent_id"].tolist()

    # Fetch lookup data for student attributes
    genders_lookup = read_table_to_dataframe(app_state_instance.engine, "gender_lookup")
    genders = (
        genders_lookup["gender_name"].tolist()
        if not genders_lookup.empty
        else ["Male", "Female"]
    )
    home_environments_lookup = read_table_to_dataframe(
        app_state_instance.engine, "home_environment_lookup"
    )
    home_environments = (
        home_environments_lookup["environment_name"].tolist()
        if not home_environments_lookup.empty
        else ["Supportive", "Neutral"]
    )
    internet_access_lookup = read_table_to_dataframe(
        app_state_instance.engine, "internet_access_lookup"
    )
    internet_access_types = (
        internet_access_lookup["access_type"].tolist()
        if not internet_access_lookup.empty
        else ["No Access", "Reliable Access"]
    )
    study_habits_lookup = read_table_to_dataframe(
        app_state_instance.engine, "study_habits_lookup"
    )
    study_habits = (
        study_habits_lookup["habit_name"].tolist()
        if not study_habits_lookup.empty
        else ["Average", "Good"]
    )
    extracurricular_engagement_lookup = read_table_to_dataframe(
        app_state_instance.engine, "extracurricular_engagement_lookup"
    )
    extracurricular_engagements = (
        extracurricular_engagement_lookup["engagement_type"].tolist()
        if not extracurricular_engagement_lookup.empty
        else ["Low", "Medium"]
    )
    health_nutrition_lookup = read_table_to_dataframe(
        app_state_instance.engine, "health_nutrition_lookup"
    )
    health_nutrition_statuses = (
        health_nutrition_lookup["status_name"].tolist()
        if not health_nutrition_lookup.empty
        else ["Good", "Average"]
    )
    special_needs_support_lookup = read_table_to_dataframe(
        app_state_instance.engine, "special_needs_support_lookup"
    )
    special_needs_supports = (
        special_needs_support_lookup["support_type"].tolist()
        if not special_needs_support_lookup.empty
        else ["No", "Yes"]
    )

    race_distribution = {
        "Black African": 0.80,
        "White": 0.085,
        "Coloured": 0.09,
        "Indian": 0.025,
    }
    races = random.choices(
        list(race_distribution.keys()),
        weights=list(race_distribution.values()),
        k=num_students,
    )

    province_grant_ratios = {  # Using simplified ratios
        "KwaZulu-Natal": 0.7,
        "Gauteng": 0.6,
        "Limpopo": 0.7,
        "Eastern Cape": 0.65,
        "Western Cape": 0.5,
        "Mpumalanga": 0.65,
        "North West": 0.6,
        "Free State": 0.6,
        "Northern Cape": 0.55,
    }

    for i in range(num_students):
        student_id = f"STU{str(uuid.uuid4()).replace('-', '')[:10].upper()}"
        first_name = random.choice(app_state_instance.first_names)
        last_name = random.choice(app_state_instance.last_names)
        dob = datetime(
            random.randint(current_year - 18, current_year - 5),
            random.randint(1, 12),
            random.randint(1, 28),
        )
        gender = random.choice(genders)
        race = races[i]

        school_id = random.choice(school_ids)
        school_province = schools_df[schools_df["school_id"] == school_id][
            "province"
        ].iloc[0]
        has_social_grant = False
        if (
            school_province in province_grant_ratios
            and random.random() < province_grant_ratios[school_province]
        ):
            has_social_grant = True

        parent_id = random.choice(
            parent_ids
        )  # Assign a single parent_id as per app.py schema

        age = current_year - dob.year
        current_grade = min(12, max(1, age - 5))
        enrollment_date = datetime(current_year, 1, 1).strftime("%Y-%m-%d")

        students_data.append(
            {
                "student_id": student_id,
                "first_name": first_name,
                "last_name": last_name,
                "date_of_birth": dob.strftime("%Y-%m-%d"),
                "gender": gender,
                "race": race,
                "has_social_grant": has_social_grant,
                "enrollment_date": enrollment_date,
                "school_id": school_id,
                "parent_id": parent_id,
                "current_grade": current_grade,
                "home_environment": random.choice(home_environments),
                "internet_access": random.choice(internet_access_types),
                "study_habits": random.choice(study_habits),
                "extracurricular_engagement": random.choice(
                    extracurricular_engagements
                ),
                "health_nutrition": random.choice(health_nutrition_statuses),
                "special_needs_support": random.choice(special_needs_supports),
                "last_update_date": datetime.now(),
                "last_update_userid": "system_gen",
            }
        )

        student_years_data.append(
            {
                "student_year_id": f"SY{str(uuid.uuid4()).replace('-', '')[:10].upper()}",
                "student_id": student_id,
                "school_id": school_id,
                "academic_year": current_year,
                "grade": current_grade,
                "enrollment_date": enrollment_date,
                "status": "Enrolled",
                "last_update_date": datetime.now(),
                "last_update_userid": "system_gen",
            }
        )
    log_to_console(
        f"Generated {num_students} student records and initial enrollments.", "INFO"
    )
    return pd.DataFrame(students_data), pd.DataFrame(student_years_data)


def generate_academic_records(
    students_df, subjects_df, start_year, end_year, app_state_instance
):
    log_to_console("Generating academic records...", "INFO")
    academic_records = []

    if subjects_df.empty:
        log_to_console(
            "Warning: No subjects found in the database. Academic records cannot be generated.",
            "WARNING",
        )
        return pd.DataFrame()

    all_subject_names = subjects_df["subject_name"].tolist()
    assessment_types_lookup = read_table_to_dataframe(
        app_state_instance.engine, "academic_assessment_type_lookup"
    )
    assessment_types = (
        assessment_types_lookup["type_name"].tolist()
        if not assessment_types_lookup.empty
        else ["Assignment", "Test", "Exam"]
    )

    num_records_generated = 0
    total_students = len(students_df)

    for i, (_, student) in enumerate(students_df.iterrows()):
        student_id = student["student_id"]
        school_id = student["school_id"]
        dob = datetime.strptime(student["date_of_birth"], "%Y-%m-%d")

        school_info = app_state_instance.schools_df[
            app_state_instance.schools_df["school_id"] == school_id
        ]
        infrastructure_score = (
            school_info["InfrastructureScore"].iloc[0] if not school_info.empty else 70
        )
        teacher_absenteeism_rate = (
            school_info["TeacherAbsenteeismRate"].iloc[0]
            if not school_info.empty
            else 0.05
        )

        for year in range(start_year, end_year + 1):
            age_at_year = year - dob.year
            grade_for_year = min(12, max(1, age_at_year - 5))

            if grade_for_year < 1 or grade_for_year > 12:
                continue

            # Select subjects relevant to the current grade (simplified as all subjects are generally available)
            selected_subject_names = random.sample(
                all_subject_names, min(5, len(all_subject_names))
            )  # 5 subjects per year

            for subject_name in selected_subject_names:
                base_mark = random.randint(30, 90)
                adjusted_mark = (
                    base_mark
                    + (infrastructure_score - 70) * 0.2
                    - (teacher_absenteeism_rate * 100 * 0.5)
                )
                mark = round(
                    max(0, min(100, adjusted_mark + random.uniform(-10, 10))), 2
                )

                academic_records.append(
                    {
                        "record_id": f"REC{str(uuid.uuid4()).replace('-', '')[:10].upper()}",
                        "student_id": student_id,
                        "school_id": school_id,
                        "subject_name": subject_name,
                        "assessment_type": random.choice(assessment_types),
                        "mark": mark,
                        "assessment_date": datetime(
                            year, random.randint(1, 12), random.randint(1, 28)
                        ).strftime("%Y-%m-%d"),
                        "academic_year": year,
                        "last_update_date": datetime.now(),
                        "last_update_userid": "system_gen",
                    }
                )
                num_records_generated += 1

        if (i + 1) % 100 == 0 or (i + 1) == total_students:
            progress = int(((i + 1) / total_students) * 100)
            log_to_console(
                f"Generating academic records... ({i+1}/{total_students} students processed)",
                "INFO",
            )

    log_to_console(f"Generated {num_records_generated} academic records.", "INFO")
    return pd.DataFrame(academic_records)


def generate_attendance_records(students_df, start_year, end_year, app_state_instance):
    log_to_console("Generating attendance records...", "INFO")
    attendance_records = []
    total_students = len(students_df)

    attendance_statuses_lookup = read_table_to_dataframe(
        app_state_instance.engine, "attendance_status_lookup"
    )
    attendance_statuses = (
        attendance_statuses_lookup["status_name"].tolist()
        if not attendance_statuses_lookup.empty
        else ["Present", "Absent", "Late"]
    )

    num_records_generated = 0
    for i, (_, student) in enumerate(students_df.iterrows()):
        student_id = student["student_id"]
        school_id = student["school_id"]

        for year in range(start_year, end_year + 1):
            start_date = datetime(year, 1, 15)
            end_date = datetime(year, 12, 15)

            current_date = start_date
            while current_date <= end_date:
                if current_date.weekday() < 5:
                    status_name = random.choices(
                        attendance_statuses, weights=[0.9, 0.08, 0.02], k=1
                    )[0]
                    reason = "N/A"
                    if status_name == "Absent":
                        reason = random.choice(["Sick", "Family Emergency", "Other"])
                    elif status_name == "Late":
                        reason = random.choice(["Traffic", "Overslept", "Other"])

                    attendance_records.append(
                        {
                            "attendance_id": f"ATT{str(uuid.uuid4()).replace('-', '')[:10].upper()}",
                            "student_id": student_id,
                            "school_id": school_id,
                            "record_date": current_date.strftime("%Y-%m-%d"),
                            "status": status_name,
                            "reason": reason,
                            "last_update_date": datetime.now(),
                            "last_update_userid": "system_gen",
                        }
                    )
                    num_records_generated += 1
                current_date += timedelta(days=1)

        if (i + 1) % 100 == 0 or (i + 1) == total_students:
            progress = int(((i + 1) / total_students) * 100)
            log_to_console(
                f"Generating attendance records... ({i+1}/{total_students} students processed)",
                "INFO",
            )

    log_to_console(f"Generated {num_records_generated} attendance records.", "INFO")
    return pd.DataFrame(attendance_records)


def simulate_student_progression(
    students_df, student_years_df, start_year, end_year, app_state_instance
):
    log_to_console(
        "Simulating student progression and updating student_years records...", "INFO"
    )
    updated_student_years = student_years_df.copy()
    all_new_entries = []

    existing_enrollments = set(
        tuple(r)
        for r in updated_student_years[
            ["student_id", "academic_year", "grade"]
        ].to_numpy()
    )

    total_students = len(students_df)

    for i, (_, student) in enumerate(students_df.iterrows()):
        student_id = student["student_id"]
        student_enrollments = updated_student_years[
            updated_student_years["student_id"] == student_id
        ].sort_values(by="academic_year")

        if student_enrollments.empty:
            continue

        last_enrollment = student_enrollments.iloc[-1]
        last_academic_year = last_enrollment["academic_year"]
        last_grade = last_enrollment["grade"]
        last_school_id = last_enrollment["school_id"]
        last_enrollment_status = last_enrollment["status"]

        if (
            last_enrollment_status != "Dropped Out"
            and last_enrollment_status != "Graduated"
        ):
            for year in range(last_academic_year + 1, end_year + 1):
                if random.random() < DROPOUT_RATE_PER_YEAR:
                    all_new_entries.append(
                        {
                            "student_year_id": f"SY{str(uuid.uuid4()).replace('-', '')[:10].upper()}",
                            "student_id": student_id,
                            "school_id": last_school_id,
                            "academic_year": year,
                            "grade": last_grade,
                            "enrollment_date": datetime(year, 1, 1).strftime(
                                "%Y-%m-%d"
                            ),
                            "status": "Dropped Out",
                            "last_update_date": datetime.now(),
                            "last_update_userid": "system_gen",
                        }
                    )
                    break

                new_grade = last_grade
                status = "Enrolled"
                if random.random() < REPEATING_GRADE_CHANCE and new_grade < 12:
                    grade_repeats = student_enrollments[
                        (student_enrollments["academic_year"] < year)
                        & (student_enrollments["grade"] == last_grade)
                        & (student_enrollments["status"] == "Repeated")
                    ].shape[0]
                    if grade_repeats < MAX_REPEATS_PER_GRADE:
                        status = "Repeated"
                    else:
                        new_grade += 1
                else:
                    new_grade += 1

                if new_grade > 12:
                    status = "Graduated"
                    new_grade = 12

                new_entry_tuple = (student_id, year, new_grade)
                if new_entry_tuple not in existing_enrollments:
                    all_new_entries.append(
                        {
                            "student_year_id": f"SY{str(uuid.uuid4()).replace('-', '')[:10].upper()}",
                            "student_id": student_id,
                            "school_id": last_school_id,
                            "academic_year": year,
                            "grade": new_grade,
                            "enrollment_date": datetime(year, 1, 1).strftime(
                                "%Y-%m-%d"
                            ),
                            "status": status,
                            "last_update_date": datetime.now(),
                            "last_update_userid": "system_gen",
                        }
                    )
                    existing_enrollments.add(new_entry_tuple)

                last_grade = new_grade
                last_enrollment_status = status
                if status == "Graduated":
                    break

        if (i + 1) % 100 == 0 or (i + 1) == total_students:
            progress = int(((i + 1) / total_students) * 100)
            log_to_console(
                f"Simulating progression... ({i+1}/{total_students} students processed)",
                "INFO",
            )

    if all_new_entries:
        updated_student_years = pd.concat(
            [updated_student_years, pd.DataFrame(all_new_entries)], ignore_index=True
        )

    log_to_console(
        f"Simulated progression for {len(all_new_entries)} new student-year entries.",
        "INFO",
    )
    return updated_student_years


def combine_datasets(app_state_instance):
    """
    Combines all relevant DataFrames into a single, comprehensive dataset for ML.
    Performs necessary merges and feature engineering.
    """
    log_to_console("Combining datasets for machine learning...", "INFO")
    app_state_instance["current_status_message"] = (
        "Starting dataset combination: Merging students and parents..."
    )

    # 1. Merge Students with Parents and Schools
    combined_df = app_state_instance["students_df"].merge(
        app_state_instance["parents_df"]
        .rename(
            columns={
                "parent_id": "parent_id",  # Keep original name for merge
                "first_name": "parent_first_name",
                "last_name": "parent_last_name",
                "socio_economic_status": "parent_socio_economic_status",
            }
        )
        .drop(
            columns=[
                "contact_email",
                "contact_phone",
                "address",
                "city",
                "state",
                "zip_code",
                "last_update_date",
                "last_update_userid",
            ],
            errors="ignore",
        ),
        how="left",
        on="parent_id",
    )

    combined_df = combined_df.merge(
        app_state_instance["schools_df"]
        .rename(
            columns={
                "school_id": "school_id",  # Keep original name for merge
                "school_name": "current_school_name",
                "school_type": "current_school_type",
                "province": "current_school_province",
                "district": "current_school_district",
                "quintile": "current_school_quintile",
                "InfrastructureScore": "current_school_infrastructure_score",
                "TeacherAbsenteeismRate": "current_school_teacher_absenteeism_rate",
            }
        )
        .drop(
            columns=[
                "contact_person",
                "contact_email",
                "contact_phone",
                "last_update_date",
                "last_update_userid",
            ],
            errors="ignore",
        ),
        how="left",
        on="school_id",
    )

    app_state_instance["current_status_message"] = (
        "Merging with student_years data (enrollment history)..."
    )
    # 2. Merge with StudentYears (to get grade progression and enrollment status)
    # This will create multiple rows per student if they have records across multiple years
    combined_df = combined_df.merge(
        app_state_instance["student_years_df"]
        .rename(
            columns={
                "academic_year": "enrolled_academic_year",
                "grade": "enrolled_grade",
                "status": "enrollment_status",
                "enrollment_date": "enrolled_date",
            }
        )
        .drop(
            columns=[
                "student_year_id",
                "school_id",
                "last_update_date",
                "last_update_userid",
            ],
            errors="ignore",
        ),
        how="left",
        left_on=[
            "student_id",
            "enrollment_date",
        ],  # Assuming enrollment_date aligns with student_years.enrollment_date
        right_on=["student_id", "enrolled_date"],
    )
    # Drop the redundant enrolled_date column if it exists and is not needed
    if "enrolled_date" in combined_df.columns:
        combined_df = combined_df.drop(columns=["enrolled_date"])

    app_state_instance["current_status_message"] = "Merging academic records..."
    # 3. Merge with Academic Records
    # This will expand the DataFrame to have one row per academic record
    combined_df = combined_df.merge(
        app_state_instance["academic_records_df"]
        .rename(
            columns={
                "record_id": "academic_record_id",
                "subject_name": "academic_subject_name",
                "assessment_type": "academic_assessment_type",
                "mark": "academic_mark",
                "assessment_date": "academic_assessment_date",
                "academic_year": "academic_record_year",
            }
        )
        .drop(
            columns=["school_id", "last_update_date", "last_update_userid"],
            errors="ignore",
        ),
        how="left",  # Use left join to keep all student-year combinations even if no academic records
        on="student_id",
    )
    # Filter academic records to match the academic year of the enrollment
    combined_df = combined_df[
        combined_df["academic_record_year"] == combined_df["enrolled_academic_year"]
    ]

    app_state_instance["current_status_message"] = "Merging attendance data..."
    # 4. Merge with Attendance (aggregate attendance for each student-year)
    attendance_detail = app_state_instance["attendance_df"].copy()

    # Convert Status to numerical for aggregation
    attendance_detail["is_present"] = attendance_detail["status"].apply(
        lambda x: 1 if x == "Present" else 0
    )

    # Extract year from record_date for grouping
    attendance_detail["record_year"] = pd.to_datetime(
        attendance_detail["record_date"]
    ).dt.year

    attendance_summary = (
        attendance_detail.groupby(["student_id", "record_year"])
        .agg(
            total_days_present=("is_present", "sum"),
            total_days_recorded=("is_present", "count"),
        )
        .reset_index()
        .rename(columns={"record_year": "academic_year_attendance"})
    )
    attendance_summary["attendance_rate"] = (
        attendance_summary["total_days_present"]
        / attendance_summary["total_days_recorded"]
    )
    attendance_summary["attendance_rate"].fillna(0, inplace=True)

    combined_df = combined_df.merge(
        attendance_summary.drop(
            columns=["total_days_present", "total_days_recorded"], errors="ignore"
        ),
        how="left",
        left_on=[
            "student_id",
            "academic_record_year",
        ],  # Merge on student_id and the academic year of the record
        right_on=["student_id", "academic_year_attendance"],
    )
    if "academic_year_attendance" in combined_df.columns:
        combined_df = combined_df.drop(columns=["academic_year_attendance"])
    combined_df["attendance_rate"].fillna(
        0, inplace=True
    )  # Fill NaN for students with no attendance records

    app_state_instance["current_status_message"] = "Performing feature engineering..."
    # 5. Feature Engineering
    combined_df["age_at_academic_year"] = (
        combined_df["academic_record_year"]
        - pd.to_datetime(combined_df["date_of_birth"]).dt.year
    )

    # Impute missing numerical marks before using them
    if "academic_mark" in combined_df.columns:
        combined_df["academic_mark"].fillna(
            combined_df["academic_mark"].mean(), inplace=True
        )

    # Categorical features for One-Hot Encoding
    categorical_cols = [
        "gender",
        "race",
        "parent_socio_economic_status",
        "current_school_type",
        "current_school_province",
        "current_school_district",
        "home_environment",
        "internet_access",
        "study_habits",
        "extracurricular_engagement",
        "health_nutrition",
        "special_needs_support",
        "academic_subject_name",
        "academic_assessment_type",
        "enrollment_status",
    ]

    # Filter for columns that actually exist in the DataFrame
    categorical_cols_existing = [
        col for col in categorical_cols if col in combined_df.columns
    ]

    if categorical_cols_existing:
        log_to_console(
            f"One-hot encoding categorical features: {categorical_cols_existing}",
            "INFO",
        )
        combined_df = pd.get_dummies(
            combined_df, columns=categorical_cols_existing, dummy_na=False
        )

    # Drop columns not suitable for ML or redundant after feature engineering
    columns_to_drop_final = [
        "first_name",
        "last_name",
        "date_of_birth",
        "enrollment_date",
        "school_id",
        "parent_id",
        "parent_first_name",
        "parent_last_name",
        "current_school_name",
        "academic_record_id",
        "academic_assessment_date",
        "record_date",
        "status",
        "reason",  # from attendance_records
        "last_update_date",
        "last_update_userid",
        "enrolled_academic_year",  # Redundant with academic_record_year for ML features
        "enrolled_grade",
        "enrollment_status",  # These are encoded
    ]
    combined_df = combined_df.drop(
        columns=[col for col in columns_to_drop_final if col in combined_df.columns],
        errors="ignore",
    )

    # Handle any remaining NaNs in numerical columns (e.g., if some merges resulted in NaNs)
    for col in combined_df.select_dtypes(include=np.number).columns:
        combined_df[col].fillna(combined_df[col].mean(), inplace=True)

    app_state_instance["current_status_message"] = (
        "Dataset combination and feature engineering complete."
    )
    log_to_console("Combined dataset created successfully.", "INFO")
    return combined_df


# --- Machine Learning Model ---
def train_and_save_model(engine):
    log_to_console("Attempting to train and save the prediction model...", "INFO")

    # Ensure combined_dataset is up-to-date
    application_state["combined_dataset"] = combine_datasets(application_state)

    if application_state["combined_dataset"].empty:
        message = "Insufficient data to train the model. Please generate more data."
        add_response_to_queue(message, "warning")
        update_app_state("model_trained", False)
        return {"status": "error", "message": message}

    try:
        target_column = "academic_mark"  # Predicting the mark
        if target_column not in application_state["combined_dataset"].columns:
            message = f"Target column '{target_column}' not found in combined dataset. Cannot train model."
            add_response_to_queue(message, "error")
            update_app_state("model_trained", False)
            return {"status": "error", "message": message}

        # Drop non-feature columns and the target
        X = application_state["combined_dataset"].drop(
            columns=[
                target_column,
                "student_id",
                "current_grade",  # current_grade is redundant with enrolled_grade/academic_record_year
            ],
            errors="ignore",
        )
        y = application_state["combined_dataset"][target_column]

        # Identify numerical and categorical (already one-hot encoded) columns
        numerical_cols = X.select_dtypes(include=np.number).columns.tolist()

        # Preprocessor for numerical features (impute and scale)
        numerical_transformer = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="mean")),
                ("scaler", StandardScaler()),
            ]
        )

        preprocessor = ColumnTransformer(
            transformers=[
                ("num", numerical_transformer, numerical_cols),
            ],
            remainder="passthrough",  # Keep one-hot encoded columns as is
            verbose_feature_names_out=False,  # To avoid prefixing column names
        )
        preprocessor.set_output(
            transform="pandas"
        )  # Output pandas DataFrame from preprocessor

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Train RandomForestRegressor model
        model = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                (
                    "regressor",
                    RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1),
                ),
            ]
        )
        model.fit(X_train, y_train)

        # Evaluate model
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)

        metrics = {"mse": mse, "r2_score": r2, "mae": mae}
        application_state["metrics"] = metrics
        log_to_console(
            f"Model trained. Metrics: MSE={mse:.2f}, R2={r2:.2f}, MAE={mae:.2f}", "INFO"
        )

        # Store the feature names after preprocessing
        # This is a bit tricky with ColumnTransformer and remainder='passthrough'
        # A simpler way is to get the column names from X_train after fitting the preprocessor
        # Or, just save the preprocessor and the model separately.
        # For simplicity, let's save the entire pipeline.

        model_path = "student_performance_pipeline.joblib"
        joblib.dump(model, model_path)

        # Store the columns of X (before preprocessing in the pipeline)
        application_state["model_features"] = X.columns.tolist()

        # Store means of numerical features for future prediction NaN filling
        # This is handled by SimpleImputer in the pipeline, so we don't need to store it separately
        # unless we want to inspect it. For now, we'll rely on the pipeline.

        update_app_state("model_trained", True)
        message = f"Prediction model trained and saved successfully. MSE: {mse:.2f}, R2 Score: {r2:.2f}"
        add_response_to_queue(message, "success", data={"metrics": metrics})
        return {"status": "success", "message": message, "metrics": metrics}

    except Exception as e:
        log_to_console(f"Error training and saving model: {e}", "ERROR")
        update_app_state("model_trained", False)
        message = f"Failed to train model: {e}"
        add_response_to_queue(message, "error")
        return {"status": "error", "message": message}


def load_model_and_features():
    model_path = "student_performance_pipeline.joblib"
    if os.path.exists(model_path):
        try:
            model_pipeline = joblib.load(model_path)
            # The model_features are the columns of X before preprocessing
            # These were saved in application_state["model_features"] during training
            log_to_console("Prediction model pipeline loaded.", "INFO")
            update_app_state("model_trained", True)
            return model_pipeline, application_state["model_features"]
        except Exception as e:
            log_to_console(f"Error loading model pipeline: {e}", "ERROR")
            update_app_state("model_trained", False)
            return None, None
    log_to_console("Model pipeline file not found.", "WARNING")
    update_app_state("model_trained", False)
    return None, None


def predict_performance(student_id):
    log_to_console(
        f"Attempting to predict performance for student ID: {student_id}", "INFO"
    )
    engine = get_db_connection()
    if engine is None:
        return {"status": "error", "message": "Database connection not available."}

    model_pipeline, trained_features = load_model_and_features()
    if model_pipeline is None or not trained_features:
        add_response_to_queue(
            "Prediction model not available or not trained. Please train the model first.",
            "warning",
        )
        return {"status": "error", "message": "Prediction model not available."}

    try:
        # Fetch all data for the specific student and combine it in the same way as training
        # This requires re-running a subset of combine_datasets logic for a single student
        student_df_raw = read_table_to_dataframe(engine, "students").query(
            f"student_id == '{student_id}'"
        )
        if student_df_raw.empty:
            add_response_to_queue(
                f"No data found for student ID: {student_id}", "warning"
            )
            return {
                "status": "error",
                "message": f"No data found for student ID: {student_id}",
            }

        # Load necessary related dataframes for this student
        parents_df_filtered = read_table_to_dataframe(engine, "parents").query(
            f"parent_id == '{student_df_raw['parent_id'].iloc[0]}'"
        )
        schools_df_filtered = read_table_to_dataframe(engine, "schools").query(
            f"school_id == '{student_df_raw['school_id'].iloc[0]}'"
        )
        student_years_df_filtered = read_table_to_dataframe(
            engine, "student_years"
        ).query(f"student_id == '{student_id}'")
        academic_records_df_filtered = read_table_to_dataframe(
            engine, "academic_records"
        ).query(f"student_id == '{student_id}'")
        attendance_df_filtered = read_table_to_dataframe(
            engine, "attendance_records"
        ).query(f"student_id == '{student_id}'")
        subject_lookup_df = read_table_to_dataframe(engine, "subject_lookup")
        academic_assessment_type_lookup_df = read_table_to_dataframe(
            engine, "academic_assessment_type_lookup"
        )
        attendance_status_lookup_df = read_table_to_dataframe(
            engine, "attendance_status_lookup"
        )
        socio_economic_status_lookup_df = read_table_to_dataframe(
            engine, "socio_economic_status_lookup"
        )
        home_environment_lookup_df = read_table_to_dataframe(
            engine, "home_environment_lookup"
        )
        internet_access_lookup_df = read_table_to_dataframe(
            engine, "internet_access_lookup"
        )
        study_habits_lookup_df = read_table_to_dataframe(engine, "study_habits_lookup")
        extracurricular_engagement_lookup_df = read_table_to_dataframe(
            engine, "extracurricular_engagement_lookup"
        )
        health_nutrition_lookup_df = read_table_to_dataframe(
            engine, "health_nutrition_lookup"
        )
        special_needs_support_lookup_df = read_table_to_dataframe(
            engine, "special_needs_support_lookup"
        )

        # Temporarily update application_state with filtered data for combine_datasets
        temp_app_state = {
            "students_df": student_df_raw,
            "parents_df": parents_df_filtered,
            "schools_df": schools_df_filtered,
            "student_years_df": student_years_df_filtered,
            "academic_records_df": academic_records_df_filtered,
            "attendance_df": attendance_df_filtered,
            "subjects_df": subject_lookup_df,  # Use lookup for subjects
            # Add other necessary lookups if combine_datasets needs them directly
            "current_status_message": "Predicting for single student...",  # Placeholder
        }

        # Combine data for the single student
        student_combined_df = combine_datasets(temp_app_state)

        if student_combined_df.empty:
            add_response_to_queue(
                f"Could not prepare data for student ID: {student_id}. Check if related data exists.",
                "warning",
            )
            return {
                "status": "error",
                "message": f"Could not prepare data for student ID: {student_id}",
            }

        # Ensure the combined_df has the target column and drop it for prediction
        if "academic_mark" in student_combined_df.columns:
            X_predict = student_combined_df.drop(
                columns=["academic_mark", "student_id", "current_grade"],
                errors="ignore",
            )
        else:
            X_predict = student_combined_df.drop(
                columns=["student_id", "current_grade"], errors="ignore"
            )  # If mark is not present

        # Reindex to match training features, filling missing columns with 0
        X_predict = X_predict.reindex(columns=trained_features, fill_value=0)

        # Make prediction
        predicted_mark = model_pipeline.predict(X_predict)[0]

        if predicted_mark >= 85:
            performance_category = "Excellent"
        elif predicted_mark >= 70:
            performance_category = "Good"
        elif predicted_mark >= 50:
            performance_category = "Average"
        else:
            performance_category = "Needs Improvement"

        result = {
            "student_id": student_id,
            "predicted_average_mark": round(predicted_mark, 2),
            "performance_category": performance_category,
            "interpretation": "This is an AI-driven prediction based on available academic and demographic data. It should be used as a guide, not a definitive assessment. Further human review is recommended.",
        }
        add_response_to_queue(
            f"Prediction for student {student_id} successful.", "success", data=result
        )
        return {"status": "success", "data": result}

    except Exception as e:
        log_to_console(
            f"Error predicting performance for student {student_id}: {e}", "ERROR"
        )
        add_response_to_queue(
            f"Failed to predict performance for student {student_id}: {e}", "error"
        )
        return {"status": "error", "message": f"Failed to predict performance: {e}"}


# --- Flask App Setup ---
app = Flask(__name__, static_folder="static", static_url_path="/static")
CORS(app, supports_credentials=True)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "your_super_secret_key")
application = WSGIMiddleware(app)


# --- Flask Routes ---
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "login.html")


@app.route("/admin_dashboard")
def admin_dashboard():
    if "username" not in session or session.get("role") != "admin":
        flash("Unauthorized access. Please log in as an administrator.")
        return redirect(url_for("index"))
    return send_from_directory(app.static_folder, "admin.html")


@app.route("/api/login", methods=["POST"])
def login():
    username = request.json.get("username").strip()
    password = request.json.get("password").strip()

    log_to_console(f"Attempting login with username: '{username}'", "DEBUG")
    log_to_console(f"Received password (raw): '{password}'", "DEBUG", sensitive=True)

    engine = get_db_connection()
    if engine is None:
        log_to_console("Login failed: Database connection not available.", "ERROR")
        return jsonify({"success": False, "message": "Database connection error."}), 500

    with engine.connect() as connection:
        cursor = connection.connection.cursor()
        try:
            cursor.execute(f"SELECT OBJECT_ID(N'users', 'U');")
            users_table_exists = cursor.fetchone()[0] is not None
            if not users_table_exists:
                log_to_console(
                    f"Login failed: 'users' table does not exist in the database.",
                    "ERROR",
                )
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "Application user table not found. Please contact administrator.",
                        }
                    ),
                    500,
                )

            cursor.execute(
                "SELECT password, role FROM users WHERE username = ?", (username,)
            )
            user_record = cursor.fetchone()

            if user_record:
                stored_password_raw = user_record[0]
                stored_password_clean = str(stored_password_raw).strip()

                log_to_console(
                    f"Stored password (raw from DB): '{stored_password_raw}'",
                    "DEBUG",
                    sensitive=True,
                )
                log_to_console(
                    f"Stored password (cleaned for comparison): '{stored_password_clean}'",
                    "DEBUG",
                    sensitive=True,
                )

                if stored_password_clean == password:
                    session["username"] = username
                    session["role"] = user_record[1]
                    log_to_console(
                        f"User '{username}' logged in successfully as '{user_record[1]}'.",
                        "INFO",
                    )
                    return jsonify(
                        {"success": True, "redirect": url_for("admin_dashboard")}
                    )
                else:
                    log_to_console(
                        f"Login failed for user '{username}': Password mismatch. Received: '{password}', Stored: '{stored_password_clean}'",
                        "WARNING",
                        sensitive=True,
                    )
                    return (
                        jsonify(
                            {
                                "success": False,
                                "message": "Invalid username or password.",
                            }
                        ),
                        401,
                    )
            else:
                log_to_console(
                    f"Login failed for user '{username}': User not found.", "WARNING"
                )
                return (
                    jsonify(
                        {"success": False, "message": "Invalid username or password."}
                    ),
                    401,
                )
        except Exception as e:
            log_to_console(
                f"Database error during login for '{username}': {e}", "ERROR"
            )
            return (
                jsonify(
                    {"success": False, "message": f"Server error during login: {e}"}
                ),
                500,
            )
        finally:
            cursor.close()


@app.route("/api/logout", methods=["POST"])
def logout():
    session.pop("username", None)
    session.pop("role", None)
    flash("You have been logged out.")
    log_to_console("User logged out.", "INFO")
    return jsonify({"success": True, "redirect": url_for("index")})


@app.route("/api/app_state", methods=["GET"])
def get_app_state():
    state_for_frontend = {
        "db_connected": application_state["db_connected"],
        "dataset_ready": application_state["dataset_ready"],
        "model_trained": application_state["model_trained"],
        "metrics": application_state["metrics"],
        "app_version": application_state["app_version"],
        "username": session.get("username"),
        "role": session.get("role"),
    }
    return jsonify(state_for_frontend)


@app.route("/api/console_logs", methods=["GET"])
def get_console_logs():
    return jsonify(list(console_output_log))


@app.route("/api/responses", methods=["GET"])
def get_responses():
    responses = list(response_queue)
    response_queue.clear()
    return jsonify(responses)


@app.route("/api/connect_db", methods=["POST"])
def connect_db_route():
    def _connect_db_task():
        conn = get_db_connection()
        if conn:
            add_response_to_queue("Database connected successfully.", "success")
        else:
            add_response_to_queue("Failed to connect to database.", "error")

    threading.Thread(target=_connect_db_task).start()
    return jsonify(
        {"status": "info", "message": "Attempting to connect to database..."}
    )


@app.route("/api/disconnect_db", methods=["POST"])
def disconnect_db_route():
    def _disconnect_db_task():
        global sqlalchemy_engine
        if sqlalchemy_engine:
            try:
                sqlalchemy_engine.dispose()
                sqlalchemy_engine = None
                update_app_state("db_connected", False)
                add_response_to_queue("Disconnected from database.", "success")
            except Exception as e:
                add_response_to_queue(
                    f"Error disconnecting from database: {e}", "error"
                )
        else:
            add_response_to_queue(
                "No active database connection to disconnect.", "info"
            )

    threading.Thread(target=_disconnect_db_task).start()
    return jsonify(
        {"status": "info", "message": "Attempting to disconnect from database..."}
    )


@app.route("/api/create_tables", methods=["POST"])
def create_tables_route():
    def _create_tables_task():
        engine = get_db_connection()
        if engine:
            create_tables_if_not_exist(engine)
            populate_lookup_tables(engine)
            populate_chatbot_knowledge_base(engine)
            add_response_to_queue(
                "Database schema and lookup tables ensured.", "success"
            )
        else:
            add_response_to_queue(
                "Failed to create tables: DB connection error.", "error"
            )

    threading.Thread(target=_create_tables_task).start()
    return jsonify({"status": "info", "message": "Initiating table creation..."})


@app.route("/api/generate_schools", methods=["POST"])
def generate_schools_route():
    if session.get("role") != "admin":
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    num_schools = request.json.get("num_schools", NUM_SCHOOLS_TO_GENERATE)

    def _generate_schools_task():
        engine = get_db_connection()
        if engine:
            df = generate_schools(num_schools, application_state)
            write_dataframe_to_sql(engine, df, "schools", if_exists="replace")
            application_state["schools_df"] = df  # Update app state with generated data
            add_response_to_queue(f"Generated {len(df)} schools.", "success")
        else:
            add_response_to_queue(
                "Failed to generate schools: DB connection error.", "error"
            )

    threading.Thread(target=_generate_schools_task).start()
    return jsonify(
        {"status": "info", "message": f"Generating {num_schools} schools..."}
    )


@app.route("/api/generate_parents", methods=["POST"])
def generate_parents_route():
    if session.get("role") != "admin":
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    num_parents = request.json.get("num_parents", NUM_PARENTS_TO_GENERATE)

    def _generate_parents_task():
        engine = get_db_connection()
        if engine:
            df = generate_parents(num_parents, application_state)
            write_dataframe_to_sql(engine, df, "parents", if_exists="replace")
            application_state["parents_df"] = df
            add_response_to_queue(f"Generated {len(df)} parents.", "success")
        else:
            add_response_to_queue(
                "Failed to generate parents: DB connection error.", "error"
            )

    threading.Thread(target=_generate_parents_task).start()
    return jsonify(
        {"status": "info", "message": f"Generating {num_parents} parents..."}
    )


@app.route("/api/generate_students", methods=["POST"])
def generate_students_route():
    if session.get("role") != "admin":
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    num_students = request.json.get("num_students", TOTAL_UNIQUE_STUDENTS_TO_GENERATE)

    def _generate_students_task():
        engine = get_db_connection()
        if engine:
            schools_df = read_table_to_dataframe(engine, "schools")
            parents_df = read_table_to_dataframe(engine, "parents")
            if schools_df.empty or parents_df.empty:
                add_response_to_queue(
                    "Cannot generate students: schools or parents data missing. Please generate them first.",
                    "error",
                )
                return

            students_df, student_years_df = generate_students_and_initial_enrollments(
                schools_df, parents_df, num_students, application_state
            )
            write_dataframe_to_sql(engine, students_df, "students", if_exists="replace")
            write_dataframe_to_sql(
                engine, student_years_df, "student_years", if_exists="replace"
            )
            application_state["students_df"] = students_df
            application_state["student_years_df"] = student_years_df
            add_response_to_queue(
                f"Generated {len(students_df)} students and their initial enrollments.",
                "success",
            )
        else:
            add_response_to_queue(
                "Failed to generate students: DB connection error.", "error"
            )

    threading.Thread(target=_generate_students_task).start()
    return jsonify(
        {"status": "info", "message": f"Generating {num_students} students..."}
    )


@app.route("/api/generate_academic_history", methods=["POST"])
def generate_academic_history_route():
    if session.get("role") != "admin":
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    num_entries_per_student = request.json.get("num_entries_per_student", 5)

    def _generate_academic_history_task():
        engine = get_db_connection()
        if engine:
            students_df = read_table_to_dataframe(engine, "students")
            subjects_df = read_table_to_dataframe(
                engine, "subject_lookup"
            )  # Use subject_lookup
            if students_df.empty or subjects_df.empty:
                add_response_to_queue(
                    "Cannot generate academic history: students or subjects data missing. Please generate them first.",
                    "error",
                )
                return
            df = generate_academic_records(
                students_df, subjects_df, START_YEAR, END_YEAR, application_state
            )
            write_dataframe_to_sql(engine, df, "academic_records", if_exists="replace")
            application_state["academic_records_df"] = df
            add_response_to_queue(f"Generated {len(df)} academic records.", "success")
        else:
            add_response_to_queue(
                "Failed to generate academic history: DB connection error.", "error"
            )

    threading.Thread(target=_generate_academic_history_task).start()
    return jsonify({"status": "info", "message": "Generating academic history..."})


@app.route("/api/generate_attendance", methods=["POST"])
def generate_attendance_route():
    if session.get("role") != "admin":
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    num_entries_per_student = request.json.get("num_entries_per_student", 10)

    def _generate_attendance_task():
        engine = get_db_connection()
        if engine:
            students_df = read_table_to_dataframe(engine, "students")
            if students_df.empty:
                add_response_to_queue(
                    "Cannot generate attendance: students data missing. Please generate them first.",
                    "error",
                )
                return
            df = generate_attendance_records(
                students_df, START_YEAR, END_YEAR, application_state
            )
            write_dataframe_to_sql(
                engine, df, "attendance_records", if_exists="replace"
            )
            application_state["attendance_df"] = df
            add_response_to_queue(f"Generated {len(df)} attendance records.", "success")
        else:
            add_response_to_queue(
                "Failed to generate attendance: DB connection error.", "error"
            )

    threading.Thread(target=_generate_attendance_task).start()
    return jsonify({"status": "info", "message": "Generating attendance records..."})


@app.route("/api/generate_all_data", methods=["POST"])
def generate_all_data_route():
    if session.get("role") != "admin":
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    def _generate_all_data_task():
        log_to_console("Starting bulk data generation...", "INFO")
        engine = get_db_connection()
        if engine is None:
            add_response_to_queue(
                "Failed to generate all data: Database connection not available.",
                "error",
            )
            return

        try:
            log_to_console("Clearing existing data...", "INFO")
            clear_all_data_internal()
            add_response_to_queue("Existing data cleared.", "info")

            # Schools
            schools_df = generate_schools(NUM_SCHOOLS_TO_GENERATE, application_state)
            write_dataframe_to_sql(engine, schools_df, "schools", if_exists="replace")
            application_state["schools_df"] = schools_df
            add_response_to_queue(f"Generated {len(schools_df)} schools.", "success")

            # Parents
            parents_df = generate_parents(NUM_PARENTS_TO_GENERATE, application_state)
            write_dataframe_to_sql(engine, parents_df, "parents", if_exists="replace")
            application_state["parents_df"] = parents_df
            add_response_to_queue(f"Generated {len(parents_df)} parents.", "success")

            # Students and Initial Enrollments
            students_df, student_years_df_initial = (
                generate_students_and_initial_enrollments(
                    schools_df,
                    parents_df,
                    TOTAL_UNIQUE_STUDENTS_TO_GENERATE,
                    application_state,
                )
            )
            write_dataframe_to_sql(engine, students_df, "students", if_exists="replace")
            write_dataframe_to_sql(
                engine, student_years_df_initial, "student_years", if_exists="replace"
            )
            application_state["students_df"] = students_df
            application_state["student_years_df"] = student_years_df_initial
            add_response_to_queue(
                f"Generated {len(students_df)} students and initial enrollments.",
                "success",
            )

            # Simulate Student Progression
            updated_student_years_df = simulate_student_progression(
                students_df,
                student_years_df_initial,
                START_YEAR,
                END_YEAR,
                application_state,
            )
            write_dataframe_to_sql(
                engine, updated_student_years_df, "student_years", if_exists="replace"
            )
            application_state["student_years_df"] = updated_student_years_df
            add_response_to_queue(
                f"Simulated student progression for {len(updated_student_years_df)} student-years.",
                "success",
            )

            # Subjects (read from lookup)
            subjects_df = read_table_to_dataframe(engine, "subject_lookup")
            application_state["subjects_df"] = subjects_df
            if subjects_df.empty:
                add_response_to_queue(
                    "Warning: Subject lookup table is empty. Academic records might not be generated.",
                    "warning",
                )
            else:
                add_response_to_queue(
                    f"Loaded {len(subjects_df)} subjects from lookup.", "success"
                )

            # Academic History
            academic_records_df = generate_academic_records(
                students_df, subjects_df, START_YEAR, END_YEAR, application_state
            )
            if not academic_records_df.empty:
                write_dataframe_to_sql(
                    engine, academic_records_df, "academic_records", if_exists="replace"
                )
                application_state["academic_records_df"] = academic_records_df
                add_response_to_queue(
                    f"Generated {len(academic_records_df)} academic records.", "success"
                )
            else:
                add_response_to_queue(
                    "No academic records generated (e.g., no subjects or students).",
                    "warning",
                )

            # Attendance Records
            attendance_df = generate_attendance_records(
                students_df, START_YEAR, END_YEAR, application_state
            )
            write_dataframe_to_sql(
                engine, attendance_df, "attendance_records", if_exists="replace"
            )
            application_state["attendance_df"] = attendance_df
            add_response_to_queue(
                f"Generated {len(attendance_df)} attendance records.", "success"
            )

            # Combine Datasets for ML
            application_state["combined_dataset"] = combine_datasets(application_state)
            add_response_to_queue("Combined dataset for ML created.", "success")
            update_app_state("dataset_ready", True)
            add_response_to_queue(
                "All data generation completed successfully.", "success"
            )

        except Exception as e:
            log_to_console(
                f"An error occurred during bulk data generation: {e}", "CRITICAL"
            )
            add_response_to_queue(f"Bulk data generation failed: {e}", "error")
            update_app_state("dataset_ready", False)

    threading.Thread(target=_generate_all_data_task).start()
    return jsonify({"status": "info", "message": "All data generation started."})


@app.route("/api/clear_all_data", methods=["POST"])
def clear_all_data_route():
    if session.get("role") != "admin":
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    def _clear_all_data_task():
        result = clear_all_data_internal()
        add_response_to_queue(result["message"], result["status"])

    threading.Thread(target=_clear_all_data_task).start()
    return jsonify({"status": "info", "message": "Initiating clear all data..."})


@app.route("/api/train_model", methods=["POST"])
def train_model_route():
    if session.get("role") != "admin":
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    def _train_model_task():
        engine = get_db_connection()
        if engine:
            result = train_and_save_model(engine)
        else:
            add_response_to_queue(
                "Model training failed: DB connection error.", "error"
            )

    threading.Thread(target=_train_model_task).start()
    return jsonify({"status": "info", "message": "Initiating model training..."})


@app.route("/api/predict_performance", methods=["POST"])
def predict_performance_route():
    if session.get("role") != "admin":
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    student_id = request.json.get("student_id")
    if not student_id:
        return (
            jsonify(
                {"status": "error", "message": "Student ID is required for prediction."}
            ),
            400,
        )

    def _predict_performance_task():
        predict_performance(student_id)

    threading.Thread(target=_predict_performance_task).start()
    return jsonify(
        {
            "status": "info",
            "message": f"Initiating prediction for student {student_id}...",
        }
    )


@app.route("/api/get_students", methods=["GET"])
def get_students():
    if session.get("role") != "admin":
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    engine = get_db_connection()
    if engine is None:
        return (
            jsonify(
                {"status": "error", "message": "Database connection not available."}
            ),
            500,
        )
    try:
        query = """
            SELECT
                s.student_id,
                s.first_name,
                s.last_name,
                s.date_of_birth,
                s.gender,
                s.race,
                s.has_social_grant,
                s.enrollment_date,
                sch.school_name,
                p.first_name AS parent_first_name,
                p.last_name AS parent_last_name,
                s.current_grade,
                s.home_environment,
                s.internet_access,
                s.study_habits,
                s.extracurricular_engagement,
                s.health_nutrition,
                s.special_needs_support
            FROM students s
            LEFT JOIN schools sch ON s.school_id = sch.school_id
            LEFT JOIN parents p ON s.parent_id = p.parent_id;
        """
        df = pd.read_sql_query(query, engine)
        students_data = df.to_dict(orient="records")
        return jsonify({"status": "success", "data": students_data})
    except Exception as e:
        log_to_console(f"Error fetching student data: {e}", "ERROR")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/get_schools", methods=["GET"])
def get_schools():
    if session.get("role") != "admin":
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    engine = get_db_connection()
    if engine is None:
        return (
            jsonify(
                {"status": "error", "message": "Database connection not available."}
            ),
            500,
        )
    try:
        query = """
            SELECT
                school_id, school_name, school_type, province, district, quintile,
                contact_person, contact_email, contact_phone, InfrastructureScore, TeacherAbsenteeismRate
            FROM schools;
        """
        df = pd.read_sql_query(query, engine)
        schools_data = df.to_dict(orient="records")
        return jsonify({"status": "success", "data": schools_data})
    except Exception as e:
        log_to_console(f"Error fetching school data: {e}", "ERROR")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/get_parents", methods=["GET"])
def get_parents():
    if session.get("role") != "admin":
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    engine = get_db_connection()
    if engine is None:
        return (
            jsonify(
                {"status": "error", "message": "Database connection not available."}
            ),
            500,
        )
    try:
        query = """
            SELECT
                parent_id, first_name, last_name, contact_email, contact_phone, address,
                city, state, zip_code, socio_economic_status
            FROM parents;
        """
        df = pd.read_sql_query(query, engine)
        parents_data = df.to_dict(orient="records")
        return jsonify({"status": "success", "data": parents_data})
    except Exception as e:
        log_to_console(f"Error fetching parent data: {e}", "ERROR")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/get_academic_records", methods=["GET"])
def get_academic_records():
    if session.get("role") != "admin":
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    engine = get_db_connection()
    if engine is None:
        return (
            jsonify(
                {"status": "error", "message": "Database connection not available."}
            ),
            500,
        )
    try:
        query = """
            SELECT
                ar.record_id,
                ar.student_id,
                s.first_name + ' ' + s.last_name AS student_name,
                ar.school_id,
                sch.school_name,
                ar.subject_name,
                ar.assessment_type,
                ar.mark,
                ar.assessment_date,
                ar.academic_year
            FROM academic_records ar
            LEFT JOIN students s ON ar.student_id = s.student_id
            LEFT JOIN schools sch ON ar.school_id = sch.school_id;
        """
        df = pd.read_sql_query(query, engine)
        records_data = df.to_dict(orient="records")
        return jsonify({"status": "success", "data": records_data})
    except Exception as e:
        log_to_console(f"Error fetching academic records: {e}", "ERROR")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/get_attendance_records", methods=["GET"])
def get_attendance_records():
    if session.get("role") != "admin":
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    engine = get_db_connection()
    if engine is None:
        return (
            jsonify(
                {"status": "error", "message": "Database connection not available."}
            ),
            500,
        )
    try:
        query = """
            SELECT
                att.attendance_id,
                att.student_id,
                s.first_name + ' ' + s.last_name AS student_name,
                att.school_id,
                sch.school_name,
                att.record_date,
                att.status,
                att.reason
            FROM attendance_records att
            LEFT JOIN students s ON att.student_id = s.student_id
            LEFT JOIN schools sch ON att.school_id = sch.school_id;
        """
        df = pd.read_sql_query(query, engine)
        records_data = df.to_dict(orient="records")
        return jsonify({"status": "success", "data": records_data})
    except Exception as e:
        log_to_console(f"Error fetching attendance records: {e}", "ERROR")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/get_student_performance_trends", methods=["GET"])
def get_student_performance_trends():
    if session.get("role") != "admin":
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    engine = get_db_connection()
    if engine is None:
        return (
            jsonify(
                {"status": "error", "message": "Database connection not available."}
            ),
            500,
        )
    try:
        query = """
            SELECT
                s.student_id,
                s.first_name + ' ' + s.last_name AS student_name,
                ar.academic_year,
                AVG(ar.mark) AS average_mark
            FROM academic_records ar
            JOIN students s ON ar.student_id = s.student_id
            GROUP BY s.student_id, s.first_name, s.last_name, ar.academic_year
            ORDER BY ar.academic_year ASC;
        """
        df = pd.read_sql_query(query, engine)

        trends_data = []
        for student_id, student_df in df.groupby("student_id"):
            student_name = student_df.iloc[0]["student_name"]
            performance_history = student_df[["academic_year", "average_mark"]].to_dict(
                orient="records"
            )
            trends_data.append(
                {
                    "student_id": student_id,
                    "student_name": student_name,
                    "performance_history": performance_history,
                }
            )
        return jsonify({"status": "success", "data": trends_data})
    except Exception as e:
        log_to_console(f"Error fetching student performance trends: {e}", "ERROR")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/get_intervention_recommendations", methods=["GET"])
def get_intervention_recommendations():
    if session.get("role") != "admin":
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    engine = get_db_connection()
    if engine is None:
        return (
            jsonify(
                {"status": "error", "message": "Database connection not available."}
            ),
            500,
        )
    try:
        query = """
            SELECT
                ir.recommendation_id,
                ir.student_id,
                s.first_name + ' ' + s.last_name AS student_name,
                ir.recommended_action,
                ir.reason,
                ir.recommendation_date
            FROM intervention_recommendations ir
            JOIN students s ON ir.student_id = s.student_id
            ORDER BY ir.recommendation_date DESC;
        """
        df = pd.read_sql_query(query, engine)
        recommendations_data = df.to_dict(orient="records")
        return jsonify({"status": "success", "data": recommendations_data})
    except Exception as e:
        log_to_console(f"Error fetching intervention recommendations: {e}", "ERROR")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/add_intervention_recommendation", methods=["POST"])
def add_intervention_recommendation():
    if session.get("role") != "admin":
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    data = request.json
    student_id = data.get("student_id")
    recommended_action = data.get("recommended_action")
    reason = data.get("reason")

    if not all([student_id, recommended_action]):
        return jsonify({"status": "error", "message": "Missing required fields."}), 400

    engine = get_db_connection()
    if engine is None:
        return (
            jsonify(
                {"status": "error", "message": "Database connection not available."}
            ),
            500,
        )

    with engine.connect() as connection:
        with connection.begin():
            cursor = connection.connection.cursor()
            try:
                recommendation_id = str(uuid.uuid4())
                current_userid = session.get("username", "admin")
                current_datetime = datetime.now()

                cursor.execute(
                    """
                    INSERT INTO intervention_recommendations (
                        recommendation_id, student_id, recommended_action, reason,
                        recommendation_date, last_update_date, last_update_userid
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        recommendation_id,
                        student_id,
                        recommended_action,
                        reason,
                        current_datetime,
                        current_datetime,
                        current_userid,
                    ),
                )
                log_to_console(
                    f"Added new intervention recommendation for student {student_id}.",
                    "INFO",
                )
                return jsonify(
                    {
                        "status": "success",
                        "message": "Recommendation added successfully.",
                    }
                )
            except Exception as e:
                log_to_console(f"Error adding recommendation: {e}", "ERROR")
                return jsonify({"status": "error", "message": str(e)}), 500
            finally:
                cursor.close()


@app.route("/api/chatbot_query", methods=["POST"])
def chatbot_query():
    query_text = request.json.get("query")
    if not query_text:
        return jsonify({"status": "error", "message": "Query text is required."}), 400

    engine = get_db_connection()
    if engine is None:
        return (
            jsonify(
                {"status": "error", "message": "Database connection not available."}
            ),
            500,
        )

    with engine.connect() as connection:
        cursor = connection.connection.cursor()
        try:
            cursor.execute(f"SELECT OBJECT_ID(N'chatbot_knowledge_base', 'U');")
            table_exists = cursor.fetchone()[0] is not None
            if not table_exists:
                log_to_console(
                    f"Chatbot query failed: 'chatbot_knowledge_base' table does not exist.",
                    "ERROR",
                )
                return (
                    jsonify(
                        {
                            "status": "error",
                            "message": "Chatbot knowledge base table not found. Please contact administrator.",
                        }
                    ),
                    500,
                )

            cursor.execute(
                "SELECT answer FROM chatbot_knowledge_base WHERE question LIKE ?",
                (f"%{query_text}%",),
            )
            result = cursor.fetchone()

            if result:
                return jsonify({"status": "success", "answer": result[0]})
            else:
                return jsonify(
                    {
                        "status": "success",
                        "answer": "I'm sorry, I don't have a specific answer for that in my knowledge base. Please try rephrasing your question or populate the 'chatbot_knowledge_base' table with relevant data.",
                    }
                )
        except Exception as e:
            log_to_console(f"Error querying chatbot knowledge base: {e}", "ERROR")
            return jsonify({"status": "error", "message": f"Server error: {e}"}), 500
        finally:
            cursor.close()


@app.route("/api/add_user", methods=["POST"])
def add_user():
    if session.get("role") != "admin":
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    username = request.json.get("username")
    password = request.json.get("password")
    role = request.json.get("role")

    if not all([username, password, role]):
        return (
            jsonify(
                {"status": "error", "message": "Missing username, password, or role."}
            ),
            400,
        )

    if role not in ["admin", "teacher", "viewer"]:
        return jsonify({"status": "error", "message": "Invalid role specified."}), 400

    engine = get_db_connection()
    if engine is None:
        return (
            jsonify(
                {"status": "error", "message": "Database connection not available."}
            ),
            500,
        )

    with engine.connect() as connection:
        with connection.begin():
            cursor = connection.connection.cursor()
            try:
                cursor.execute(f"SELECT OBJECT_ID(N'users', 'U');")
                users_table_exists = cursor.fetchone()[0] is not None
                if not users_table_exists:
                    log_to_console(
                        f"Add user failed: 'users' table does not exist in the database.",
                        "ERROR",
                    )
                    return (
                        jsonify(
                            {
                                "status": "error",
                                "message": "Application user table not found. Cannot add user.",
                            }
                        ),
                        500,
                    )

                cursor.execute(
                    "SELECT COUNT(*) FROM users WHERE username = ?", (username,)
                )
                if cursor.fetchone()[0] > 0:
                    return (
                        jsonify(
                            {"status": "error", "message": "Username already exists."}
                        ),
                        409,
                    )

                current_userid = session.get("username", "system")
                current_datetime = datetime.now()

                cursor.execute(
                    """
                    INSERT INTO users (username, password, role, last_update_date, last_update_userid)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (username, password, role, current_datetime, current_userid),
                )
                log_to_console(
                    f"User '{username}' with role '{role}' added by {current_userid}.",
                    "INFO",
                )
                return jsonify(
                    {
                        "status": "success",
                        "message": f"User '{username}' added successfully.",
                    }
                )
            except Exception as e:
                log_to_console(f"Database error adding user: {e}", "ERROR")
                return (
                    jsonify({"status": "error", "message": f"Database error: {e}"}),
                    500,
                )
            finally:
                cursor.close()


@app.route("/api/get_users", methods=["GET"])
def get_users():
    if session.get("role") != "admin":
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    engine = get_db_connection()
    if engine is None:
        return (
            jsonify(
                {"status": "error", "message": "Database connection not available."}
            ),
            500,
        )
    try:
        cursor = engine.connect().connection.cursor()
        cursor.execute(f"SELECT OBJECT_ID(N'users', 'U');")
        users_table_exists = cursor.fetchone()[0] is not None
        cursor.close()
        if not users_table_exists:
            log_to_console(
                f"Get users failed: 'users' table does not exist in the database.",
                "ERROR",
            )
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Application user table not found. Cannot retrieve users.",
                    }
                ),
                500,
            )

        query = "SELECT user_id, username, role, last_update_date, last_update_userid FROM users"
        df = pd.read_sql_query(query, engine)
        users_data = df.to_dict(orient="records")
        return jsonify({"status": "success", "data": users_data})
    except Exception as e:
        log_to_console(f"Error fetching users: {e}", "ERROR")
        return jsonify({"status": "error", "message": str(e)}), 500


# --- Startup Logic ---
def initialize_database():
    """Initialize the database, create tables, and populate lookup data."""
    engine = get_db_connection()
    if engine:
        try:
            create_tables_if_not_exist(engine)
            populate_lookup_tables(engine)
            populate_chatbot_knowledge_base(engine)

            with engine.connect() as connection:
                with connection.begin():
                    cursor = connection.connection.cursor()
                    try:
                        cursor.execute(f"SELECT OBJECT_ID(N'users', 'U');")
                        users_table_exists = cursor.fetchone()[0] is not None
                        if not users_table_exists:
                            log_to_console(
                                f"User count check failed: 'users' table does not exist.",
                                "ERROR",
                            )
                            add_response_to_queue(
                                "Critical: Application user table ('users') not found after startup. Please ensure database connection and permissions are correct.",
                                "critical",
                            )
                            return

                        cursor.execute(
                            "SELECT COUNT(*) FROM users WHERE username = 'admin_rise'"
                        )
                        admin_user_exists = cursor.fetchone()[0] > 0

                        if not admin_user_exists:
                            log_to_console(
                                "Default admin user 'admin_rise' not found. Creating it...",
                                "INFO",
                            )
                            try:
                                cursor.execute(
                                    """
                                    INSERT INTO users (username, password, role, last_update_date, last_update_userid)
                                    VALUES (?, ?, ?, ?, ?)
                                    """,
                                    (
                                        "admin_rise",
                                        "M@Rych1n!bM0h9s0z!",
                                        "admin",
                                        datetime.now(),
                                        "system_init",
                                    ),
                                )
                                log_to_console(
                                    "Default admin user 'admin_rise' created successfully.",
                                    "INFO",
                                )
                            except Exception as e:
                                log_to_console(
                                    f"Error creating default admin user: {e}", "ERROR"
                                )
                                add_response_to_queue(
                                    f"Failed to create default admin user: {e}", "error"
                                )
                        else:
                            log_to_console(
                                "Default admin user 'admin_rise' already exists.",
                                "INFO",
                            )

                        cursor.execute("SELECT COUNT(*) FROM users")
                        user_count = cursor.fetchone()[0]
                        log_to_console(
                            f"Found {user_count} user(s) in the database.", "INFO"
                        )
                    finally:
                        cursor.close()

            with engine.connect() as connection:
                cursor = connection.connection.cursor()
                cursor.execute(f"SELECT OBJECT_ID(N'students', 'U');")
                students_table_exists = cursor.fetchone()[0] is not None
                cursor.close()
                if students_table_exists:
                    df_students_check = pd.read_sql_query(
                        "SELECT COUNT(*) FROM students", engine
                    )
                    if df_students_check.iloc[0, 0] > 0:
                        update_app_state("dataset_ready", True)
                        # Attempt to load dataframes into application_state if dataset is ready
                        application_state["schools_df"] = read_table_to_dataframe(
                            engine, "schools"
                        )
                        application_state["parents_df"] = read_table_to_dataframe(
                            engine, "parents"
                        )
                        application_state["students_df"] = read_table_to_dataframe(
                            engine, "students"
                        )
                        application_state["student_years_df"] = read_table_to_dataframe(
                            engine, "student_years"
                        )
                        application_state["academic_records_df"] = (
                            read_table_to_dataframe(engine, "academic_records")
                        )
                        application_state["attendance_df"] = read_table_to_dataframe(
                            engine, "attendance_records"
                        )
                        application_state["subjects_df"] = read_table_to_dataframe(
                            engine, "subject_lookup"
                        )
                        application_state["first_names"] = read_table_to_dataframe(
                            engine, "first_names_lookup"
                        )["first_name"].tolist()
                        application_state["last_names"] = read_table_to_dataframe(
                            engine, "last_names_lookup"
                        )["last_name"].tolist()

                    else:
                        update_app_state("dataset_ready", False)
                else:
                    log_to_console(
                        f"Students table does not exist, setting dataset_ready to False.",
                        "WARNING",
                    )
                    update_app_state("dataset_ready", False)

            load_model_and_features()
            log_to_console("Database initialization and setup complete.", "INFO")
        except Exception as e:
            log_to_console(
                f"Database initialization failed during startup: {e}", "CRITICAL"
            )
            update_app_state("db_connected", False)
    else:
        log_to_console(
            f"Failed to get database connection during startup. Application may not function correctly.",
            "CRITICAL",
        )
        update_app_state("db_connected", False)


def on_startup():
    initialize_database()


on_startup()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
