# model_interpretability.py

import shap
import pandas as pd
import joblib
import os
from typing import Dict, Any, Optional, List
from utils import logger
from data_preprocessing import DataPreprocessor
from database_utils import db_manager  # For fetching raw student data and training data


class ModelInterpretabilityService:
    """
    Provides interpretability for machine learning model predictions using SHAP.
    Explains individual model outputs by attributing the contribution of each feature.
    """

    def __init__(
        self,
        model_path: str = "models",
        default_model_name: str = "randomforestregressor",
    ):
        self.model_path = model_path
        self.default_model_name = default_model_name
        self.model = self._load_model()
        self.preprocessor = DataPreprocessor()
        self.explainer = None
        self.background_data = self._load_and_preprocess_background_data()

        if self.model and not self.background_data.empty:
            self._initialize_explainer()
        elif not self.background_data.empty:
            logger.warning(
                "Model not loaded, SHAP explainer cannot be fully initialized."
            )
        else:
            logger.error(
                "Background data is empty. SHAP explainer cannot be initialized."
            )

    def _load_model(self) -> Optional[Any]:
        """
        Loads the best trained prediction model.
        """
        optimized_model_filename = f"optimized_{self.default_model_name}_model.joblib"
        model_filepath = os.path.join(self.model_path, optimized_model_filename)

        if not os.path.exists(model_filepath):
            logger.warning(
                f"Optimized model '{optimized_model_filename}' not found. Attempting to load default '{self.default_model_name}_model.joblib'."
            )
            model_filepath = os.path.join(
                self.model_path, f"{self.default_model_name}_model.joblib"
            )

        if not os.path.exists(model_filepath):
            logger.error(
                f"No prediction model found at {model_filepath}. Cannot initialize interpretability service."
            )
            return None

        try:
            model = joblib.load(model_filepath)
            logger.info(
                f"Successfully loaded prediction model for interpretability from {model_filepath}"
            )
            return model
        except Exception as e:
            logger.error(
                f"Error loading prediction model for interpretability from {model_filepath}: {e}",
                exc_info=True,
            )
            return None

    def _load_and_preprocess_background_data(self) -> pd.DataFrame:
        """
        Loads a representative sample of the training data to be used as background
        data for SHAP explainer.
        """
        logger.info("Loading and preprocessing background data for SHAP.")
        # This should ideally load a sample of your *original* training data,
        # then preprocess it using the same preprocessor.
        # Simulating dummy raw data for demonstration (similar to model_training)
        raw_data_list = [
            {
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
                "target_mark": 75,
                "attendance_records": [
                    {"date": "2025-05-05", "status": "Present"},
                    {"date": "2025-05-06", "status": "Present"},
                ],
            },
            {
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
                "target_mark": 60,
                "attendance_records": [
                    {"date": "2025-05-05", "status": "Absent"},
                    {"date": "2025-05-06", "status": "Present"},
                ],
            },
            {
                "student_id": "S003",
                "gender": "Female",
                "age": 14,
                "grade_level": 8,
                "home_learning_environment": "Conducive",
                "internet_access": "Broadband",
                "study_habits": "Consistent",
                "disability_status": "None",
                "socioeconomic_classification": "High",
                "parental_education_level": "Postgraduate",
                "target_mark": 90,
                "attendance_records": [
                    {"date": "2025-05-05", "status": "Present"},
                    {"date": "2025-05-06", "status": "Present"},
                ],
            },
        ]

        processed_data_frames = []
        for raw_student_data in raw_data_list:
            # We only need features for background data, not the target
            temp_data = raw_student_data.copy()
            temp_data.pop("target_mark", None)  # Remove target if present
            processed_features_df = self.preprocessor.preprocess_student_data(temp_data)
            processed_data_frames.append(processed_features_df)

        if not processed_data_frames:
            logger.warning("No background data found after preprocessing.")
            return pd.DataFrame()

        combined_df = pd.concat(processed_data_frames, ignore_index=True)
        # Select only numerical features, as SHAP expects numerical input
        combined_df = combined_df.select_dtypes(include=["number"])
        logger.info(
            f"Loaded and preprocessed {len(combined_df)} rows for SHAP background data."
        )
        return combined_df

    def _initialize_explainer(self):
        """
        Initializes the SHAP explainer based on the loaded model and background data.
        """
        if self.model and not self.background_data.empty:
            logger.info("Initializing SHAP explainer.")
            try:
                # For tree-based models, shap.TreeExplainer is efficient
                if (
                    "Forest" in type(self.model).__name__
                    or "Boosting" in type(self.model).__name__
                ):
                    self.explainer = shap.TreeExplainer(
                        self.model, self.background_data
                    )
                else:
                    # For other models, KernelExplainer is more general but slower
                    self.explainer = shap.KernelExplainer(
                        self.model.predict, self.background_data
                    )
                logger.info("SHAP explainer initialized successfully.")
            except Exception as e:
                logger.error(f"Error initializing SHAP explainer: {e}", exc_info=True)
                self.explainer = None
        else:
            logger.warning(
                "Cannot initialize SHAP explainer: model or background data is missing."
            )

    def explain_prediction(self, student_id: str) -> Optional[Dict[str, float]]:
        """
        Generates SHAP explanations for a specific student's predicted mark.
        Returns a dictionary of feature importance (SHAP values).
        """
        if self.explainer is None:
            logger.error("SHAP explainer not initialized. Cannot explain prediction.")
            return None

        # Fetch raw student data (similar to PredictionService)
        # This would use db_manager.execute_query to get the student's current state
        # For demonstration, we'll simulate.
        # from prediction_service import PredictionService # To reuse data fetching logic
        # pred_service = PredictionService()
        # raw_student_data = pred_service.get_student_raw_data(student_id)

        # Simulate raw student data for demonstration
        if student_id == "S001":
            raw_student_data = {
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
                    {"subject": "Math", "mark": 75}
                ],  # Only relevant for preprocessing features
                "attendance_records": [{"date": "2025-05-05", "status": "Present"}],
            }
        else:
            logger.warning(
                f"No raw data found for student_id: {student_id} for explanation."
            )
            return None

        # Preprocess the raw data into features for explanation
        features_df = self.preprocessor.preprocess_student_data(raw_student_data)

        if features_df.empty:
            logger.error(
                f"No features generated for student {student_id} for explanation. Cannot explain."
            )
            return None

        # Ensure feature columns match the background data's columns and order
        # This is critical for SHAP. Missing columns should be added with 0 or mean.
        # Extra columns should be dropped.
        if not self.background_data.empty:
            missing_cols = set(self.background_data.columns) - set(features_df.columns)
            for c in missing_cols:
                features_df[c] = 0  # Or use mean of background data[c]
            features_df = features_df[self.background_data.columns]  # Ensure same order

        try:
            # Calculate SHAP values for the instance
            shap_values = self.explainer.shap_values(features_df)

            # If the model outputs a single value (regression), shap_values will be an array.
            # If it outputs multiple values (e.g., multi-output), it might be a list of arrays.
            # For regression, we expect a single array of SHAP values.
            if isinstance(
                shap_values, list
            ):  # For multi-output models, take the first output
                shap_values = shap_values[0]

            # Map SHAP values to feature names
            feature_importance = {}
            for i, feature_name in enumerate(features_df.columns):
                feature_importance[feature_name] = float(
                    shap_values[0][i]
                )  # [0] because it's a single instance

            logger.info(f"SHAP explanation generated for student {student_id}.")
            return feature_importance

        except Exception as e:
            logger.error(
                f"Error generating SHAP explanation for student {student_id}: {e}",
                exc_info=True,
            )
            return None

    def plot_explanation(
        self, shap_values_dict: Dict[str, float], plot_type: str = "waterfall"
    ):
        """
        (Conceptual) Generates a SHAP plot.
        Note: SHAP plotting typically requires a matplotlib backend, which might not
        be suitable for direct web serving. You'd usually save the plot to a file
        or convert it to a web-friendly format.
        """
        if not shap_values_dict:
            logger.warning("No SHAP values provided for plotting.")
            return

        logger.info(f"Generating SHAP {plot_type} plot (conceptual).")
        # For actual plotting, you would need to reconstruct the shap.Explanation object
        # or use shap.plots directly with the values.
        # Example:
        # if self.model and not self.background_data.empty:
        #     # Reconstruct a single explanation object for plotting
        #     # This is tricky without the original instance and base value.
        #     # A simpler way is to just use shap.plots.bar for feature importance from dict.
        #     features = pd.DataFrame([list(shap_values_dict.keys())], columns=list(shap_values_dict.keys()))
        #     values = np.array([list(shap_values_dict.values())])
        #
        #     # This is a simplified example, for a full waterfall plot you need base value
        #     # and the original instance.
        #     # shap.plots.waterfall(shap.Explanation(values=values[0], base_values=self.explainer.expected_value, data=features.iloc[0]))
        #     # Or for a simple bar plot of feature importance
        #     shap.plots.bar(shap.Explanation(values=values[0], base_values=0, data=features.iloc[0]), show=False)
        #     plt.tight_layout()
        #     plt.savefig("shap_explanation.png")
        #     plt.close()
        #     logger.info("SHAP plot saved to shap_explanation.png")
        # else:
        #     logger.warning("Cannot plot SHAP explanation: model or background data missing.")

        print("\n--- SHAP Feature Importance ---")
        sorted_features = sorted(
            shap_values_dict.items(), key=lambda item: abs(item[1]), reverse=True
        )
        for feature, value in sorted_features:
            print(f"{feature}: {value:.4f}")
        print("-------------------------------")


# Example Usage:
if __name__ == "__main__":
    # Ensure db_manager is connected for this test
    try:
        db_manager.connect()
        # Ensure dummy lookup tables are created and a dummy model is saved
        # for DataPreprocessor and ModelInterpretabilityService to function.
        # You can run `model_training.py`'s __main__ block first to generate a model.

        # Create a dummy model file for testing if it doesn't exist
        if not os.path.exists("models/randomforestregressor_model.joblib"):
            logger.warning("No model found. Creating a dummy model for testing.")
            from sklearn.ensemble import RandomForestRegressor
            import numpy as np

            dummy_X = pd.DataFrame(
                np.random.rand(10, 5), columns=[f"feature{i}" for i in range(5)]
            )
            dummy_y = pd.Series(np.random.randint(50, 90, 10))
            dummy_model = RandomForestRegressor(n_estimators=10, random_state=42)
            dummy_model.fit(dummy_X, dummy_y)
            os.makedirs("models", exist_ok=True)
            joblib.dump(dummy_model, "models/randomforestregressor_model.joblib")
            logger.info("Dummy model created.")

        # Ensure dummy lookup tables for preprocessor are created (as in data_preprocessing.py __main__)
        # This is crucial for the preprocessor to work correctly when loading background data.

        interpret_service = ModelInterpretabilityService()

        test_student_id = "S001"
        feature_importance = interpret_service.explain_prediction(test_student_id)

        if feature_importance:
            print(f"\nSHAP Feature Importance for {test_student_id}:")
            interpret_service.plot_explanation(feature_importance)
        else:
            print(f"\nFailed to get SHAP explanation for {test_student_id}.")

    except Exception as e:
        logger.error(f"An error occurred during model_interpretability test: {e}")
    finally:
        db_manager.close()
