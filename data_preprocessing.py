# data_preprocessing.py

import pandas as pd
from typing import Dict, Any, List
from utils import logger
from database_utils import db_manager  # Import the global db_manager


class DataPreprocessor:
    """
    Handles data cleaning, transformation, and feature engineering.
    All dynamic content, including dropdowns, labels, and configurations,
    will be fetched from backend services, ensuring a table-driven approach.
    """

    def __init__(self):
        # The db_manager is initialized globally, so we just use it directly
        self.lookup_data = (
            self._load_all_lookup_data()
        )  # All lookup data is table-driven

    def _load_all_lookup_data(self) -> Dict[str, pd.DataFrame]:
        """
        Loads all necessary lookup tables from the database using db_manager.
        This ensures all dynamic content and configurations are table-driven.
        """
        logger.info("Loading all lookup tables for data preprocessing...")
        lookup_tables = [
            "academic_assessment_type_lookup",
            "access_to_healthcare_lookup",
            "access_to_specialized_programs_lookup",
            "allocation_category_lookup",
            "attendance_status_lookup",
            "device_access_lookup",
            "digital_literacy_lookup",
            "digital_literacy_support_lookup",
            "disability_status_lookup",
            "disciplinary_incidents_lookup",
            "dropout_reason_lookup",
            "engagement_level_lookup",
            "extracurricular_activity_type_lookup",
            "extracurricular_role_lookup",
            "funding_model_lookup",
            "gender_lookup",
            "geographic_density_classification_lookup",
            "health_conditions_lookup",
            "highest_qualification_lookup",
            "home_learning_environment_lookup",
            "internet_access_lookup",
            "internet_access_quality_lookup",
            "intervention_outcome_lookup",
            "intervention_type_lookup",
            "language_lookup",
            "learning_resources_lookup",
            "local_municipality_lookup",
            "mental_health_support_lookup",
            "nutrition_status_lookup",
            "parental_education_level_lookup",
            "parental_employment_status_lookup",
            "parental_marital_status_lookup",
            "parental_tech_support_lookup",
            "psychological_assessment_type_lookup",
            "race_lookup",
            "school_infrastructure_lookup",
            "school_phase_lookup",
            "school_prototype_size_lookup",
            "school_safety_perception_lookup",
            "school_specialization_lookup",
            "school_status_lookup",
            "school_type_lookup",
            "social_grants_lookup",
            "socioeconomic_classification_lookup",
            "software_platform_access_lookup",
            "study_environment_lookup",
            "study_habits_lookup",
            "teacher_effectiveness_rating_lookup",
            "teacher_student_ratio_lookup",
            "urban_rural_classification_lookup",
            "Holidays",  # Assuming this is the table for public/school holidays
        ]

        data = {}
        for table_name in lookup_tables:
            df = db_manager.get_lookup_data(table_name)
            if not df.empty:
                data[table_name] = df
                logger.debug(f"Loaded {len(df)} rows from {table_name}")
            else:
                logger.warning(
                    f"Could not load data from lookup table: {table_name}. It might be empty or not exist."
                )
                data[table_name] = (
                    pd.DataFrame()
                )  # Ensure an empty DataFrame is present
        logger.info("Lookup tables loading complete.")
        return data

    def calculate_attendance_percentage(
        self, attendance_records: pd.DataFrame
    ) -> float:
        """
        Calculates student attendance percentage, explicitly excluding
        Saturdays, Sundays, public holidays, and school holidays.
        """
        if attendance_records.empty:
            return 0.0

        attendance_records["date"] = pd.to_datetime(attendance_records["date"])

        # Get public and school holidays from loaded lookup data
        # Assuming 'Holidays' table contains both public and school holidays
        holidays_df = self.lookup_data.get("Holidays", pd.DataFrame())

        public_holidays = []
        school_holidays = []

        if (
            not holidays_df.empty
            and "FromDate" in holidays_df.columns
            and "ToDate" in holidays_df.columns
        ):
            for _, row in holidays_df.iterrows():
                start_date = pd.to_datetime(row["FromDate"])
                end_date = pd.to_datetime(row["ToDate"])
                current_date = start_date
                while current_date <= end_date:
                    if row.get("Type") == "Public Holiday":
                        public_holidays.append(current_date)
                    elif row.get("Type") == "School Holiday":
                        school_holidays.append(current_date)
                    current_date += pd.Timedelta(days=1)

        # Filter out weekends
        non_weekend_days = attendance_records[
            attendance_records["date"].dt.dayofweek < 5
        ]  # Monday=0, Sunday=6

        # Filter out public and school holidays
        filtered_days = non_weekend_days[
            ~non_weekend_days["date"].isin(public_holidays)
            & ~non_weekend_days["date"].isin(school_holidays)
        ]

        total_school_days = filtered_days["date"].nunique()
        present_days = filtered_days[filtered_days["status"] == "Present"][
            "date"
        ].nunique()  # Assuming 'status' column

        if total_school_days == 0:
            return 0.0
        return (present_days / total_school_days) * 100

    def preprocess_student_data(self, raw_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Performs comprehensive data preprocessing and feature engineering
        for student data. All features are derived dynamically from the
        database schema and lookup tables.
        """
        logger.info(
            f"Starting preprocessing for student: {raw_data.get('student_id', 'N/A')}"
        )
        df = pd.DataFrame(
            [raw_data]
        )  # Convert single student data dict to DataFrame for consistency

        # Example transformations and feature engineering:
        # 1. Handle missing values (e.g., imputation or dropping)
        # 2. Encode categorical features using one-hot encoding or label encoding
        #    (mapping against loaded lookup data)
        # 3. Create new features (e.g., student-teacher ratio, infrastructure score from school data)

        # Example: Encoding 'gender' using the lookup table
        if (
            "gender" in df.columns
            and "gender_lookup" in self.lookup_data
            and not self.lookup_data["gender_lookup"].empty
        ):
            gender_map = (
                self.lookup_data["gender_lookup"]
                .set_index("gender_name")["gender_id"]
                .to_dict()
            )
            df["gender_encoded"] = (
                df["gender"].map(gender_map).fillna(-1)
            )  # Use -1 for unknown
        else:
            df["gender_encoded"] = -1  # Default if lookup data is missing

        # Example: Calculating attendance (requires attendance_records in raw_data)
        if "attendance_records" in raw_data and raw_data["attendance_records"]:
            attendance_df = pd.DataFrame(raw_data["attendance_records"])
            df["attendance_percentage"] = self.calculate_attendance_percentage(
                attendance_df
            )
        else:
            df["attendance_percentage"] = 0.0

        # Integrate contextual data from various lookup tables
        contextual_features = [
            "home_learning_environment",
            "internet_access",
            "study_habits",
            "disability_status",
            "socioeconomic_classification",
            "parental_education_level",
            "race",
            "access_to_healthcare",
            "access_to_specialized_programs",
            "allocation_category",
            "device_access",
            "digital_literacy",
            "digital_literacy_support",
            "disciplinary_incidents",
            "dropout_reason",
            "engagement_level",
            "extracurricular_activity_type",
            "extracurricular_role",
            "funding_model",
            "geographic_density_classification",
            "health_conditions",
            "highest_qualification",
            "internet_access_quality",
            "intervention_outcome",
            "intervention_type",
            "language",
            "learning_resources",
            "local_municipality",
            "mental_health_support",
            "nutrition_status",
            "parental_employment_status",
            "parental_marital_status",
            "parental_tech_support",
            "psychological_assessment_type",
            "school_infrastructure",
            "school_phase",
            "school_prototype_size",
            "school_safety_perception",
            "school_specialization",
            "school_status",
            "school_type",
            "social_grants",
            "software_platform_access",
            "study_environment",
            "teacher_effectiveness_rating",
            "teacher_student_ratio",
            "urban_rural_classification",
        ]

        for context_feature_key in contextual_features:
            # Determine lookup table name based on convention
            lookup_table_name = f"{context_feature_key}_lookup"
            # Handle specific cases where table name might differ from simple suffix
            if context_feature_key == "race":
                lookup_table_name = "race_lookup"
            elif context_feature_key == "extracurricular_activity_type":
                lookup_table_name = "extracurricular_activity_type_lookup"
            elif context_feature_key == "extracurricular_role":
                lookup_table_name = "extracurricular_role_lookup"
            elif context_feature_key == "academic_assessment_type":
                lookup_table_name = "academic_assessment_type_lookup"
            elif context_feature_key == "psychological_assessment_type":
                lookup_table_name = "psychological_assessment_type_lookup"

            if (
                context_feature_key in df.columns
                and lookup_table_name in self.lookup_data
                and not self.lookup_data[lookup_table_name].empty
            ):
                # Dynamically determine ID and Name column names based on SQL schema convention
                id_col = f"{context_feature_key}_id"
                name_col = f"{context_feature_key}_name"

                # Override for specific cases where ID/Name column naming convention differs
                if lookup_table_name == "race_lookup":
                    id_col = "race_id"
                    name_col = "race_name"
                elif lookup_table_name == "extracurricular_activity_type_lookup":
                    id_col = "activity_type_id"
                    name_col = "activity_type_name"
                elif lookup_table_name == "extracurricular_role_lookup":
                    id_col = "role_id"
                    name_col = "role_name"
                elif lookup_table_name == "academic_assessment_type_lookup":
                    id_col = "assessment_type_id"
                    name_col = "assessment_type_name"
                elif lookup_table_name == "psychological_assessment_type_lookup":
                    id_col = "assessment_type_id"
                    name_col = "assessment_type_name"
                elif lookup_table_name == "teacher_student_ratio_lookup":
                    id_col = "teacher_student_ratio_id"
                    name_col = "teacher_student_ratio_name"
                elif lookup_table_name == "disciplinary_incidents_lookup":
                    id_col = "disciplinary_incidents_id"
                    name_col = "disciplinary_incidents_name"
                elif lookup_table_name == "mental_health_support_lookup":
                    id_col = "mental_health_support_id"
                    name_col = "mental_health_support_name"
                elif lookup_table_name == "local_municipality_lookup":
                    id_col = "local_municipality_id"
                    name_col = "local_municipality_name"
                elif lookup_table_name == "learning_resources_lookup":
                    id_col = "learning_resources_id"
                    name_col = "learning_resources_name"
                elif lookup_table_name == "highest_qualification_lookup":
                    id_col = "highest_qualification_id"
                    name_col = "highest_qualification_name"
                elif lookup_table_name == "health_conditions_lookup":
                    id_col = "health_conditions_id"
                    name_col = "health_conditions_name"
                elif lookup_table_name == "geographic_density_classification_lookup":
                    id_col = "geographic_density_classification_id"
                    name_col = "geographic_density_classification_name"
                elif lookup_table_name == "funding_model_lookup":
                    id_col = "funding_model_id"
                    name_col = "funding_model_name"
                elif lookup_table_name == "dropout_reason_lookup":
                    id_col = "dropout_reason_id"
                    name_col = "dropout_reason_name"
                elif lookup_table_name == "digital_literacy_support_lookup":
                    id_col = "digital_literacy_support_id"
                    name_col = "digital_literacy_support_name"
                elif lookup_table_name == "digital_literacy_lookup":
                    id_col = "digital_literacy_id"
                    name_col = "digital_literacy_name"
                elif lookup_table_name == "device_access_lookup":
                    id_col = "device_access_id"
                    name_col = "device_access_name"
                elif lookup_table_name == "allocation_category_lookup":
                    id_col = "allocation_category_id"
                    name_col = "allocation_category_name"
                elif lookup_table_name == "access_to_specialized_programs_lookup":
                    id_col = "access_to_specialized_programs_id"
                    name_col = "access_to_specialized_programs_name"
                elif lookup_table_name == "access_to_healthcare_lookup":
                    id_col = "access_to_healthcare_id"
                    name_col = "access_to_healthcare_name"
                elif lookup_table_name == "intervention_outcome_lookup":
                    id_col = "intervention_outcome_id"
                    name_col = "intervention_outcome_name"
                elif lookup_table_name == "intervention_type_lookup":
                    id_col = "intervention_type_id"
                    name_col = "intervention_type_name"
                elif lookup_table_name == "language_lookup":
                    id_col = "language_id"
                    name_col = "language_name"
                elif lookup_table_name == "nutrition_status_lookup":
                    id_col = "nutrition_status_id"
                    name_col = "nutrition_status_name"
                elif lookup_table_name == "parental_employment_status_lookup":
                    id_col = "parental_employment_status_id"
                    name_col = "parental_employment_status_name"
                elif lookup_table_name == "parental_marital_status_lookup":
                    id_col = "parental_marital_status_id"
                    name_col = "parental_marital_status_name"
                elif lookup_table_name == "parental_tech_support_lookup":
                    id_col = "parental_tech_support_id"
                    name_col = "parental_tech_support_name"
                elif lookup_table_name == "school_infrastructure_lookup":
                    id_col = "school_infrastructure_id"
                    name_col = "school_infrastructure_name"
                elif lookup_table_name == "school_phase_lookup":
                    id_col = "school_phase_id"
                    name_col = "school_phase_name"
                elif lookup_table_name == "school_prototype_size_lookup":
                    id_col = "school_prototype_size_id"
                    name_col = "school_prototype_size_name"
                elif lookup_table_name == "school_safety_perception_lookup":
                    id_col = "school_safety_perception_id"
                    name_col = "school_safety_perception_name"
                elif lookup_table_name == "school_specialization_lookup":
                    id_col = "school_specialization_id"
                    name_col = "school_specialization_name"
                elif lookup_table_name == "school_status_lookup":
                    id_col = "school_status_id"
                    name_col = "school_status_name"
                elif lookup_table_name == "school_type_lookup":
                    id_col = "school_type_id"
                    name_col = "school_type_name"
                elif lookup_table_name == "social_grants_lookup":
                    id_col = "social_grants_id"
                    name_col = "social_grants_name"
                elif lookup_table_name == "software_platform_access_lookup":
                    id_col = "software_platform_access_id"
                    name_col = "software_platform_access_name"
                elif lookup_table_name == "study_environment_lookup":
                    id_col = "study_environment_id"
                    name_col = "study_environment_name"
                elif lookup_table_name == "teacher_effectiveness_rating_lookup":
                    id_col = "teacher_effectiveness_rating_id"
                    name_col = "teacher_effectiveness_rating_name"
                elif lookup_table_name == "urban_rural_classification_lookup":
                    id_col = "urban_rural_classification_id"
                    name_col = "urban_rural_classification_name"
                elif lookup_table_name == "engagement_level_lookup":
                    id_col = "engagement_level_id"
                    name_col = "engagement_level_name"
                # Special cases for non-lookup tables that might be encoded
                elif lookup_table_name == "provinces":
                    id_col = "provinceid"
                    name_col = "province_name"
                elif lookup_table_name == "districts":
                    id_col = "districtid"
                    name_col = "district_name"
                elif lookup_table_name == "subjects":
                    id_col = "subjectid"
                    name_col = "subject_name"
                elif lookup_table_name == "schools":
                    id_col = "schoolid"
                    name_col = "schoolname"
                elif lookup_table_name == "parents":
                    id_col = "parentid"
                    name_col = (
                        "firstname"  # Using firstname as an example, adjust as needed
                    )

                if (
                    id_col in self.lookup_data[lookup_table_name].columns
                    and name_col in self.lookup_data[lookup_table_name].columns
                ):
                    context_map = (
                        self.lookup_data[lookup_table_name]
                        .set_index(name_col)[id_col]
                        .to_dict()
                    )
                    df[f"{context_feature_key}_encoded"] = (
                        df[context_feature_key].map(context_map).fillna(-1)
                    )
                else:
                    logger.warning(
                        f"Lookup table '{lookup_table_name}' missing expected columns '{id_col}' or '{name_col}'. Skipping encoding."
                    )
                    df[f"{context_feature_key}_encoded"] = -1  # Default or placeholder
            else:
                df[f"{context_feature_key}_encoded"] = -1  # Default or placeholder

        # Select only numerical features for the model.
        # This is a simplification; in a real scenario, you'd ensure all relevant
        # features are correctly encoded and handled.
        numerical_features = df.select_dtypes(include=["number"]).columns.tolist()
        # Exclude original IDs or non-feature columns that might be numeric
        features_for_model = [
            col for col in numerical_features if col not in ["student_id", "mark"]
        ]

        logger.info(
            f"Student data preprocessing complete. Features generated: {features_for_model}"
        )
        return df[features_for_model]


# Example Usage (for testing purposes)
if __name__ == "__main__":
    # Ensure db_manager is connected for this test
    try:
        db_manager.connect()

        # --- Create Dummy Lookup Tables if they don't exist ---
        # These are for local testing only; in production, these tables should exist and be populated
        # by your database setup script (e.g., create_studentmarks_tables.sql).
        # Simplified to only include tables directly used in sample_student_data for encoding.

        # gender_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'gender_lookup')
            CREATE TABLE gender_lookup (gender_id INT IDENTITY(1,1) PRIMARY KEY, gender_name NVARCHAR(50));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM gender_lookup WHERE gender_name = 'Male') INSERT INTO gender_lookup (gender_name) VALUES ('Male');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM gender_lookup WHERE gender_name = 'Female') INSERT INTO gender_lookup (gender_name) VALUES ('Female');"
        )

        # Holidays (for attendance calculation)
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Holidays')
            CREATE TABLE Holidays (date_id INT IDENTITY(1,1) PRIMARY KEY, FromDate DATE, ToDate DATE, Duration_Days INT, HolidayName NVARCHAR(255), Type NVARCHAR(50), Comments NVARCHAR(MAX));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM Holidays WHERE HolidayName = 'Youth Day') INSERT INTO Holidays (FromDate, ToDate, Duration_Days, HolidayName, Type, Comments) VALUES ('2025-06-16', '2025-06-16', 1, 'Youth Day', 'Public Holiday', '');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM Holidays WHERE HolidayName = 'Workers Day') INSERT INTO Holidays (FromDate, ToDate, Duration_Days, HolidayName, Type, Comments) VALUES ('2025-05-01', '2025-05-01', 1, 'Workers Day', 'Public Holiday', '');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM Holidays WHERE HolidayName = 'Term 1 Break') INSERT INTO Holidays (FromDate, ToDate, Duration_Days, HolidayName, Type, Comments) VALUES ('2025-03-28', '2025-04-07', 11, 'Term 1 Break', 'School Holiday', 'Easter break');"
        )

        # home_learning_environment_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'home_learning_environment_lookup')
            CREATE TABLE home_learning_environment_lookup (home_learning_environment_id INT IDENTITY(1,1) PRIMARY KEY, home_learning_environment_name NVARCHAR(50));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM home_learning_environment_lookup WHERE home_learning_environment_name = 'Conducive') INSERT INTO home_learning_environment_lookup (home_learning_environment_name) VALUES ('Conducive');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM home_learning_environment_lookup WHERE home_learning_environment_name = 'Challenging') INSERT INTO home_learning_environment_lookup (home_learning_environment_name) VALUES ('Challenging');"
        )

        # internet_access_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'internet_access_lookup')
            CREATE TABLE internet_access_lookup (internet_access_id INT IDENTITY(1,1) PRIMARY KEY, internet_access_name NVARCHAR(50));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM internet_access_lookup WHERE internet_access_name = 'Broadband') INSERT INTO internet_access_lookup (internet_access_name) VALUES ('Broadband');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM internet_access_lookup WHERE internet_access_name = 'Limited') INSERT INTO internet_access_lookup (internet_access_name) VALUES ('Limited');"
        )

        # study_habits_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'study_habits_lookup')
            CREATE TABLE study_habits_lookup (study_habits_id INT IDENTITY(1,1) PRIMARY KEY, study_habits_name NVARCHAR(50));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM study_habits_lookup WHERE study_habits_name = 'Consistent') INSERT INTO study_habits_lookup (study_habits_name) VALUES ('Consistent');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM study_habits_lookup WHERE study_habits_name = 'Irregular') INSERT INTO study_habits_lookup (study_habits_name) VALUES ('Irregular');"
        )

        # race_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'race_lookup')
            CREATE TABLE race_lookup (race_id INT IDENTITY(1,1) PRIMARY KEY, race_name NVARCHAR(50));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM race_lookup WHERE race_name = 'Black African') INSERT INTO race_lookup (race_name) VALUES ('Black African');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM race_lookup WHERE race_name = 'Coloured') INSERT INTO race_lookup (race_name) VALUES ('Coloured');"
        )

        # disability_status_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'disability_status_lookup')
            CREATE TABLE disability_status_lookup (disability_status_id INT IDENTITY(1,1) PRIMARY KEY, disability_status_name NVARCHAR(50));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM disability_status_lookup WHERE disability_status_name = 'None') INSERT INTO disability_status_lookup (disability_status_name) VALUES ('None');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM disability_status_lookup WHERE disability_status_name = 'Physical') INSERT INTO disability_status_lookup (disability_status_name) VALUES ('Physical');"
        )

        # socioeconomic_classification_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'socioeconomic_classification_lookup')
            CREATE TABLE socioeconomic_classification_lookup (socioeconomic_classification_id INT IDENTITY(1,1) PRIMARY KEY, socioeconomic_classification_name NVARCHAR(50));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM socioeconomic_classification_lookup WHERE socioeconomic_classification_name = 'Low') INSERT INTO socioeconomic_classification_lookup (socioeconomic_classification_name) VALUES ('Low');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM socioeconomic_classification_lookup WHERE socioeconomic_classification_name = 'Middle') INSERT INTO socioeconomic_classification_lookup (socioeconomic_classification_name) VALUES ('Middle');"
        )

        # parental_education_level_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'parental_education_level_lookup')
            CREATE TABLE parental_education_level_lookup (parental_education_level_id INT IDENTITY(1,1) PRIMARY KEY, parental_education_level_name NVARCHAR(50));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM parental_education_level_lookup WHERE parental_education_level_name = 'Primary') INSERT INTO parental_education_level_lookup (parental_education_level_name) VALUES ('Primary');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM parental_education_level_lookup WHERE parental_education_level_name = 'Secondary') INSERT INTO parental_education_level_lookup (parental_education_level_name) VALUES ('Secondary');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM parental_education_level_lookup WHERE parental_education_level_name = 'Degree') INSERT INTO parental_education_level_lookup (parental_education_level_name) VALUES ('Degree');"
        )

        # access_to_healthcare_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'access_to_healthcare_lookup')
            CREATE TABLE access_to_healthcare_lookup (access_to_healthcare_id INT IDENTITY(1,1) PRIMARY KEY, access_to_healthcare_name NVARCHAR(50));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM access_to_healthcare_lookup WHERE access_to_healthcare_name = 'Good') INSERT INTO access_to_healthcare_lookup (access_to_healthcare_name) VALUES ('Good');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM access_to_healthcare_lookup WHERE access_to_healthcare_name = 'Limited') INSERT INTO access_to_healthcare_lookup (access_to_healthcare_name) VALUES ('Limited');"
        )

        # access_to_specialized_programs_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'access_to_specialized_programs_lookup')
            CREATE TABLE access_to_specialized_programs_lookup (access_to_specialized_programs_id INT IDENTITY(1,1) PRIMARY KEY, access_to_specialized_programs_name NVARCHAR(50));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM access_to_specialized_programs_lookup WHERE access_to_specialized_programs_name = 'Yes') INSERT INTO access_to_specialized_programs_lookup (access_to_specialized_programs_name) VALUES ('Yes');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM access_to_specialized_programs_lookup WHERE access_to_specialized_programs_name = 'No') INSERT INTO access_to_specialized_programs_lookup (access_to_specialized_programs_name) VALUES ('No');"
        )

        # allocation_category_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'allocation_category_lookup')
            CREATE TABLE allocation_category_lookup (allocation_category_id INT IDENTITY(1,1) PRIMARY KEY, allocation_category_name NVARCHAR(50));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM allocation_category_lookup WHERE allocation_category_name = 'Category A') INSERT INTO allocation_category_lookup (allocation_category_name) VALUES ('Category A');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM allocation_category_lookup WHERE allocation_category_name = 'Category B') INSERT INTO allocation_category_lookup (allocation_category_name) VALUES ('Category B');"
        )

        # device_access_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'device_access_lookup')
            CREATE TABLE device_access_lookup (device_access_id INT IDENTITY(1,1) PRIMARY KEY, device_access_name NVARCHAR(50));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM device_access_lookup WHERE device_access_name = 'Own Device') INSERT INTO device_access_lookup (device_access_name) VALUES ('Own Device');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM device_access_lookup WHERE device_access_name = 'Shared Device') INSERT INTO device_access_lookup (device_access_name) VALUES ('Shared Device');"
        )

        # digital_literacy_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'digital_literacy_lookup')
            CREATE TABLE digital_literacy_lookup (digital_literacy_id INT IDENTITY(1,1) PRIMARY KEY, digital_literacy_name NVARCHAR(50));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM digital_literacy_lookup WHERE digital_literacy_name = 'High') INSERT INTO digital_literacy_lookup (digital_literacy_name) VALUES ('High');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM digital_literacy_lookup WHERE digital_literacy_name = 'Low') INSERT INTO digital_literacy_lookup (digital_literacy_name) VALUES ('Low');"
        )

        # digital_literacy_support_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'digital_literacy_support_lookup')
            CREATE TABLE digital_literacy_support_lookup (digital_literacy_support_id INT IDENTITY(1,1) PRIMARY KEY, digital_literacy_support_name NVARCHAR(50));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM digital_literacy_support_lookup WHERE digital_literacy_support_name = 'Available') INSERT INTO digital_literacy_support_lookup (digital_literacy_support_name) VALUES ('Available');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM digital_literacy_support_lookup WHERE digital_literacy_support_name = 'Not Available') INSERT INTO digital_literacy_support_lookup (digital_literacy_support_name) VALUES ('Not Available');"
        )

        # disciplinary_incidents_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'disciplinary_incidents_lookup')
            CREATE TABLE disciplinary_incidents_lookup (disciplinary_incidents_id INT IDENTITY(1,1) PRIMARY KEY, disciplinary_incidents_name NVARCHAR(50));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM disciplinary_incidents_lookup WHERE disciplinary_incidents_name = 'None') INSERT INTO disciplinary_incidents_lookup (disciplinary_incidents_name) VALUES ('None');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM disciplinary_incidents_lookup WHERE disciplinary_incidents_name = 'Minor') INSERT INTO disciplinary_incidents_lookup (disciplinary_incidents_name) VALUES ('Minor');"
        )

        # dropout_reason_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'dropout_reason_lookup')
            CREATE TABLE dropout_reason_lookup (dropout_reason_id INT IDENTITY(1,1) PRIMARY KEY, dropout_reason_name NVARCHAR(100));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM dropout_reason_lookup WHERE dropout_reason_name = 'Financial') INSERT INTO dropout_reason_lookup (dropout_reason_name) VALUES ('Financial');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM dropout_reason_lookup WHERE dropout_reason_name = 'Health') INSERT INTO dropout_reason_lookup (dropout_reason_name) VALUES ('Health');"
        )

        # engagement_level_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'engagement_level_lookup')
            CREATE TABLE engagement_level_lookup (engagement_level_id INT IDENTITY(1,1) PRIMARY KEY, engagement_level_name NVARCHAR(50));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM engagement_level_lookup WHERE engagement_level_name = 'High') INSERT INTO engagement_level_lookup (engagement_level_name) VALUES ('High');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM engagement_level_lookup WHERE engagement_level_name = 'Low') INSERT INTO engagement_level_lookup (engagement_level_name) VALUES ('Low');"
        )

        # extracurricular_activity_type_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'extracurricular_activity_type_lookup')
            CREATE TABLE extracurricular_activity_type_lookup (activity_type_id INT IDENTITY(1,1) PRIMARY KEY, activity_type_name NVARCHAR(50));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM extracurricular_activity_type_lookup WHERE activity_type_name = 'Sports') INSERT INTO extracurricular_activity_type_lookup (activity_type_name) VALUES ('Sports');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM extracurricular_activity_type_lookup WHERE activity_type_name = 'Art') INSERT INTO extracurricular_activity_type_lookup (activity_type_name) VALUES ('Art');"
        )

        # extracurricular_role_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'extracurricular_role_lookup')
            CREATE TABLE extracurricular_role_lookup (role_id INT IDENTITY(1,1) PRIMARY KEY, role_name NVARCHAR(50));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM extracurricular_role_lookup WHERE role_name = 'Leader') INSERT INTO extracurricular_role_lookup (role_name) VALUES ('Leader');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM extracurricular_role_lookup WHERE role_name = 'Member') INSERT INTO extracurricular_role_lookup (role_name) VALUES ('Member');"
        )

        # funding_model_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'funding_model_lookup')
            CREATE TABLE funding_model_lookup (funding_model_id INT IDENTITY(1,1) PRIMARY KEY, funding_model_name NVARCHAR(50));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM funding_model_lookup WHERE funding_model_name = 'Public') INSERT INTO funding_model_lookup (funding_model_name) VALUES ('Public');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM funding_model_lookup WHERE funding_model_name = 'Private') INSERT INTO funding_model_lookup (funding_model_name) VALUES ('Private');"
        )

        # geographic_density_classification_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'geographic_density_classification_lookup')
            CREATE TABLE geographic_density_classification_lookup (geographic_density_classification_id INT IDENTITY(1,1) PRIMARY KEY, geographic_density_classification_name NVARCHAR(50));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM geographic_density_classification_lookup WHERE geographic_density_classification_name = 'Urban') INSERT INTO geographic_density_classification_lookup (geographic_density_classification_name) VALUES ('Urban');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM geographic_density_classification_lookup WHERE geographic_density_classification_name = 'Rural') INSERT INTO geographic_density_classification_lookup (geographic_density_classification_name) VALUES ('Rural');"
        )

        # health_conditions_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'health_conditions_lookup')
            CREATE TABLE health_conditions_lookup (health_conditions_id INT IDENTITY(1,1) PRIMARY KEY, health_conditions_name NVARCHAR(50));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM health_conditions_lookup WHERE health_conditions_name = 'None') INSERT INTO health_conditions_lookup (health_conditions_name) VALUES ('None');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM health_conditions_lookup WHERE health_conditions_name = 'Asthma') INSERT INTO health_conditions_lookup (health_conditions_name) VALUES ('Asthma');"
        )

        # highest_qualification_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'highest_qualification_lookup')
            CREATE TABLE highest_qualification_lookup (highest_qualification_id INT IDENTITY(1,1) PRIMARY KEY, highest_qualification_name NVARCHAR(100));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM highest_qualification_lookup WHERE highest_qualification_name = 'Matric') INSERT INTO highest_qualification_lookup (highest_qualification_name) VALUES ('Matric');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM highest_qualification_lookup WHERE highest_qualification_name = 'Degree') INSERT INTO highest_qualification_lookup (highest_qualification_name) VALUES ('Degree');"
        )

        # internet_access_quality_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'internet_access_quality_lookup')
            CREATE TABLE internet_access_quality_lookup (internet_access_quality_id INT IDENTITY(1,1) PRIMARY KEY, internet_access_quality_name NVARCHAR(50));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM internet_access_quality_lookup WHERE internet_access_quality_name = 'High Speed') INSERT INTO internet_access_quality_lookup (internet_access_quality_name) VALUES ('High Speed');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM internet_access_quality_lookup WHERE internet_access_quality_name = 'Low Speed') INSERT INTO internet_access_quality_lookup (internet_access_quality_name) VALUES ('Low Speed');"
        )

        # intervention_outcome_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'intervention_outcome_lookup')
            CREATE TABLE intervention_outcome_lookup (intervention_outcome_id INT IDENTITY(1,1) PRIMARY KEY, intervention_outcome_name NVARCHAR(50));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM intervention_outcome_lookup WHERE intervention_outcome_name = 'Successful') INSERT INTO intervention_outcome_lookup (intervention_outcome_name) VALUES ('Successful');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM intervention_outcome_lookup WHERE intervention_outcome_name = 'Unsuccessful') INSERT INTO intervention_outcome_lookup (intervention_outcome_name) VALUES ('Unsuccessful');"
        )

        # intervention_type_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'intervention_type_lookup')
            CREATE TABLE intervention_type_lookup (intervention_type_id INT IDENTITY(1,1) PRIMARY KEY, intervention_type_name NVARCHAR(50));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM intervention_type_lookup WHERE intervention_type_name = 'Tutoring') INSERT INTO intervention_type_lookup (intervention_type_name) VALUES ('Tutoring');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM intervention_type_lookup WHERE intervention_type_name = 'Counseling') INSERT INTO intervention_type_lookup (intervention_type_name) VALUES ('Counseling');"
        )

        # language_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'language_lookup')
            CREATE TABLE language_lookup (language_id INT IDENTITY(1,1) PRIMARY KEY, language_name NVARCHAR(50));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM language_lookup WHERE language_name = 'English') INSERT INTO language_lookup (language_name) VALUES ('English');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM language_lookup WHERE language_name = 'Afrikaans') INSERT INTO language_lookup (language_name) VALUES ('Afrikaans');"
        )

        # learning_resources_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'learning_resources_lookup')
            CREATE TABLE learning_resources_lookup (learning_resources_id INT IDENTITY(1,1) PRIMARY KEY, learning_resources_name NVARCHAR(50));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM learning_resources_lookup WHERE learning_resources_name = 'Books') INSERT INTO learning_resources_lookup (learning_resources_name) VALUES ('Books');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM learning_resources_lookup WHERE learning_resources_name = 'Online') INSERT INTO learning_resources_lookup (learning_resources_name) VALUES ('Online');"
        )

        # local_municipality_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'local_municipality_lookup')
            CREATE TABLE local_municipality_lookup (local_municipality_id INT IDENTITY(1,1) PRIMARY KEY, local_municipality_name NVARCHAR(100));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM local_municipality_lookup WHERE local_municipality_name = 'City of JHB') INSERT INTO local_municipality_lookup (local_municipality_name) VALUES ('City of JHB');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM local_municipality_lookup WHERE local_municipality_name = 'Ekurhuleni') INSERT INTO local_municipality_lookup (local_municipality_name) VALUES ('Ekurhuleni');"
        )

        # mental_health_support_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'mental_health_support_lookup')
            CREATE TABLE mental_health_support_lookup (mental_health_support_id INT IDENTITY(1,1) PRIMARY KEY, mental_health_support_name NVARCHAR(100));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM mental_health_support_lookup WHERE mental_health_support_name = 'Available') INSERT INTO mental_health_support_lookup (mental_health_support_name) VALUES ('Available');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM mental_health_support_lookup WHERE mental_health_support_name = 'Not Available') INSERT INTO mental_health_support_lookup (mental_health_support_name) VALUES ('Not Available');"
        )

        # nutrition_status_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'nutrition_status_lookup')
            CREATE TABLE nutrition_status_lookup (nutrition_status_id INT IDENTITY(1,1) PRIMARY KEY, nutrition_status_name NVARCHAR(50));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM nutrition_status_lookup WHERE nutrition_status_name = 'Good') INSERT INTO nutrition_status_lookup (nutrition_status_name) VALUES ('Good');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM nutrition_status_lookup WHERE nutrition_status_name = 'Poor') INSERT INTO nutrition_status_lookup (nutrition_status_name) VALUES ('Poor');"
        )

        # parental_employment_status_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'parental_employment_status_lookup')
            CREATE TABLE parental_employment_status_lookup (parental_employment_status_id INT IDENTITY(1,1) PRIMARY KEY, parental_employment_status_name NVARCHAR(50));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM parental_employment_status_lookup WHERE parental_employment_status_name = 'Employed') INSERT INTO parental_employment_status_lookup (parental_employment_status_name) VALUES ('Employed');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM parental_employment_status_lookup WHERE parental_employment_status_name = 'Unemployed') INSERT INTO parental_employment_status_lookup (parental_employment_status_name) VALUES ('Unemployed');"
        )

        # parental_marital_status_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'parental_marital_status_lookup')
            CREATE TABLE parental_marital_status_lookup (parental_marital_status_id INT IDENTITY(1,1) PRIMARY KEY, parental_marital_status_name NVARCHAR(50));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM parental_marital_status_lookup WHERE parental_marital_status_name = 'Married') INSERT INTO parental_marital_status_lookup (parental_marital_status_name) VALUES ('Married');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM parental_marital_status_lookup WHERE parental_marital_status_name = 'Single') INSERT INTO parental_marital_status_lookup (parental_marital_status_name) VALUES ('Single');"
        )

        # parental_tech_support_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'parental_tech_support_lookup')
            CREATE TABLE parental_tech_support_lookup (parental_tech_support_id INT IDENTITY(1,1) PRIMARY KEY, parental_tech_support_name NVARCHAR(50));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM parental_tech_support_lookup WHERE parental_tech_support_name = 'High') INSERT INTO parental_tech_support_lookup (parental_tech_support_name) VALUES ('High');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM parental_tech_support_lookup WHERE parental_tech_support_name = 'Low') INSERT INTO parental_tech_support_lookup (parental_tech_support_name) VALUES ('Low');"
        )

        # psychological_assessment_type_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'psychological_assessment_type_lookup')
            CREATE TABLE psychological_assessment_type_lookup (assessment_type_id INT IDENTITY(1,1) PRIMARY KEY, assessment_type_name NVARCHAR(50));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM psychological_assessment_type_lookup WHERE assessment_type_name = 'Cognitive') INSERT INTO psychological_assessment_type_lookup (assessment_type_name) VALUES ('Cognitive');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM psychological_assessment_type_lookup WHERE assessment_type_name = 'Behavioral') INSERT INTO psychological_assessment_type_lookup (assessment_type_name) VALUES ('Behavioral');"
        )

        # school_infrastructure_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'school_infrastructure_lookup')
            CREATE TABLE school_infrastructure_lookup (school_infrastructure_id INT IDENTITY(1,1) PRIMARY KEY, school_infrastructure_name NVARCHAR(50));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM school_infrastructure_lookup WHERE school_infrastructure_name = 'Good') INSERT INTO school_infrastructure_lookup (school_infrastructure_name) VALUES ('Good');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM school_infrastructure_lookup WHERE school_infrastructure_name = 'Average') INSERT INTO school_infrastructure_lookup (school_infrastructure_name) VALUES ('Average');"
        )

        # school_phase_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'school_phase_lookup')
            CREATE TABLE school_phase_lookup (school_phase_id INT IDENTITY(1,1) PRIMARY KEY, school_phase_name NVARCHAR(50));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM school_phase_lookup WHERE school_phase_name = 'Primary') INSERT INTO school_phase_lookup (school_phase_name) VALUES ('Primary');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM school_phase_lookup WHERE school_phase_name = 'Secondary') INSERT INTO school_phase_lookup (school_phase_name) VALUES ('Secondary');"
        )

        # school_prototype_size_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'school_prototype_size_lookup')
            CREATE TABLE school_prototype_size_lookup (school_prototype_size_id INT IDENTITY(1,1) PRIMARY KEY, school_prototype_size_name NVARCHAR(50));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM school_prototype_size_lookup WHERE school_prototype_size_name = 'Small') INSERT INTO school_prototype_size_lookup (school_prototype_size_name) VALUES ('Small');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM school_prototype_size_lookup WHERE school_prototype_size_name = 'Large') INSERT INTO school_prototype_size_lookup (school_prototype_size_name) VALUES ('Large');"
        )

        # school_safety_perception_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'school_safety_perception_lookup')
            CREATE TABLE school_safety_perception_lookup (school_safety_perception_id INT IDENTITY(1,1) PRIMARY KEY, school_safety_perception_name NVARCHAR(50));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM school_safety_perception_lookup WHERE school_safety_perception_name = 'Safe') INSERT INTO school_safety_perception_lookup (school_safety_perception_name) VALUES ('Safe');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM school_safety_perception_lookup WHERE school_safety_perception_name = 'Unsafe') INSERT INTO school_safety_perception_lookup (school_safety_perception_name) VALUES ('Unsafe');"
        )

        # school_specialization_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'school_specialization_lookup')
            CREATE TABLE school_specialization_lookup (school_specialization_id INT IDENTITY(1,1) PRIMARY KEY, school_specialization_name NVARCHAR(50));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM school_specialization_lookup WHERE school_specialization_name = 'Academic') INSERT INTO school_specialization_lookup (school_specialization_name) VALUES ('Academic');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM school_specialization_lookup WHERE school_specialization_name = 'Technical') INSERT INTO school_specialization_lookup (school_specialization_name) VALUES ('Technical');"
        )

        # school_status_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'school_status_lookup')
            CREATE TABLE school_status_lookup (school_status_id INT IDENTITY(1,1) PRIMARY KEY, school_status_name NVARCHAR(50));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM school_status_lookup WHERE school_status_name = 'Open') INSERT INTO school_status_lookup (school_status_name) VALUES ('Open');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM school_status_lookup WHERE school_status_name = 'Closed') INSERT INTO school_status_lookup (school_status_name) VALUES ('Closed');"
        )

        # school_type_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'school_type_lookup')
            CREATE TABLE school_type_lookup (school_type_id INT IDENTITY(1,1) PRIMARY KEY, school_type_name NVARCHAR(50));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM school_type_lookup WHERE school_type_name = 'Public') INSERT INTO school_type_lookup (school_type_name) VALUES ('Public');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM school_type_lookup WHERE school_type_name = 'Private') INSERT INTO school_type_lookup (school_type_name) VALUES ('Private');"
        )

        # social_grants_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'social_grants_lookup')
            CREATE TABLE social_grants_lookup (social_grants_id INT IDENTITY(1,1) PRIMARY KEY, social_grants_name NVARCHAR(10));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM social_grants_lookup WHERE social_grants_name = 'Yes') INSERT INTO social_grants_lookup (social_grants_name) VALUES ('Yes');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM social_grants_lookup WHERE social_grants_name = 'No') INSERT INTO social_grants_lookup (social_grants_name) VALUES ('No');"
        )

        # software_platform_access_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'software_platform_access_lookup')
            CREATE TABLE software_platform_access_lookup (software_platform_access_id INT IDENTITY(1,1) PRIMARY KEY, software_platform_access_name NVARCHAR(50));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM software_platform_access_lookup WHERE software_platform_access_name = 'MS Teams') INSERT INTO software_platform_access_lookup (software_platform_access_name) VALUES ('MS Teams');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM software_platform_access_lookup WHERE software_platform_access_name = 'Google Classroom') INSERT INTO software_platform_access_lookup (software_platform_access_name) VALUES ('Google Classroom');"
        )

        # study_environment_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'study_environment_lookup')
            CREATE TABLE study_environment_lookup (study_environment_id INT IDENTITY(1,1) PRIMARY KEY, study_environment_name NVARCHAR(50));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM study_environment_lookup WHERE study_environment_name = 'Quiet') INSERT INTO study_environment_lookup (study_environment_name) VALUES ('Quiet');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM study_environment_lookup WHERE study_environment_name = 'Noisy') INSERT INTO study_environment_lookup (study_environment_name) VALUES ('Noisy');"
        )

        # teacher_effectiveness_rating_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'teacher_effectiveness_rating_lookup')
            CREATE TABLE teacher_effectiveness_rating_lookup (teacher_effectiveness_rating_id INT IDENTITY(1,1) PRIMARY KEY, teacher_effectiveness_rating_name NVARCHAR(50));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM teacher_effectiveness_rating_lookup WHERE teacher_effectiveness_rating_name = 'High') INSERT INTO teacher_effectiveness_rating_lookup (teacher_effectiveness_rating_name) VALUES ('High');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM teacher_effectiveness_rating_lookup WHERE teacher_effectiveness_rating_name = 'Medium') INSERT INTO teacher_effectiveness_rating_lookup (teacher_effectiveness_rating_name) VALUES ('Medium');"
        )

        # teacher_student_ratio_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'teacher_student_ratio_lookup')
            CREATE TABLE teacher_student_ratio_lookup (teacher_student_ratio_id INT IDENTITY(1,1) PRIMARY KEY, teacher_student_ratio_name NVARCHAR(50));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM teacher_student_ratio_lookup WHERE teacher_student_ratio_name = 'Low') INSERT INTO teacher_student_ratio_lookup (teacher_student_ratio_name) VALUES ('Low');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM teacher_student_ratio_lookup WHERE teacher_student_ratio_name = 'High') INSERT INTO teacher_student_ratio_lookup (teacher_student_ratio_name) VALUES ('High');"
        )

        # urban_rural_classification_lookup
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'urban_rural_classification_lookup')
            CREATE TABLE urban_rural_classification_lookup (urban_rural_classification_id INT IDENTITY(1,1) PRIMARY KEY, urban_rural_classification_name NVARCHAR(50));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM urban_rural_classification_lookup WHERE urban_rural_classification_name = 'Urban') INSERT INTO urban_rural_classification_lookup (urban_rural_classification_name) VALUES ('Urban');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM urban_rural_classification_lookup WHERE urban_rural_classification_name = 'Rural') INSERT INTO urban_rural_classification_lookup (urban_rural_classification_name) VALUES ('Rural');"
        )

        # provinces
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'provinces')
            CREATE TABLE provinces (provinceid INT IDENTITY(1,1) PRIMARY KEY, province_name NVARCHAR(100));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM provinces WHERE province_name = 'Gauteng') INSERT INTO provinces (province_name) VALUES ('Gauteng');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM provinces WHERE province_name = 'Western Cape') INSERT INTO provinces (province_name) VALUES ('Western Cape');"
        )

        # districts
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'districts')
            CREATE TABLE districts (districtid INT IDENTITY(1,1) PRIMARY KEY, district_name NVARCHAR(100), provinceid INT);
            """
        )
        # Note: For districts, you'll need to ensure the provinceid exists if you want to maintain referential integrity
        # For this dummy data, we'll assume province IDs 1 and 2 are already generated by the above inserts.
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM districts WHERE district_name = 'Johannesburg Central') INSERT INTO districts (district_name, provinceid) VALUES ('Johannesburg Central', (SELECT provinceid FROM provinces WHERE province_name = 'Gauteng'));"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM districts WHERE district_name = 'Cape Town Metro') INSERT INTO districts (district_name, provinceid) VALUES ('Cape Town Metro', (SELECT provinceid FROM provinces WHERE province_name = 'Western Cape'));"
        )

        # subjects
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'subjects')
            CREATE TABLE subjects (subjectid INT IDENTITY(1,1) PRIMARY KEY, subject_name NVARCHAR(100));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM subjects WHERE subject_name = 'Mathematics') INSERT INTO subjects (subject_name) VALUES ('Mathematics');"
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM subjects WHERE subject_name = 'Science') INSERT INTO subjects (subject_name) VALUES ('Science');"
        )

        # schools
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'schools')
            CREATE TABLE schools (schoolid BIGINT IDENTITY(1,1) PRIMARY KEY, schoolname NVARCHAR(255), quintile INT, infrastructurescore INT, teacherabsenteeismrate DECIMAL(17,15));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM schools WHERE schoolname = 'Central High') INSERT INTO schools (schoolname, quintile, infrastructurescore, teacherabsenteeismrate) VALUES ('Central High', 3, 80, 0.05);"
        )

        # parents
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'parents')
            CREATE TABLE parents (parentid INT IDENTITY(1,1) PRIMARY KEY, firstname NVARCHAR(50), lastname NVARCHAR(50));
            """
        )
        db_manager.execute_non_query(
            "IF NOT EXISTS (SELECT 1 FROM parents WHERE firstname = 'John' AND lastname = 'Doe') INSERT INTO parents (firstname, lastname) VALUES ('John', 'Doe');"
        )

        preprocessor = DataPreprocessor()

        sample_student_data = {
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
            "race": "Black African",
            "access_to_healthcare": "Good",
            "access_to_specialized_programs": "Yes",
            "allocation_category": "Category A",
            "device_access": "Own Device",
            "digital_literacy": "High",
            "digital_literacy_support": "Available",
            "disciplinary_incidents": "None",
            "dropout_reason": "Financial",
            "engagement_level": "High",
            "extracurricular_activity_type": "Sports",
            "extracurricular_role": "Leader",
            "funding_model": "Public",
            "geographic_density_classification": "Urban",
            "health_conditions": "None",
            "highest_qualification": "Matric",
            "internet_access_quality": "High Speed",
            "intervention_outcome": "Successful",
            "intervention_type": "Tutoring",
            "language": "English",
            "learning_resources": "Books",
            "local_municipality": "City of JHB",
            "mental_health_support": "Available",
            "nutrition_status": "Good",
            "parental_employment_status": "Employed",
            "parental_marital_status": "Married",
            "parental_tech_support": "High",
            "psychological_assessment_type": "Cognitive",
            "school_infrastructure": "Good",
            "school_phase": "Secondary",
            "school_prototype_size": "Large",
            "school_safety_perception": "Safe",
            "school_specialization": "Academic",
            "school_status": "Open",
            "school_type": "Public",
            "social_grants": "Yes",
            "software_platform_access": "MS Teams",
            "study_environment": "Quiet",
            "teacher_effectiveness_rating": "High",
            "teacher_student_ratio": "Low",
            "urban_rural_classification": "Urban",
            "academic_records": [
                {"subject": "Math", "mark": 75},
                {"subject": "Science", "mark": 80},
            ],
            "attendance_records": [
                {"date": "2025-05-01", "status": "Present"},  # Public holiday
                {"date": "2025-05-02", "status": "Absent"},
                {
                    "date": "2025-05-03",
                    "status": "Present",
                },  # Saturday - should be excluded
                {
                    "date": "2025-05-04",
                    "status": "Present",
                },  # Sunday - should be excluded
                {"date": "2025-05-05", "status": "Present"},
                {"date": "2025-06-16", "status": "Present"},  # Public holiday
            ],
        }

        processed_df = preprocessor.preprocess_student_data(sample_student_data)
        print("\nProcessed Data for Model:")
        print(processed_df)

        # Test attendance calculation separately with direct data
        attendance_df_test = pd.DataFrame(
            [
                {"date": "2025-05-01", "status": "Present"},  # This is a public holiday
                {"date": "2025-05-02", "status": "Absent"},
                {"date": "2025-05-03", "status": "Present"},  # Saturday
                {"date": "2025-05-04", "status": "Present"},  # Sunday
                {"date": "2025-05-05", "status": "Present"},
                {"date": "2025-05-06", "status": "Present"},
                {"date": "2025-05-07", "status": "Present"},
                {"date": "2025-05-08", "status": "Present"},
                {"date": "2025-05-09", "status": "Present"},
            ]
        )
        attendance_percent = preprocessor.calculate_attendance_percentage(
            attendance_df_test
        )
        print(
            f"\nAttendance Percentage (excluding weekends and holidays): {attendance_percent:.2f}%"
        )

    except Exception as e:
        logger.error(f"An error occurred during data_preprocessing test: {e}")
    finally:
        db_manager.close()
