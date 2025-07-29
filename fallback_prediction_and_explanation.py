import os
import joblib
import pandas as pd
from typing import Optional, Tuple, Dict, Any
import logging
import sys

# --- Inlined utils 2.py ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(ch)


def log_error(message: str, exception: Exception = None):
    if exception:
        logger.error(f"{message}: {exception}", exc_info=True)
    else:
        logger.error(message)


def log_info(message: str):
    logger.info(message)


def log_debug(message: str):
    logger.debug(message)


# --- Inlined DataPreprocessor from data_preprocessing 2.py ---
class DataPreprocessor:
    def preprocess_student_data(self, raw_data: Dict[str, Any]) -> pd.DataFrame:
        log_info(
            f"Starting preprocessing for student: {raw_data.get('student_id', 'N/A')}"
        )
        df = pd.DataFrame([raw_data])
        df["gender_encoded"] = df["gender"].map({"Male": 0, "Female": 1}).fillna(-1)
        df["attendance_percentage"] = (
            100.0 if raw_data.get("attendance_records") else 0.0
        )
        return df[["gender_encoded", "attendance_percentage"]]


# --- Patched PredictionService ---
class PredictionService:
    def __init__(
        self,
        model_path: str = "models",
        default_model_name: str = "randomforestregressor",
    ):
        self.model_path = model_path
        self.default_model_name = default_model_name
        self.model = self._load_best_model()
        self.preprocessor = DataPreprocessor()

    def _load_best_model(self) -> Optional[Any]:
        optimized_model_filename = f"optimized_{self.default_model_name}_model.joblib"
        model_filepath = os.path.join(self.model_path, optimized_model_filename)

        if not os.path.exists(model_filepath):
            log_info(
                f"Optimized model '{optimized_model_filename}' not found. Attempting to load default model."
            )
            model_filepath = os.path.join(
                self.model_path, f"{self.default_model_name}_model.joblib"
            )

        if not os.path.exists(model_filepath):
            log_info(
                f"No prediction model found at {model_filepath}. Using fallback prediction."
            )
            return None

        try:
            model = joblib.load(model_filepath)
            log_info(f"Successfully loaded prediction model from {model_filepath}")
            return model
        except Exception as e:
            log_error("Error loading prediction model", e)
            return None

    def predict_performance(
        self, student_id: str
    ) -> Tuple[Optional[float], Optional[float]]:
        raw_data = self._get_dummy_student_data(student_id)
        if not raw_data:
            log_info(f"No raw data available for student_id: {student_id}")
            return None, None

        features_df = self.preprocessor.preprocess_student_data(raw_data)
        if features_df.empty:
            log_info(f"No features generated for student {student_id}.")
            return None, None

        if self.model:
            try:
                predicted_mark = self.model.predict(features_df)[0]
                confidence = max(0.0, min(1.0, 1.0 - abs(predicted_mark - 75) / 100.0))
                log_info(
                    f"Predicted mark for student {student_id}: {predicted_mark:.2f}, Confidence: {confidence:.2f}"
                )
                return float(predicted_mark), float(confidence)
            except Exception as e:
                log_error("Error during prediction", e)
                return None, None
        else:
            log_info(f"Using fallback prediction for student {student_id}.")
            return 75.0, 0.5

    def _get_dummy_student_data(self, student_id: str) -> Optional[Dict[str, Any]]:
        if student_id == "S001":
            return {
                "student_id": "S001",
                "gender": "Female",
                "age": 15,
                "grade_level": 9,
                "attendance_records": [{"date": "2025-05-05", "status": "Present"}],
            }
        return None


# --- Patched ModelInterpretabilityService ---
class ModelInterpretabilityService:
    def __init__(
        self,
        model_path: str = "models",
        default_model_name: str = "randomforestregressor",
    ):
        self.model_path = model_path
        self.default_model_name = default_model_name
        self.model = self._load_model()
        self.preprocessor = DataPreprocessor()

    def _load_model(self) -> Optional[Any]:
        optimized_model_filename = f"optimized_{self.default_model_name}_model.joblib"
        model_filepath = os.path.join(self.model_path, optimized_model_filename)

        if not os.path.exists(model_filepath):
            log_info(
                f"Optimized model '{optimized_model_filename}' not found. Attempting to load default model."
            )
            model_filepath = os.path.join(
                self.model_path, f"{self.default_model_name}_model.joblib"
            )

        if not os.path.exists(model_filepath):
            log_info(
                f"No interpretability model found at {model_filepath}. Using fallback explanation."
            )
            return None

        try:
            model = joblib.load(model_filepath)
            log_info(
                f"Successfully loaded interpretability model from {model_filepath}"
            )
            return model
        except Exception as e:
            log_error("Error loading interpretability model", e)
            return None

    def explain_prediction(self, student_id: str) -> Dict[str, float]:
        raw_data = self._get_dummy_student_data(student_id)
        if not raw_data:
            log_info(f"No raw data available for student_id: {student_id}")
            return {}

        features_df = self.preprocessor.preprocess_student_data(raw_data)
        if features_df.empty:
            log_info(f"No features generated for student {student_id}.")
            return {}

        if self.model:
            try:
                explanation = {
                    col: round(abs(val), 2)
                    for col, val in zip(features_df.columns, features_df.iloc[0])
                }
                log_info(f"Generated explanation for student {student_id}")
                return explanation
            except Exception as e:
                log_error("Error during explanation", e)
                return {}
        else:
            log_info(f"Using fallback explanation for student {student_id}.")
            return {col: 0.1 for col in features_df.columns}

    def _get_dummy_student_data(self, student_id: str) -> Optional[Dict[str, Any]]:
        if student_id == "S001":
            return {
                "student_id": "S001",
                "gender": "Female",
                "age": 15,
                "grade_level": 9,
                "attendance_records": [{"date": "2025-05-05", "status": "Present"}],
            }
        return None


# --- Example usage ---
if __name__ == "__main__":
    prediction_service = PredictionService()
    interpretability_service = ModelInterpretabilityService()

    student_id = "S001"
    predicted_mark, confidence = prediction_service.predict_performance(student_id)
    explanation = interpretability_service.explain_prediction(student_id)

    print(
        f"\nPrediction for {student_id}: Mark={predicted_mark}, Confidence={confidence}"
    )
    print(f"\nExplanation for {student_id}:")
    for feature, importance in explanation.items():
        print(f"  {feature}: {importance}")
