import configparser
import pyodbc
from flask import Flask, request, jsonify, send_from_directory
import os
import random
from datetime import date, timedelta

# --- Flask Application Setup ---
# Assuming admin.html is in a 'static' folder relative to app.py
app = Flask(__name__, static_folder='static')

# --- Configuration Management ---
CONFIG_FILE = 'config.ini'
config_parser = configparser.ConfigParser()

def load_config():
    """Loads configuration from config.ini."""
    try:
        config_parser.read(CONFIG_FILE)
        print(f"Configuration loaded from {CONFIG_FILE}")
    except Exception as e:
        print(f"Error loading config.ini: {e}")
        # Optionally, create a default config.ini if it doesn't exist or is invalid
        create_default_config()
        config_parser.read(CONFIG_FILE) # Try reading again after creating default

def create_default_config():
    """Creates a default config.ini file if it doesn't exist or is empty."""
    if not os.path.exists(CONFIG_FILE) or os.stat(CONFIG_FILE).st_size == 0:
        print(f"Creating default {CONFIG_FILE}...")
        # Define default configuration sections and options
        default_config_data = configparser.ConfigParser()

        default_config_data.add_section('DATA_GENERATION')
        default_config_data.set('DATA_GENERATION', 'NUM_SCHOOLS', '12')
        default_config_data.set('DATA_GENERATION', 'NUM_PARENTS', '300')
        default_config_data.set('DATA_GENERATION', 'TOTAL_UNIQUE_STUDENTS', '1100')
        default_config_data.set('DATA_GENERATION', 'START_YEAR', '2017')
        default_config_data.set('DATA_GENERATION', 'END_YEAR', '2025')

        default_config_data.add_section('GENERATE_ALL_DATA')
        default_config_data.set('GENERATE_ALL_DATA', 'SCHOOLS', '10000')
        default_config_data.set('GENERATE_ALL_DATA', 'PARENTS', '300000')
        default_config_data.set('GENERATE_ALL_DATA', 'STUDENTS', '10000000')

        default_config_data.add_section('DATABASE')
        default_config_data.set('DATABASE', 'CONNECTION_STRING', 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=alinatics;DATABASE=StudentMarks;UID=admin_rise;PWD=M@Rych1n!bM0h9s0z!;')

        with open(CONFIG_FILE, 'w') as configfile:
            default_config_data.write(configfile)
        print("Default config.ini created.")

# Load configuration at application startup
load_config()

# --- Database Connection ---
def get_db_connection():
    """Establishes and returns a pyodbc connection to the SQL Server database."""
    try:
        conn_str = config_parser.get('DATABASE', 'CONNECTION_STRING')
        conn = pyodbc.connect(conn_str)
        conn.autocommit = False # Ensure transactions are managed manually
        print("Database connection established.")
        return conn
    except configparser.NoSectionError:
        print("Error: 'DATABASE' section not found in config.ini. Please ensure it exists.")
        return None
    except configparser.NoOptionError:
        print("Error: 'CONNECTION_STRING' option not found in section of config.ini.")
        return None
    except pyodbc.Error as ex:
        sqlstate = ex.args # Get SQLSTATE
        print(f"Database connection error: SQLSTATE {sqlstate} - {ex.args[1]}")
        return None

# --- Route for serving frontend files ---
@app.route('/dashboard')
def serve_dashboard():
    return send_from_directory('templates', 'dashboard.html')

@app.route('/parent-dashboard')
def serve_parent_dashboard():
    return send_from_directory('templates', 'parent_dashboard.html')

@app.route('/teacher-dashboard')
def serve_teacher_dashboard():
    return send_from_directory('templates', 'teacher_dashboard.html')

@app.route('/school-admin-dashboard')
def serve_school_admin_dashboard():
    return send_from_directory('templates', 'school_admin_dashboard.html')

@app.route('/student-management')
def serve_student_management():
    return send_from_directory('templates', 'student_management.html')

@app.route('/user-management')
def serve_user_management():
    return send_from_directory('templates', 'user_management.html')

# --- API Endpoints ---

@app.route('/api/config', methods=['GET'])
def get_config():
    """
    API endpoint to retrieve the current configuration from config.ini.
    Returns a JSON object containing all relevant configuration parameters.
    """
    try:
        response_config = {}
        for section in config_parser.sections():
            response_config[section] = {key: config_parser.get(section, key) for key in config_parser.options(section)}
        return jsonify(response_config), 200
    except Exception as e:
        print(f"Error getting config: {e}")
        return jsonify({"error": "Failed to retrieve configuration"}), 500

@app.route('/api/config/update', methods=['POST'])
def update_config():
    """
    API endpoint to update a specific configuration parameter in config.ini.
    Expects a JSON payload: {"section": "SECTION_NAME", "key": "KEY_NAME", "value": "NEW_VALUE"}.
    """
    data = request.get_json()
    section = data.get('section')
    key = data.get('key')
    value = str(data.get('value')) # Ensure value is stored as string in configparser

    if not all([section, key, value is not None]):
        return jsonify({"error": "Missing section, key, or value"}), 400

    try:
        if not config_parser.has_section(section):
            config_parser.add_section(section)

        config_parser.set(section, key, value)
        with open(CONFIG_FILE, 'w') as configfile:
            config_parser.write(configfile)

        # After updating, re-read the config to ensure in-memory parser is consistent
        # and return the full updated config to the frontend for synchronization
        load_config()
        response_config = {}
        for sec in config_parser.sections():
            response_config[sec] = {k: config_parser.get(sec, k) for k in config_parser.options(sec)}

        print(f"Config updated: [{section}] {key} = {value}")
        return jsonify(response_config), 200
    except Exception as e:
        print(f"Error updating config: {e}")
        return jsonify({"error": f"Failed to update configuration: {e}"}), 500

@app.route('/api/generate/<data_type>', methods=['POST'])
def generate_data(data_type):
    """
    API endpoint to trigger individual data generation processes.
    <data_type> can be 'schools', 'parents', 'students', 'academicHistory', 'attendance'.
    """
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            raise Exception("Could not connect to database.")

        cursor = conn.cursor()

        # Read generation parameters from config.ini
        num_schools = config_parser.getint('DATA_GENERATION', 'NUM_SCHOOLS')
        num_parents = config_parser.getint('DATA_GENERATION', 'NUM_PARENTS')
        total_students = config_parser.getint('DATA_GENERATION', 'TOTAL_UNIQUE_STUDENTS')
        start_year = config_parser.getint('DATA_GENERATION', 'START_YEAR')
        end_year = config_parser.getint('DATA_GENERATION', 'END_YEAR')

        if data_type == 'schools':
            populate_schools(cursor, num_schools)
            conn.commit()
            message = f"Populated {num_schools} schools."
        elif data_type == 'parents':
            generate_parents(cursor, num_parents)
            conn.commit()
            message = f"Generated {num_parents} parents."
        elif data_type == 'students':
            enroll_students(cursor, total_students)
            conn.commit()
            message = f"Enrolled {total_students} students."
        elif data_type == 'academicHistory':
            assign_academic_history(cursor, start_year, end_year)
            conn.commit()
            message = "Assigned academic history."
        elif data_type == 'attendance':
            generate_attendance(cursor, start_year, end_year)
            conn.commit()
            message = "Generated attendance records."
        else:
            return jsonify({"error": "Invalid data type for generation"}), 400

        return jsonify({"message": message}), 200

    except Exception as e:
        print(f"Error generating {data_type}: {e}")
        if conn:
            conn.rollback()
            print("Transaction rolled back.")
        return jsonify({"error": f"Failed to generate {data_type}: {e}"}), 500
    finally:
        if conn:
            conn.close()

def execute_sql_script(cursor, file_path):
    """Executes a SQL script from a file."""
    with open(file_path, 'r') as f:
        sql_script = f.read()
    cursor.execute(sql_script)

@app.route('/api/db/execute-script/<script_name>', methods=['POST'])
def execute_db_script(script_name):
    """API endpoint to execute a SQL script."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            raise Exception("Could not connect to database.")

        cursor = conn.cursor()

        if script_name == 'drop_create':
            execute_sql_script(cursor, 'drop_create_tables.sql')
            message = "Tables dropped and recreated successfully."
        elif script_name == 'insert_data':
            execute_sql_script(cursor, 'insert_data_student_marks_tables.sql')
            message = "Sample data inserted successfully."
        else:
            return jsonify({"error": "Invalid script name"}), 400

        conn.commit()
        return jsonify({"message": message}), 200

    except Exception as e:
        print(f"Error executing script {script_name}: {e}")
        if conn:
            conn.rollback()
        return jsonify({"error": f"Failed to execute script {script_name}: {e}"}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/generate/all', methods=['POST'])
def generate_all_data():
    """
    API endpoint to clear all existing data and regenerate all datasets from scratch.
    This operation is transactional.
    """
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            raise Exception("Could not connect to database.")

        cursor = conn.cursor()

        # Read generation parameters from the centralized 'DATA_GENERATION' section
        num_schools = config_parser.getint('DATA_GENERATION', 'NUM_SCHOOLS')
        num_parents = config_parser.getint('DATA_GENERATION', 'NUM_PARENTS')
        total_students = config_parser.getint('DATA_GENERATION', 'TOTAL_UNIQUE_STUDENTS')
        start_year = config_parser.getint('DATA_GENERATION', 'START_YEAR')
        end_year = config_parser.getint('DATA_GENERATION', 'END_YEAR')

        # --- Start Transaction for entire process ---
        # (conn.autocommit = False ensures this is implicitly a transaction until commit/rollback)

        # 1. Clear existing data
        clear_all_data(cursor)

        # 2. Generate all datasets in correct order
        populate_schools(cursor, num_schools)
        generate_parents(cursor, num_parents)
        enroll_students(cursor, total_students)
        assign_academic_history(cursor, start_year, end_year)
        generate_attendance(cursor, start_year, end_year)

        conn.commit() # Commit all changes if successful
        print("All data cleared and regenerated successfully.")
        return jsonify({"message": "All data cleared and regenerated successfully!"}), 200

    except Exception as e:
        print(f"Error generating all data: {e}")
        if conn:
            conn.rollback() # Rollback all changes if any step fails
            print("Full generation transaction rolled back.")
        return jsonify({"error": f"Failed to generate all data: {e}"}), 500
    finally:
        if conn:
            conn.close()

# --- Data Generation and Clearing Functions (Conceptual Implementations) ---
# These functions would contain your actual database interaction logic.
# They are designed to be idempotent where applicable.

def execute_upsert(cursor, table_name, unique_cols, data):
    """
    Conceptual function to perform an UPSERT operation for SQL Server.
    This is a simplified placeholder and needs to be adapted to your specific SQL Server syntax
    and table schemas, potentially using MERGE statements or a more robust SELECT + INSERT/UPDATE.

    Parameters:
    - cursor: pyodbc cursor object
    - table_name: Name of the table to upsert into
    - unique_cols: List of column names that form the unique key for checking existence
    - data: Dictionary where keys are column names and values are data to insert/update
    """
    # Construct WHERE clause for checking existence
    where_clause = " AND ".join([f"{col} =?" for col in unique_cols])
    select_sql = f"SELECT 1 FROM {table_name} WHERE {where_clause}"

    # Prepare values for the SELECT statement
    select_values = [data[col] for col in unique_cols]

    # Execute SELECT to check for existence
    cursor.execute(select_sql, *select_values)
    exists = cursor.fetchone()

    if exists:
        # Update existing record (simplified)
        # Exclude unique_cols from SET clause if they are not meant to be updated
        set_clause = ", ".join([f"{k} =?" for k in data.keys() if k not in unique_cols])
        update_sql = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
        update_values = [data[k] for k in data.keys() if k not in unique_cols] + select_values
        print(f"Updating {table_name} with {data}")
        cursor.execute(update_sql, *update_values)
    else:
        # Insert new record
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        insert_values = list(data.values())
        print(f"Inserting into {table_name} with {data}")
        cursor.execute(insert_sql, *insert_values)

def populate_schools(cursor, num_schools):
    """
    Populates the Schools table. Designed to be idempotent.
    Requires unique constraint on (SchoolName, Address) or similar.
    """
    print(f"Populating {num_schools} schools...")
    for i in range(num_schools):
        school_data = {
            "SchoolName": f"School_{i+1}",
            "Address": f"{i+1} Main St",
            "Capacity": 1000 + (i % 5) * 100
        }
        # In a real scenario, you'd generate more diverse data
        execute_upsert(cursor, "Schools", ["SchoolName", "Address"], school_data)
    print(f"Finished populating {num_schools} schools.")

def generate_parents(cursor, num_parents):
    """
    Generates parent records. Designed to be idempotent.
    Requires unique constraint on (Email) or (FirstName, LastName, Phone) or similar.
    """
    print(f"Generating {num_parents} parents...")
    for i in range(num_parents):
        parent_data = {
            "FirstName": f"ParentFN_{i+1}",
            "LastName": f"ParentLN_{i+1}",
            "Email": f"parent{i+1}@example.com"
        }
        execute_upsert(cursor, "Parents", ["Email"], parent_data)
    print(f"Finished generating {num_parents} parents.")

def enroll_students(cursor, total_students):
    """
    Enrolls students and links them to existing schools and parents.
    Designed to be idempotent. Requires unique constraint on (StudentID) or similar.
    This function needs to query existing School and Parent IDs.
    """
    print(f"Enrolling {total_students} students...")
    # Fetch existing school and parent IDs to ensure referential integrity
    # Assuming SchoolID and ParentID are the first columns in their respective tables
    cursor.execute("SELECT SchoolID FROM Schools")
    school_ids = [row[0] for row in cursor.fetchall()] # Extract just the ID

    cursor.execute("SELECT ParentID FROM Parents")
    parent_ids = [row[0] for row in cursor.fetchall()] # Extract just the ID

    if not school_ids or not parent_ids:
        print("Warning: No schools or parents found. Cannot enroll students.")
        return

    for i in range(total_students):
        student_data = {
            "StudentID": f"S{i+1:05d}",
            "FirstName": f"StudentFN_{i+1}",
            "LastName": f"StudentLN_{i+1}",
            "SchoolID": random.choice(school_ids), # Link to an existing school
            "ParentID": random.choice(parent_ids)  # Link to an existing parent
        }
        execute_upsert(cursor, "Students", ["StudentID"], student_data)
    print(f"Finished enrolling {total_students} students.")

def assign_academic_history(cursor, start_year, end_year):
    """
    Assigns academic history to existing students. Designed to be idempotent.
    Requires unique constraint on (StudentID, Year, Subject) or similar.
    """
    print("Assigning academic history...")
    cursor.execute("SELECT StudentID FROM Students")
    student_ids = [row[0] for row in cursor.fetchall()]

    if not student_ids:
        print("Warning: No students found. Cannot assign academic history.")
        return

    subjects = ["Math", "Science", "English", "History", "Geography", "Art", "Music", "Physical Education"]
    grades = ["A", "B", "C", "D", "F"]
    for student_id in student_ids:
        for year in range(start_year, end_year + 1):
            for subject in subjects:
                history_data = {
                    "StudentID": student_id,
                    "Year": year,
                    "Subject": subject,
                    "Grade": random.choice(grades)
                }
                execute_upsert(cursor, "AcademicHistory", ["StudentID", "Year", "Subject"], history_data)
    print("Finished assigning academic history.")

def generate_attendance(cursor, start_year, end_year):
    """
    Generates attendance records for existing students. Designed to be idempotent.
    Requires unique constraint on (StudentID, AttendanceDate) or similar.
    """
    print("Generating attendance records...")
    cursor.execute("SELECT StudentID FROM Students")
    student_ids = [row[0] for row in cursor.fetchall()]

    if not student_ids:
        print("Warning: No students found. Cannot generate attendance.")
        return

    attendance_statuses = ["Present", "Absent", "Late"]
    # Generate attendance for a sample period (e.g., 30 days in a school year)
    for student_id in student_ids:
        for day_offset in range(30): # Example: 30 days of attendance
            current_date = date(start_year, 9, 1) + timedelta(days=day_offset) # Starting Sept 1st
            attendance_data = {
                "StudentID": student_id,
                "AttendanceDate": current_date.strftime('%Y-%m-%d'), # Format as YYYY-MM-DD
                "Status": random.choice(attendance_statuses)
            }
            execute_upsert(cursor, "Attendance", ["StudentID", "AttendanceDate"], attendance_data)
    print("Finished generating attendance records.")

def clear_all_data(cursor):
    """
    Clears all data from relevant tables in the correct order to respect foreign keys.
    This operation is transactional (managed by the calling function's commit/rollback).
    """
    print("Clearing all existing data...")
    # Order of deletion is crucial due to foreign key constraints:
    # Child tables first, then parent tables.
    tables_to_clear = ["Attendance", "AcademicHistory", "Students", "Parents", "Schools"]

    for table in tables_to_clear:
        try:
            cursor.execute(f"DELETE FROM {table}")
            print(f"Cleared data from {table}.")
        except pyodbc.Error as ex:
            sqlstate = ex.args
            print(f"Error clearing {table}: SQLSTATE {sqlstate} - {ex.args[1]}")
            raise # Re-raise to trigger rollback

    # Optional: Reset identity columns if using DELETE FROM and need IDs to restart from 1
    # This is database-specific. For SQL Server:
    # for table in tables_to_clear:
    #     try:
    #         # This command might require specific permissions or might not apply to all tables
    #         cursor.execute(f"DBCC CHECKIDENT ('{table}', RESEED, 0)")
    #         print(f"Reset identity for {table}.")
    #     except pyodbc.Error as ex:
    #         # Handle cases where table might not have an identity column or permission issues
    #         print(f"Could not reset identity for {table}: {ex.args[1]}")
    print("Finished clearing all existing data.")

# --- Run Flask App ---
if __name__ == '__main__':
    # Ensure config.ini exists and is populated before running the app
    create_default_config()
    app.run(debug=True) # debug=True is for development, set to False for production
