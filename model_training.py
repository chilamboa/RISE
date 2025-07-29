# model_training.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os
from utils import logger
from database_utils import db_manager
from data_preprocessing import DataPreprocessor


class ModelTrainer:
    """
    Manages the training, evaluation, and saving of the predictive model.
    """

    def __init__(self, model_save_path: str = "models"):
        self.model_save_path = model_save_path
        # Ensure models directory exists immediately upon initialization
        os.makedirs(self.model_save_path, exist_ok=True)
        logger.info(f"Model save path ensured: {os.path.abspath(self.model_save_path)}")
        self.preprocessor = DataPreprocessor()
        self.model = None

    def train_model(self, model_name: str = "randomforestregressor_model.joblib"):
        """
        Loads data, preprocesses it, trains a RandomForestRegressor model,
        and saves the trained model.
        """
        logger.info("Starting model training process.")

        try:
            # Attempt to load some dummy data or real data if available
            # For a quick test, we'll create synthetic data
            data = pd.DataFrame(
                {
                    "age": [15, 16, 14, 17, 15, 16, 14, 17, 15, 16],
                    "grade_level": [9, 10, 8, 11, 9, 10, 8, 11, 9, 10],
                    "gender_encoded": [1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
                    "attendance_percentage": [90, 85, 95, 80, 92, 88, 91, 78, 85, 93],
                    "home_learning_environment_encoded": [1, 2, 1, 1, 2, 1, 2, 1, 1, 2],
                    "internet_access_encoded": [1, 1, 2, 1, 2, 1, 1, 2, 1, 2],
                    "study_habits_encoded": [1, 2, 1, 2, 1, 1, 2, 1, 2, 1],
                    "disability_status_encoded": [1, 1, 1, 2, 1, 1, 1, 1, 2, 1],
                    "socioeconomic_classification_encoded": [
                        2,
                        1,
                        3,
                        2,
                        1,
                        3,
                        2,
                        1,
                        3,
                        2,
                    ],
                    "parental_education_level_encoded": [3, 2, 1, 3, 2, 1, 3, 2, 1, 3],
                    "race_encoded": [1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
                    "access_to_healthcare_encoded": [1, 1, 2, 1, 1, 2, 1, 1, 2, 1],
                    "access_to_specialized_programs_encoded": [
                        1,
                        2,
                        1,
                        2,
                        1,
                        2,
                        1,
                        2,
                        1,
                        2,
                    ],
                    "allocation_category_encoded": [1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
                    "device_access_encoded": [1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
                    "digital_literacy_encoded": [1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
                    "digital_literacy_support_encoded": [1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
                    "disciplinary_incidents_encoded": [1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
                    "dropout_reason_encoded": [1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
                    "engagement_level_encoded": [1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
                    "extracurricular_activity_type_encoded": [
                        1,
                        2,
                        1,
                        2,
                        1,
                        2,
                        1,
                        2,
                        1,
                        2,
                    ],
                    "extracurricular_role_encoded": [1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
                    "funding_model_encoded": [1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
                    "geographic_density_classification_encoded": [
                        1,
                        2,
                        1,
                        2,
                        1,
                        2,
                        1,
                        2,
                        1,
                        2,
                    ],
                    "health_conditions_encoded": [1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
                    "highest_qualification_encoded": [1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
                    "internet_access_quality_encoded": [1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
                    "intervention_outcome_encoded": [1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
                    "intervention_type_encoded": [1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
                    "language_encoded": [1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
                    "learning_resources_encoded": [1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
                    "local_municipality_encoded": [1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
                    "mental_health_support_encoded": [1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
                    "nutrition_status_encoded": [1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
                    "parental_employment_status_encoded": [
                        1,
                        2,
                        1,
                        2,
                        1,
                        2,
                        1,
                        2,
                        1,
                        2,
                    ],
                    "parental_marital_status_encoded": [1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
                    "parental_tech_support_encoded": [1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
                    "psychological_assessment_type_encoded": [
                        1,
                        2,
                        1,
                        2,
                        1,
                        2,
                        1,
                        2,
                        1,
                        2,
                    ],
                    "school_infrastructure_encoded": [1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
                    "school_phase_encoded": [1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
                    "school_prototype_size_encoded": [1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
                    "school_safety_perception_encoded": [1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
                    "school_specialization_encoded": [1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
                    "school_status_encoded": [1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
                    "school_type_encoded": [1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
                    "social_grants_encoded": [1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
                    "software_platform_access_encoded": [1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
                    "study_environment_encoded": [1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
                    "teacher_effectiveness_rating_encoded": [
                        1,
                        2,
                        1,
                        2,
                        1,
                        2,
                        1,
                        2,
                        1,
                        2,
                    ],
                    "teacher_student_ratio_encoded": [1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
                    "urban_rural_classification_encoded": [
                        1,
                        2,
                        1,
                        2,
                        1,
                        2,
                        1,
                        2,
                        1,
                        2,
                    ],
                    "target_mark": [
                        75,
                        60,
                        85,
                        55,
                        78,
                        65,
                        80,
                        50,
                        70,
                        88,
                    ],  # Target variable
                }
            )

            X = data.drop(columns=["target_mark"])
            y = data["target_mark"]

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            # Initialize and train the model
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.model.fit(X_train, y_train)

            # Evaluate the model
            y_pred = self.model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            logger.info(
                f"Model trained. Mean Squared Error: {mse:.2f}, R2 Score: {r2:.2f}"
            )

            # Save the trained model
            model_path = os.path.join(self.model_save_path, model_name)
            joblib.dump(self.model, model_path)
            logger.info(
                f"Model saved to {os.path.abspath(model_path)}"
            )  # Log absolute path

        except Exception as e:
            logger.error(f"Error during model training: {e}", exc_info=True)
            raise

    def load_model(self, model_name: str = "randomforestregressor_model.joblib"):
        """
        Loads a pre-trained model.
        """
        model_path = os.path.join(self.model_save_path, model_name)
        if os.path.exists(model_path):
            self.model = joblib.load(model_path)
            logger.info(
                f"Model loaded from {os.path.abspath(model_path)}"
            )  # Log absolute path
            return True
        else:
            logger.warning(
                f"Model not found at {os.path.abspath(model_path)}. Please train a model first."
            )
            return False


# Example Usage:
if __name__ == "__main__":
    try:
        db_manager.connect()  # Ensure DB connection is established for preprocessor lookups
        trainer = ModelTrainer()
        trainer.train_model()
    except Exception as e:
        logger.error(f"An error occurred during model training execution: {e}")
    finally:
        db_manager.close()
