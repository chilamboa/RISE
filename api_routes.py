# api_routes.py

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from utils import logger
from database_utils import db_manager  # For general DB operations and lookup management

# Import services
from prediction_service import PredictionService
from intervention_rl_agent import RLInterventionAgent
from model_interpretability import ModelInterpretabilityService
from chatbot_service import ChatbotService

# from model_training import ModelTrainer # If you need an API to trigger retraining

router = APIRouter()

# Initialize services (these should ideally be singleton instances or dependency injected)
prediction_service = PredictionService()
rl_agent = RLInterventionAgent()  # Default PPO
interpretability_service = ModelInterpretabilityService()
chatbot_service = ChatbotService()
# model_trainer = ModelTrainer() # Uncomment if you need to expose training via API


# --- Pydantic Models for Request/Response Bodies ---
class LoginRequest(BaseModel):
    username: str
    password: str


class PredictionRequest(BaseModel):
    student_id: str


class ChatbotRequest(BaseModel):
    user_query: str
    user_role: str = "Student"  # Default role


class GenericResponse(BaseModel):
    message: str
    status: str = "success"
    data: Optional[Dict[str, Any]] = None


class UserProfile(BaseModel):
    user_id: str
    username: str
    role: str
    email: Optional[str] = None


class StudentData(BaseModel):
    student_id: str
    name: str
    grade_level: int
    # Add other relevant student fields


class AcademicRecord(BaseModel):
    subject: str
    mark: float
    assessment_type: str


class AttendanceRecord(BaseModel):
    date: str
    status: str


class InterventionRecommendation(BaseModel):
    intervention_id: int
    name: str
    description: str
    # Add other relevant intervention details


# --- Dependency for authenticated user (conceptual) ---
# In a real app, this would involve JWT token verification
# and fetching user details from the database.
async def get_current_user(token: str = Depends(lambda: "dummy_token")):  # Placeholder
    # This is a mock function. Replace with actual authentication logic.
    if token != "dummy_token":  # For demonstration, a simple check
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Mock user roles for testing
    mock_users = {
        "user1": {"user_id": "U001", "username": "teacher_ali", "role": "Teacher"},
        "user2": {"user_id": "U002", "username": "parent_zola", "role": "Parent"},
        "user3": {"user_id": "U003", "username": "admin_sys", "role": "System Admin"},
    }
    # In a real app, you'd decode the JWT token to get user_id and role
    return mock_users.get("user1")  # Return a default mock user


# --- API Endpoints ---


@router.post("/login", response_model=GenericResponse)
async def login(request: LoginRequest):
    """
    Handles user authentication.
    """
    logger.info(f"Login attempt for username: {request.username}")
    # In a real application:
    # 1. Query database for user by username
    # 2. Verify hashed password
    # 3. Generate JWT token
    # 4. Return token and user role

    # Mock login for demonstration
    if request.username == "testuser" and request.password == "password":
        logger.info(f"User {request.username} logged in successfully.")
        return GenericResponse(
            message="Login successful",
            data={"token": "mock_jwt_token", "role": "Student"},
        )
    elif request.username == "teacher" and request.password == "password":
        logger.info(f"User {request.username} logged in successfully.")
        return GenericResponse(
            message="Login successful",
            data={"token": "mock_jwt_token_teacher", "role": "Teacher"},
        )
    elif request.username == "parent" and request.password == "password":
        logger.info(f"User {request.username} logged in successfully.")
        return GenericResponse(
            message="Login successful",
            data={"token": "mock_jwt_token_parent", "role": "Parent"},
        )
    else:
        logger.warning(f"Failed login attempt for username: {request.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )


@router.get("/user/profile", response_model=UserProfile)
async def get_user_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Retrieves the profile of the currently authenticated user.
    """
    return UserProfile(**current_user)


# --- Student Data Management (Admin/Educator) ---
@router.get("/students/{student_id}", response_model=StudentData)
async def get_student_details(
    student_id: str, current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Retrieves detailed information for a specific student.
    Requires appropriate user role (e.g., Teacher, Admin, Parent if linked).
    """
    logger.info(
        f"Fetching student details for {student_id} by {current_user['username']}"
    )
    # Query database for student details
    query = "SELECT student_id, name, grade_level FROM Students WHERE student_id = ?;"
    student_data = db_manager.execute_query(query, (student_id,))
    if student_data:
        return StudentData(**student_data[0])
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
    )


@router.get(
    "/students/{student_id}/academic_records", response_model=List[AcademicRecord]
)
async def get_student_academic_records(
    student_id: str, current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Retrieves academic records for a specific student.
    """
    logger.info(
        f"Fetching academic records for {student_id} by {current_user['username']}"
    )
    query = """
    SELECT ar.subject, ar.mark, aat.name AS assessment_type
    FROM Academic_Records ar
    JOIN academic_assessment_type_lookup aat ON ar.assessment_type_id = aat.id
    WHERE ar.student_id = ?;
    """
    records = db_manager.execute_query(query, (student_id,))
    return [AcademicRecord(**rec) for rec in records]


@router.get(
    "/students/{student_id}/attendance_records", response_model=List[AttendanceRecord]
)
async def get_student_attendance_records(
    student_id: str, current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Retrieves attendance records for a specific student.
    """
    logger.info(
        f"Fetching attendance records for {student_id} by {current_user['username']}"
    )
    query = """
    SELECT date, ast.name AS status
    FROM Attendance att
    JOIN attendance_status_lookup ast ON att.status_id = ast.id
    WHERE att.student_id = ?;
    """
    records = db_manager.execute_query(query, (student_id,))
    return [AttendanceRecord(**rec) for rec in records]


# --- Prediction Service ---
@router.post("/predict", response_model=Dict[str, float])
async def get_prediction(
    request: PredictionRequest, current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Endpoint to get predicted academic performance for a student.
    """
    logger.info(
        f"Prediction request for student {request.student_id} by {current_user['username']}"
    )
    predicted_mark, confidence = prediction_service.predict_performance(
        request.student_id
    )
    if predicted_mark is not None:
        return {"predicted_mark": predicted_mark, "confidence": confidence}
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Could not generate prediction",
    )


# --- Intervention Recommendation Service ---
@router.post("/interventions/recommend", response_model=InterventionRecommendation)
async def recommend_intervention_api(
    request: PredictionRequest, current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Endpoint to get a recommended intervention for a student based on RL agent.
    """
    logger.info(
        f"Intervention recommendation request for student {request.student_id} by {current_user['username']}"
    )
    recommended_action_id = rl_agent.recommend_intervention(request.student_id)

    if recommended_action_id is not None:
        # Fetch intervention details from database using the ID
        query = (
            "SELECT id, name, description FROM intervention_type_lookup WHERE id = ?;"
        )
        intervention_details = db_manager.execute_query(query, (recommended_action_id,))
        if intervention_details:
            return InterventionRecommendation(**intervention_details[0])
        else:
            logger.error(
                f"Intervention details not found for ID: {recommended_action_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Intervention details not found",
            )
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Could not recommend an intervention",
    )


# --- Model Interpretability Service ---
@router.post("/explain_prediction", response_model=Dict[str, float])
async def get_explanation(
    request: PredictionRequest, current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Endpoint to get SHAP explanations for a student's predicted mark.
    """
    logger.info(
        f"Explanation request for student {request.student_id} by {current_user['username']}"
    )
    feature_importance = interpretability_service.explain_prediction(request.student_id)
    if feature_importance:
        return feature_importance
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Could not generate explanation",
    )


# --- Chatbot Service ---
@router.post("/chatbot", response_model=Dict[str, str])
async def chat_with_naledi(
    request: ChatbotRequest, current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Endpoint for interacting with the Naledi chatbot.
    """
    logger.info(
        f"Chatbot query from {current_user['username']} (Role: {request.user_role}): '{request.user_query}'"
    )
    response = chatbot_service.get_chatbot_response(
        request.user_query, request.user_role
    )
    return response


# --- Lookup Table Management (Admin only) ---
@router.get("/lookup/{table_name}", response_model=List[Dict[str, Any]])
async def get_lookup_table(
    table_name: str, current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Retrieves data from any lookup table. Requires System Admin role.
    """
    if current_user["role"] != "System Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Requires System Admin role.",
        )

    logger.info(f"Admin {current_user['username']} fetching lookup table: {table_name}")
    df = db_manager.get_lookup_data(table_name)
    if not df.empty:
        return df.to_dict(orient="records")
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Lookup table '{table_name}' not found or empty.",
    )


@router.post("/lookup/{table_name}/add", response_model=GenericResponse)
async def add_lookup_entry(
    table_name: str,
    entry: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Adds a new entry to a lookup table. Requires System Admin role.
    """
    if current_user["role"] != "System Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Requires System Admin role.",
        )

    logger.info(
        f"Admin {current_user['username']} adding entry to {table_name}: {entry}"
    )

    # Construct INSERT query dynamically
    columns = ", ".join(entry.keys())
    placeholders = ", ".join(["?"] * len(entry))
    query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders});"

    try:
        rows_affected = db_manager.execute_non_query(query, tuple(entry.values()))
        if rows_affected > 0:
            # Reload chatbot KB if it's the chatbot table
            if table_name.lower() == "chatbot_knowledge_base":
                chatbot_service._load_knowledge_base()
            return GenericResponse(message=f"Entry added to {table_name} successfully.")
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add entry.",
            )
    except Exception as e:
        logger.error(f"Error adding entry to {table_name}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {e}",
        )


# --- Synthetic Data Generation (Admin only) ---
@router.post("/generate_synthetic_data", response_model=GenericResponse)
async def generate_synthetic_data_api(
    num_students: int = 100, current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Generates synthetic data for testing purposes. Requires System Admin role.
    """
    if current_user["role"] != "System Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Requires System Admin role.",
        )

    logger.info(
        f"Admin {current_user['username']} generating {num_students} synthetic students and related data."
    )

    # This function would be in a separate utility module or within this service
    # For now, we'll put a placeholder for the logic.
    try:
        # Call a function to generate and insert synthetic data
        # synthetic_data_generator.generate_all_data(num_students)
        logger.info(f"Simulating generation of {num_students} synthetic data records.")
        return GenericResponse(
            message=f"Successfully initiated generation of {num_students} synthetic data records."
        )
    except Exception as e:
        logger.error(f"Error generating synthetic data: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate synthetic data: {e}",
        )


# --- Model Retraining (Admin only, conceptual) ---
# @router.post("/train_models", response_model=GenericResponse)
# async def trigger_model_training(current_user: Dict[str, Any] = Depends(get_current_user)):
#     """
#     Triggers the retraining of all machine learning models. Requires System Admin role.
#     """
#     if current_user['role'] != "System Admin":
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied. Requires System Admin role.")

#     logger.info(f"Admin {current_user['username']} triggering model retraining.")
#     try:
#         model_trainer.train_all_models()
#         return GenericResponse(message="Model retraining initiated successfully.")
#     except Exception as e:
#         logger.error(f"Error during model retraining: {e}", exc_info=True)
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Model retraining failed: {e}")

# @router.post("/optimize_hyperparameters/{model_name}", response_model=GenericResponse)
# async def trigger_hyperparameter_optimization(model_name: str, current_user: Dict[str, Any] = Depends(get_current_user)):
#     """
#     Triggers hyperparameter optimization for a specific model. Requires System Admin role.
#     """
#     if current_user['role'] != "System Admin":
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied. Requires System Admin role.")

#     logger.info(f"Admin {current_user['username']} triggering hyperparameter optimization for {model_name}.")
#     try:
#         from hyperparameter_optimization import HyperparameterOptimizer # Import locally to avoid circular
#         optimizer = HyperparameterOptimizer()
#         best_params = optimizer.optimize_model(model_name, n_trials=50) # Use more trials in production
#         if best_params:
#             return GenericResponse(message=f"Hyperparameter optimization for {model_name} completed. Best params: {best_params}", data=best_params)
#         else:
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Hyperparameter optimization for {model_name} failed.")
#     except Exception as e:
#         logger.error(f"Error during hyperparameter optimization: {e}", exc_info=True)
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Hyperparameter optimization failed: {e}")

# Example Usage (for testing API endpoints locally with Uvicorn):
if __name__ == "__main__":
    import uvicorn

    # Ensure db_manager is connected for this test
    try:
        db_manager.connect()
        # You might want to run model_training.py and hyperparameter_optimization.py
        # main blocks first to ensure models are saved for prediction/interpretability services.

        # Create dummy tables for testing if they don't exist
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Students')
            CREATE TABLE Students (student_id NVARCHAR(50) PRIMARY KEY, name NVARCHAR(100), grade_level INT,
            gender NVARCHAR(50), age INT, home_learning_environment_id INT, internet_access_id INT,
            study_habits_id INT, disability_status_id INT, socioeconomic_classification_id INT,
            parental_education_level_id INT, dropout_risk FLOAT);
        """
        )
        db_manager.execute_non_query(
            """
            INSERT INTO Students (student_id, name, grade_level, gender, age, home_learning_environment_id, internet_access_id, study_habits_id, disability_status_id, socioeconomic_classification_id, parental_education_level_id, dropout_risk)
            VALUES ('S001', 'Alice Smith', 9, 1, 15, 1, 1, 1, 1, 1, 1, 0.1)
            WHERE NOT EXISTS (SELECT 1 FROM Students WHERE student_id = 'S001');
        """
        )
        db_manager.execute_non_query(
            """
            INSERT INTO Students (student_id, name, grade_level, gender, age, home_learning_environment_id, internet_access_id, study_habits_id, disability_status_id, socioeconomic_classification_id, parental_education_level_id, dropout_risk)
            VALUES ('S002', 'Bob Johnson', 10, 2, 16, 2, 2, 2, 2, 2, 2, 0.5)
            WHERE NOT EXISTS (SELECT 1 FROM Students WHERE student_id = 'S002');
        """
        )

        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Academic_Records')
            CREATE TABLE Academic_Records (record_id INT IDENTITY(1,1) PRIMARY KEY, student_id NVARCHAR(50), subject NVARCHAR(100), mark FLOAT, assessment_type_id INT);
        """
        )
        db_manager.execute_non_query(
            "INSERT INTO Academic_Records (student_id, subject, mark, assessment_type_id) VALUES ('S001', 'Math', 75.0, 1) WHERE NOT EXISTS (SELECT 1 FROM Academic_Records WHERE student_id = 'S001' AND subject = 'Math');"
        )
        db_manager.execute_non_query(
            "INSERT INTO Academic_Records (student_id, subject, mark, assessment_type_id) VALUES ('S001', 'Science', 80.0, 1) WHERE NOT EXISTS (SELECT 1 FROM Academic_Records WHERE student_id = 'S001' AND subject = 'Science');"
        )
        db_manager.execute_non_query(
            "INSERT INTO Academic_Records (student_id, subject, mark, assessment_type_id) VALUES ('S002', 'Math', 60.0, 1) WHERE NOT EXISTS (SELECT 1 FROM Academic_Records WHERE student_id = 'S002' AND subject = 'Math');"
        )

        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Attendance')
            CREATE TABLE Attendance (attendance_id INT IDENTITY(1,1) PRIMARY KEY, student_id NVARCHAR(50), date DATE, status_id INT);
        """
        )
        db_manager.execute_non_query(
            "INSERT INTO Attendance (student_id, date, status_id) VALUES ('S001', '2025-05-05', 1) WHERE NOT EXISTS (SELECT 1 FROM Attendance WHERE student_id = 'S001' AND date = '2025-05-05');"
        )
        db_manager.execute_non_query(
            "INSERT INTO Attendance (student_id, date, status_id) VALUES ('S001', '2025-05-06', 1) WHERE NOT EXISTS (SELECT 1 FROM Attendance WHERE student_id = 'S001' AND date = '2025-05-06');"
        )
        db_manager.execute_non_query(
            "INSERT INTO Attendance (student_id, date, status_id) VALUES ('S002', '2025-05-05', 2) WHERE NOT EXISTS (SELECT 1 FROM Attendance WHERE student_id = 'S002' AND date = '2025-05-05');"
        )

        # Ensure lookup tables for preprocessor are created (as in data_preprocessing.py __main__)
        # Ensure intervention_type_lookup is created (as in intervention_rl_environment.py __main__)
        # Ensure Chatbot_Knowledge_Base is created (as in chatbot_service.py __main__)
        # Ensure Predictions table exists for storing predictions
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Predictions')
            CREATE TABLE Predictions (
                prediction_id INT IDENTITY(1,1) PRIMARY KEY,
                student_id NVARCHAR(50) NOT NULL,
                predicted_mark FLOAT,
                confidence_score FLOAT,
                prediction_date DATETIME DEFAULT GETDATE()
            );
        """
        )
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'academic_assessment_type_lookup')
            CREATE TABLE academic_assessment_type_lookup (id INT PRIMARY KEY, name NVARCHAR(50));
        """
        )
        db_manager.execute_non_query(
            "INSERT INTO academic_assessment_type_lookup (id, name) VALUES (1, 'Exam') WHERE NOT EXISTS (SELECT 1 FROM academic_assessment_type_lookup WHERE id = 1);"
        )
        db_manager.execute_non_query(
            "INSERT INTO academic_assessment_type_lookup (id, name) VALUES (2, 'Assignment') WHERE NOT EXISTS (SELECT 1 FROM academic_assessment_type_lookup WHERE id = 2);"
        )

        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'attendance_status_lookup')
            CREATE TABLE attendance_status_lookup (id INT PRIMARY KEY, name NVARCHAR(50));
        """
        )
        db_manager.execute_non_query(
            "INSERT INTO attendance_status_lookup (id, name) VALUES (1, 'Present') WHERE NOT EXISTS (SELECT 1 FROM attendance_status_lookup WHERE id = 1);"
        )
        db_manager.execute_non_query(
            "INSERT INTO attendance_status_lookup (id, name) VALUES (2, 'Absent') WHERE NOT EXISTS (SELECT 1 FROM attendance_status_lookup WHERE id = 2);"
        )

        # Run the FastAPI application using Uvicorn
        # This will make the API endpoints available at http://127.0.0.1:8000
        print("\n--- Starting FastAPI Application (API Endpoints) ---")
        print("Access API documentation at: http://127.0.0.1:8000/docs")
        print("Access the web app at: http://127.0.0.1:8000/")
        uvicorn.run(router, host="0.0.0.0", port=8000)

    except Exception as e:
        logger.error(f"An error occurred during api_routes test: {e}")
    finally:
        db_manager.close()
