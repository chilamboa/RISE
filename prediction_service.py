# prediction_service.py

import pandas as pd
import joblib
import os
from typing import Dict, Any, Optional, Tuple
from utils import logger
from data_preprocessing import DataPreprocessor
from database_utils import db_manager  # For fetching raw student data


class PredictionService:
    """
    Provides services for predicting student academic performance.
    Loads a pre-trained model and uses the DataPreprocessor.
    """

    def __init__(
        self,
        model_path: str = "models",
        default_model_name: str = "randomforestregressor",
    ):
        self.model_path = model_path
        self.default_model_name = default_model_name
        self.model = self._load_best_model()
        self.preprocessor = DataPreprocessor()  # Initialize preprocessor

    def _load_best_model(self) -> Optional[Any]:
        """
        Loads the best trained model from the specified path.
        Assumes the model is named 'optimized_{model_name}_model.joblib'
        or 'randomforestregressor_model.joblib' if not optimized.
        """
        # Try to load an optimized model first
        optimized_model_filename = f"optimized_{self.default_model_name}_model.joblib"
        model_filepath = os.path.join(self.model_path, optimized_model_filename)

        if not os.path.exists(model_filepath):
            # Fallback to a non-optimized model if optimized one not found
            logger.warning(
                f"Optimized model '{optimized_model_filename}' not found. Attempting to load default '{self.default_model_name}_model.joblib'."
            )
            model_filepath = os.path.join(
                self.model_path, f"{self.default_model_name}_model.joblib"
            )

        if not os.path.exists(model_filepath):
            logger.error(
                f"No prediction model found at {model_filepath}. Please train a model first."
            )
            return None

        try:
            model = joblib.load(model_filepath)
            logger.info(f"Successfully loaded prediction model from {model_filepath}")
            return model
        except Exception as e:
            logger.error(
                f"Error loading prediction model from {model_filepath}: {e}",
                exc_info=True,
            )
            return None

    def get_student_raw_data(self, student_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetches raw student data from the database, including academic records
        and attendance.
        """
        logger.info(f"Fetching raw data for student_id: {student_id}")

        # This query needs to be comprehensive to gather all features
        # required by the preprocessor and the model.
        # It should join across Students, Academic_Records, Attendance,
        # and all relevant lookup tables.
        # Example:
        query = f"""
        SELECT
            s.student_id, s.gender, s.age, s.grade_level,
            hle.name AS home_learning_environment,
            ia.name AS internet_access,
            sh.name AS study_habits,
            ds.name AS disability_status,
            sec.name AS socioeconomic_classification,
            pel.name AS parental_education_level,
            (SELECT mark FROM Academic_Records WHERE student_id = s.student_id FOR JSON PATH) AS academic_records_json,
            (SELECT status, date FROM Attendance WHERE student_id = s.student_id FOR JSON PATH) AS attendance_records_json
        FROM
            Students s
        LEFT JOIN home_learning_environment_lookup hle ON s.home_learning_environment_id = hle.id
        LEFT JOIN internet_access_lookup ia ON s.internet_access_id = ia.id
        LEFT JOIN study_habits_lookup sh ON s.study_habits_id = sh.id
        LEFT JOIN disability_status_lookup ds ON s.disability_status_id = ds.id
        LEFT JOIN socioeconomic_classification_lookup sec ON s.socioeconomic_classification_id = sec.id
        LEFT JOIN parental_education_level_lookup pel ON s.parental_education_level_id = pel.id
        WHERE s.student_id = ?;
        """

        # Execute the query. pyodbc might return JSON as string, so parsing is needed.
        # For simplicity, we'll simulate data here.
        # raw_data_list = db_manager.execute_query(query, (student_id,))

        # Simulate fetching raw data for demonstration
        if student_id == "S001":
            raw_data = {
                "student_id": "S001",
                "gender": "Female",
                "age": 15,
                "grade_level": 9,
                "home_learning_environment": "Conducive",
                "internet_access": "Broadband",
                "study_habits": "Consistent",
                "disability_status": "None",
                "socioeconomic_classification": "Middle",
                "parental_education_level": "Degree",
                "academic_records": [
                    {"subject": "Math", "mark": 75},
                    {"subject": "Science", "mark": 80},
                ],
                "attendance_records": [
                    {"date": "2025-05-05", "status": "Present"},
                    {"date": "2025-05-06", "status": "Present"},
                ],
            }
        elif student_id == "S002":
            raw_data = {
                "student_id": "S002",
                "gender": "Male",
                "age": 16,
                "grade_level": 10,
                "home_learning_environment": "Challenging",
                "internet_access": "Limited",
                "study_habits": "Irregular",
                "disability_status": "Visual Impairment",
                "socioeconomic_classification": "Low",
                "parental_education_level": "High School",
                "academic_records": [
                    {"subject": "Math", "mark": 60},
                    {"subject": "Science", "mark": 55},
                ],
                "attendance_records": [
                    {"date": "2025-05-05", "status": "Absent"},
                    {"date": "2025-05-06", "status": "Present"},
                ],
            }
        else:
            raw_data = None

        if raw_data:
            # If academic_records_json and attendance_records_json are strings from DB, parse them
            # import json
            # if 'academic_records_json' in raw_data and raw_data['academic_records_json']:
            #     raw_data['academic_records'] = json.loads(raw_data.pop('academic_records_json'))
            # if 'attendance_records_json' in raw_data and raw_data['attendance_records_json']:
            #     raw_data['attendance_records'] = json.loads(raw_data.pop('attendance_records_json'))
            logger.info(f"Raw data fetched for student {student_id}.")
            return raw_data
        else:
            logger.warning(f"No raw data found for student_id: {student_id}")
            return None

    def predict_performance(
        self, student_id: str
    ) -> Tuple[Optional[float], Optional[float]]:
        """
        Predicts the academic performance (mark) for a given student.
        Returns the predicted mark and a confidence score (e.g., from model's std dev or a simple range).
        """
        if self.model is None:
            logger.error("Prediction model not loaded. Cannot make predictions.")
            return None, None

        raw_student_data = self.get_student_raw_data(student_id)
        if not raw_student_data:
            logger.error(
                f"Could not retrieve raw data for student {student_id}. Cannot predict."
            )
            return None, None

        # Preprocess the raw data into features suitable for the model
        # The preprocessor expects a dict, and returns a DataFrame of features
        features_df = self.preprocessor.preprocess_student_data(raw_student_data)

        if features_df.empty:
            logger.error(
                f"No features generated for student {student_id} after preprocessing. Cannot predict."
            )
            return None, None

        # Ensure the feature columns match what the model was trained on
        # This is crucial. In a real system, you'd store the feature names
        # used during training and reorder/align them here.
        # For simplicity, we'll assume the preprocessor outputs consistent columns.

        try:
            predicted_mark = self.model.predict(features_df)[0]

            # Simple confidence score (e.g., based on prediction range or model type)
            # For tree-based models, you might use std dev of trees for confidence.
            # For linear models, it's harder. This is a placeholder.
            confidence = 1.0 - (
                abs(predicted_mark - 75) / 100.0
            )  # Example: higher confidence closer to 75
            confidence = max(0.0, min(1.0, confidence))  # Clamp between 0 and 1

            logger.info(
                f"Predicted mark for student {student_id}: {predicted_mark:.2f}, Confidence: {confidence:.2f}"
            )

            # Store prediction in database
            self._store_prediction(student_id, predicted_mark, confidence)

            return float(predicted_mark), float(confidence)
        except Exception as e:
            logger.error(
                f"Error during prediction for student {student_id}: {e}", exc_info=True
            )
            return None, None

    def _store_prediction(
        self, student_id: str, predicted_mark: float, confidence: float
    ):
        """
        Stores the prediction result in the 'predictions' table.
        """
        query = """
        INSERT INTO Predictions (student_id, predicted_mark, confidence_score, prediction_date)
        VALUES (?, ?, ?, GETDATE());
        """
        rows_affected = db_manager.execute_non_query(
            query, (student_id, predicted_mark, confidence)
        )
        if rows_affected > 0:
            logger.info(f"Prediction for student {student_id} stored in database.")
        else:
            logger.error(
                f"Failed to store prediction for student {student_id} in database."
            )


# Example Usage:
if __name__ == "__main__":
    # Ensure db_manager is connected for this test
    try:
        db_manager.connect()
        # Ensure dummy lookup tables are created and a dummy model is saved
        # for DataPreprocessor and PredictionService to function.
        # You can run `model_training.py`'s __main__ block first to generate a model.

        # Create a dummy model file for testing if it doesn't exist
        if not os.path.exists("models/randomforestregressor_model.joblib"):
            logger.warning("No model found. Creating a dummy model for testing.")
            from sklearn.ensemble import RandomForestRegressor
            import numpy as np

            dummy_model = RandomForestRegressor(n_estimators=10)
            # Need some dummy data to fit it
            dummy_X = pd.DataFrame(
                np.random.rand(10, 5), columns=[f"feature{i}" for i in range(5)]
            )
            dummy_y = pd.Series(np.random.randint(50, 90, 10))
            dummy_model.fit(dummy_X, dummy_y)
            os.makedirs("models", exist_ok=True)
            joblib.dump(dummy_model, "models/randomforestregressor_model.joblib")
            logger.info("Dummy model created.")

        service = PredictionService()

        # Test prediction for a known student (S001 in dummy data)
        predicted_mark, confidence = service.predict_performance("S001")
        if predicted_mark is not None:
            print(
                f"\nPrediction for S001: Mark={predicted_mark:.2f}, Confidence={confidence:.2f}"
            )
        else:
            print("\nPrediction for S001 failed.")

        # Test prediction for an unknown student
        predicted_mark_unknown, confidence_unknown = service.predict_performance("S999")
        if predicted_mark_unknown is None:
            print(
                "\nPrediction for S999 (unknown student) correctly failed as expected."
            )

    except Exception as e:
        logger.error(f"An error occurred during prediction_service test: {e}")
    finally:
        db_manager.close()
