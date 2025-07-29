# hyperparameter_optimization.py

import optuna
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.metrics import mean_squared_error
from typing import Dict, Any, Tuple
from utils import logger
from database_utils import db_manager  # For loading data
from data_preprocessing import DataPreprocessor  # For preprocessing data
import joblib  # For saving/loading optimized models


class HyperparameterOptimizer:
    """
    Automates and optimizes the hyperparameter tuning process for
    predictive models using Optuna.
    """

    def __init__(self):
        self.preprocessor = DataPreprocessor()
        self.data = self._load_and_preprocess_data()
        if not self.data.empty and "target_mark" in self.data.columns:
            self.X = self.data.drop(columns=["target_mark"]).select_dtypes(
                include=["number"]
            )
            self.y = self.data["target_mark"]
            self.X_train, self.X_val, self.y_train, self.y_val = train_test_split(
                self.X, self.y, test_size=0.2, random_state=42
            )
        else:
            self.X = pd.DataFrame()
            self.y = pd.Series()
            self.X_train, self.X_val, self.y_train, self.y_val = (
                pd.DataFrame(),
                pd.DataFrame(),
                pd.Series(),
                pd.Series(),
            )
            logger.error(
                "Failed to load or preprocess data for hyperparameter optimization."
            )

        self.models_to_optimize = {
            "RandomForestRegressor": RandomForestRegressor,
            "GradientBoostingRegressor": GradientBoostingRegressor,
            "SupportVectorRegressor": SVR,
            "KNeighborsRegressor": KNeighborsRegressor,
            "RidgeRegression": Ridge,
            "LassoRegression": Lasso,
            "ElasticNetRegression": ElasticNet,
        }  #

    def _load_and_preprocess_data(self) -> pd.DataFrame:
        """
        Loads raw training data and preprocesses it for optimization.
        This is similar to ModelTrainer's data loading but specifically for optimization.
        """
        logger.info("Loading raw training data for hyperparameter optimization.")
        # Simulating dummy raw data for demonstration
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
            target_mark = raw_student_data.pop("target_mark", None)
            processed_features_df = self.preprocessor.preprocess_student_data(
                raw_student_data
            )
            if target_mark is not None:
                processed_features_df["target_mark"] = target_mark
            processed_data_frames.append(processed_features_df)

        if not processed_data_frames:
            logger.warning(
                "No data found for hyperparameter optimization after preprocessing."
            )
            return pd.DataFrame()

        combined_df = pd.concat(processed_data_frames, ignore_index=True)
        logger.info(
            f"Loaded and preprocessed {len(combined_df)} rows for optimization."
        )
        return combined_df

    def _objective_rf(self, trial: optuna.Trial) -> float:
        """Objective function for RandomForestRegressor optimization."""
        n_estimators = trial.suggest_int("n_estimators", 50, 200)
        max_depth = trial.suggest_int("max_depth", 5, 20)
        min_samples_split = trial.suggest_int("min_samples_split", 2, 10)
        min_samples_leaf = trial.suggest_int("min_samples_leaf", 1, 5)

        model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            random_state=42,
        )
        model.fit(self.X_train, self.y_train)
        y_pred = model.predict(self.X_val)
        mse = mean_squared_error(self.y_val, y_pred)
        return mse

    def _objective_gb(self, trial: optuna.Trial) -> float:
        """Objective function for GradientBoostingRegressor optimization."""
        n_estimators = trial.suggest_int("n_estimators", 50, 200)
        learning_rate = trial.suggest_loguniform("learning_rate", 1e-3, 0.1)
        max_depth = trial.suggest_int("max_depth", 3, 10)
        subsample = trial.suggest_loguniform("subsample", 0.6, 1.0)

        model = GradientBoostingRegressor(
            n_estimators=n_estimators,
            learning_rate=learning_rate,
            max_depth=max_depth,
            subsample=subsample,
            random_state=42,
        )
        model.fit(self.X_train, self.y_train)
        y_pred = model.predict(self.X_val)
        mse = mean_squared_error(self.y_val, y_pred)
        return mse

    def _objective_svr(self, trial: optuna.Trial) -> float:
        """Objective function for SVR optimization."""
        C = trial.suggest_loguniform("C", 1e-2, 1e2)
        epsilon = trial.suggest_loguniform("epsilon", 1e-3, 1e-1)
        kernel = trial.suggest_categorical("kernel", ["rbf", "linear", "poly"])

        model = SVR(C=C, epsilon=epsilon, kernel=kernel)
        model.fit(self.X_train, self.y_train)
        y_pred = model.predict(self.X_val)
        mse = mean_squared_error(self.y_val, y_pred)
        return mse

    def _objective_knn(self, trial: optuna.Trial) -> float:
        """Objective function for KNeighborsRegressor optimization."""
        n_neighbors = trial.suggest_int("n_neighbors", 3, 15)
        weights = trial.suggest_categorical("weights", ["uniform", "distance"])
        algorithm = trial.suggest_categorical(
            "algorithm", ["auto", "ball_tree", "kd_tree", "brute"]
        )

        model = KNeighborsRegressor(
            n_neighbors=n_neighbors, weights=weights, algorithm=algorithm
        )
        model.fit(self.X_train, self.y_train)
        y_pred = model.predict(self.X_val)
        mse = mean_squared_error(self.y_val, y_pred)
        return mse

    def _objective_ridge(self, trial: optuna.Trial) -> float:
        """Objective function for Ridge Regression optimization."""
        alpha = trial.suggest_loguniform("alpha", 1e-3, 1e2)
        model = Ridge(alpha=alpha)
        model.fit(self.X_train, self.y_train)
        y_pred = model.predict(self.X_val)
        mse = mean_squared_error(self.y_val, y_pred)
        return mse

    def _objective_lasso(self, trial: optuna.Trial) -> float:
        """Objective function for Lasso Regression optimization."""
        alpha = trial.suggest_loguniform("alpha", 1e-3, 1e2)
        model = Lasso(alpha=alpha)
        model.fit(self.X_train, self.y_train)
        y_pred = model.predict(self.X_val)
        mse = mean_squared_error(self.y_val, y_pred)
        return mse

    def _objective_elasticnet(self, trial: optuna.Trial) -> float:
        """Objective function for ElasticNet Regression optimization."""
        alpha = trial.suggest_loguniform("alpha", 1e-3, 1e2)
        l1_ratio = trial.suggest_uniform("l1_ratio", 0.0, 1.0)  # 0 for L2, 1 for L1
        model = ElasticNet(alpha=alpha, l1_ratio=l1_ratio)
        model.fit(self.X_train, self.y_train)
        y_pred = model.predict(self.X_val)
        mse = mean_squared_error(self.y_val, y_pred)
        return mse

    def optimize_model(self, model_name: str, n_trials: int = 50) -> Dict[str, Any]:
        """
        Runs hyperparameter optimization for a specified model.
        Returns the best hyperparameters found.
        """
        if self.X.empty or self.y.empty:
            logger.error("No data available for optimization. Exiting.")
            return {}

        objective_map = {
            "RandomForestRegressor": self._objective_rf,
            "GradientBoostingRegressor": self._objective_gb,
            "SupportVectorRegressor": self._objective_svr,
            "KNeighborsRegressor": self._objective_knn,
            "RidgeRegression": self._objective_ridge,
            "LassoRegression": self._objective_lasso,
            "ElasticNetRegression": self._objective_elasticnet,
        }  #

        if model_name not in objective_map:
            logger.error(f"Optimization objective not defined for model: {model_name}")
            return {}

        logger.info(
            f"Starting hyperparameter optimization for {model_name} with {n_trials} trials."
        )
        study = optuna.create_study(direction="minimize")  # Minimize MSE
        study.optimize(objective_map[model_name], n_trials=n_trials)

        logger.info(f"Optimization finished for {model_name}.")
        logger.info(f"Best trial for {model_name}:")
        logger.info(f"  Value: {study.best_value:.4f} (MSE)")
        logger.info(f"  Params: {study.best_params}")

        # Save the best model with optimized hyperparameters
        best_model_class = self.models_to_optimize[model_name]
        optimized_model = best_model_class(**study.best_params)

        # Train on full training data (X_train, y_train) for the final model to be saved
        optimized_model.fit(self.X_train, self.y_train)

        # Save the optimized model
        joblib.dump(
            optimized_model,
            f"models/optimized_{model_name.lower().replace(' ', '_')}_model.joblib",
        )
        logger.info(f"Optimized {model_name} saved.")

        return study.best_params


# Example Usage:
if __name__ == "__main__":
    # Ensure db_manager is connected for this test
    try:
        db_manager.connect()
        # Ensure dummy lookup tables are created for DataPreprocessor if running this directly
        # (as done in data_preprocessing.py __main__ block)

        optimizer = HyperparameterOptimizer()

        if not optimizer.X.empty and not optimizer.y.empty:
            # Optimize RandomForestRegressor
            logger.info("\n--- Optimizing RandomForestRegressor ---")
            best_params_rf = optimizer.optimize_model(
                "RandomForestRegressor", n_trials=10
            )  # Reduced trials for quick test
            print(f"\nBest Hyperparameters for RandomForestRegressor: {best_params_rf}")

            # Optimize GradientBoostingRegressor
            logger.info("\n--- Optimizing GradientBoostingRegressor ---")
            best_params_gb = optimizer.optimize_model(
                "GradientBoostingRegressor", n_trials=10
            )  # Reduced trials for quick test
            print(
                f"\nBest Hyperparameters for GradientBoostingRegressor: {best_params_gb}"
            )
        else:
            logger.error("Skipping optimization tests due to missing data.")

    except Exception as e:
        logger.error(f"An error occurred during hyperparameter_optimization test: {e}")
    finally:
        db_manager.close()
