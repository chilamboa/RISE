Use StudentMarks
go

-- Drop Foreign Key Constraints
IF OBJECT_ID(N'dbo.fk_academic_records_studentid_students_studentid', 'F') IS NOT NULL
    ALTER TABLE [dbo].[academic_records] DROP CONSTRAINT [fk_academic_records_studentid_students_studentid];
IF OBJECT_ID(N'dbo.fk_academic_records_schoolid_schools_schoolid', 'F') IS NOT NULL
    ALTER TABLE [dbo].[academic_records] DROP CONSTRAINT [fk_academic_records_schoolid_schools_schoolid];
IF OBJECT_ID(N'dbo.fk_academic_records_subjectid_subjects_subjectid', 'F') IS NOT NULL
    ALTER TABLE [dbo].[academic_records] DROP CONSTRAINT [fk_academic_records_subjectid_subjects_subjectid];
IF OBJECT_ID(N'dbo.fk_attendance_studentid_students_studentid', 'F') IS NOT NULL
    ALTER TABLE [dbo].[attendance] DROP CONSTRAINT [fk_attendance_studentid_students_studentid];
IF OBJECT_ID(N'dbo.fk_districts_provinceid_provinces_provinceid', 'F') IS NOT NULL
    ALTER TABLE [dbo].[districts] DROP CONSTRAINT [fk_districts_provinceid_provinces_provinceid];
IF OBJECT_ID(N'dbo.fk_extracurricular_activities_studentid_students_studentid', 'F') IS NOT NULL
    ALTER TABLE [dbo].[extracurricular_activities] DROP CONSTRAINT [fk_extracurricular_activities_studentid_students_studentid];
IF OBJECT_ID(N'dbo.fk_interventions_studentid_students_studentid', 'F') IS NOT NULL
    ALTER TABLE [dbo].[interventions] DROP CONSTRAINT [fk_interventions_studentid_students_studentid];
IF OBJECT_ID(N'dbo.fk_psychological_assessments_studentid_students_studentid', 'F') IS NOT NULL
    ALTER TABLE [dbo].[psychological_assessments] DROP CONSTRAINT [fk_psychological_assessments_studentid_students_studentid];
IF OBJECT_ID(N'dbo.fk_school_staff_highest_qualification_id_highest_qualification_lookup_highest_qualification_id', 'F') IS NOT NULL
    ALTER TABLE [dbo].[school_staff] DROP CONSTRAINT [fk_school_staff_highest_qualification_id_highest_qualification_lookup_highest_qualification_id];
IF OBJECT_ID(N'dbo.fk_school_staff_teacher_effectiveness_rating_id_teacher_effectiveness_rating_lookup_teacher_effectiveness_rating_id', 'F') IS NOT NULL
    ALTER TABLE [dbo].[school_staff] DROP CONSTRAINT [fk_school_staff_teacher_effectiveness_rating_id_teacher_effectiveness_rating_lookup_teacher_effectiveness_rating_id];
IF OBJECT_ID(N'dbo.fk_school_staff_school_id_schools_schoolid', 'F') IS NOT NULL
    ALTER TABLE [dbo].[school_staff] DROP CONSTRAINT [fk_school_staff_school_id_schools_schoolid];
IF OBJECT_ID(N'dbo.fk_school_staff_subject_taught_id_subjects_subjectid', 'F') IS NOT NULL
    ALTER TABLE [dbo].[school_staff] DROP CONSTRAINT [fk_school_staff_subject_taught_id_subjects_subjectid];
IF OBJECT_ID(N'dbo.fk_student_years_studentid_students_studentid', 'F') IS NOT NULL
    ALTER TABLE [dbo].[student_years] DROP CONSTRAINT [fk_student_years_studentid_students_studentid];
IF OBJECT_ID(N'dbo.fk_student_years_schoolid_schools_schoolid', 'F') IS NOT NULL
    ALTER TABLE [dbo].[student_years] DROP CONSTRAINT [fk_student_years_schoolid_schools_schoolid];
IF OBJECT_ID(N'dbo.fk_students_parentid1_parents_parentid', 'F') IS NOT NULL
    ALTER TABLE [dbo].[students] DROP CONSTRAINT [fk_students_parentid1_parents_parentid];
IF OBJECT_ID(N'dbo.fk_students_parentid2_parents_parentid', 'F') IS NOT NULL
    ALTER TABLE [dbo].[students] DROP CONSTRAINT [fk_students_parentid2_parents_parentid];
GO

-- Drop Foreign Key Constraints
IF OBJECT_ID(N'dbo.fk_academic_records_studentid_students_studentid', 'F') IS NOT NULL
ALTER TABLE [dbo].[academic_records] DROP CONSTRAINT [fk_academic_records_studentid_students_studentid];
IF OBJECT_ID(N'dbo.fk_academic_records_schoolid_schools_schoolid', 'F') IS NOT NULL
ALTER TABLE [dbo].[academic_records] DROP CONSTRAINT [fk_academic_records_schoolid_schools_schoolid];
IF OBJECT_ID(N'dbo.fk_academic_records_subjectid_subjects_subjectid', 'F') IS NOT NULL
ALTER TABLE [dbo].[academic_records] DROP CONSTRAINT [fk_academic_records_subjectid_subjects_subjectid];
IF OBJECT_ID(N'dbo.fk_attendance_studentid_students_studentid', 'F') IS NOT NULL
ALTER TABLE [dbo].[attendance] DROP CONSTRAINT [fk_attendance_studentid_students_studentid];
IF OBJECT_ID(N'dbo.fk_districts_provinceid_provinces_provinceid', 'F') IS NOT NULL
ALTER TABLE [dbo].[districts] DROP CONSTRAINT [fk_districts_provinceid_provinces_provinceid];
IF OBJECT_ID(N'dbo.fk_extracurricular_activities_studentid_students_studentid', 'F') IS NOT NULL
ALTER TABLE [dbo].[extracurricular_activities] DROP CONSTRAINT [fk_extracurricular_activities_studentid_students_studentid];
IF OBJECT_ID(N'dbo.fk_interventions_studentid_students_studentid', 'F') IS NOT NULL
ALTER TABLE [dbo].[interventions] DROP CONSTRAINT [fk_interventions_studentid_students_studentid];
IF OBJECT_ID(N'dbo.fk_psychological_assessments_studentid_students_studentid', 'F') IS NOT NULL
ALTER TABLE [dbo].[psychological_assessments] DROP CONSTRAINT [fk_psychological_assessments_studentid_students_studentid];
IF OBJECT_ID(N'dbo.fk_school_staff_highest_qualification_id_highest_qualification_lookup_highest_qualification_id', 'F') IS NOT NULL
ALTER TABLE [dbo].[school_staff] DROP CONSTRAINT [fk_school_staff_highest_qualification_id_highest_qualification_lookup_highest_qualification_id];
IF OBJECT_ID(N'dbo.fk_school_staff_teacher_effectiveness_rating_id_teacher_effectiveness_rating_lookup_teacher_effectiveness_rating_id', 'F') IS NOT NULL
ALTER TABLE [dbo].[school_staff] DROP CONSTRAINT [fk_school_staff_teacher_effectiveness_rating_id_teacher_effectiveness_rating_lookup_teacher_effectiveness_rating_id];
IF OBJECT_ID(N'dbo.fk_school_staff_school_id_schools_schoolid', 'F') IS NOT NULL
ALTER TABLE [dbo].[school_staff] DROP CONSTRAINT [fk_school_staff_school_id_schools_schoolid];
IF OBJECT_ID(N'dbo.fk_school_staff_subject_taught_id_subjects_subjectid', 'F') IS NOT NULL
ALTER TABLE [dbo].[school_staff] DROP CONSTRAINT [fk_school_staff_subject_taught_id_subjects_subjectid];
IF OBJECT_ID(N'dbo.fk_student_years_studentid_students_studentid', 'F') IS NOT NULL
ALTER TABLE [dbo].[student_years] DROP CONSTRAINT [fk_student_years_studentid_students_studentid];
IF OBJECT_ID(N'dbo.fk_student_years_schoolid_schools_schoolid', 'F') IS NOT NULL
ALTER TABLE [dbo].[student_years] DROP CONSTRAINT [fk_student_years_schoolid_schools_schoolid];
IF OBJECT_ID(N'dbo.fk_students_parentid1_parents_parentid', 'F') IS NOT NULL
ALTER TABLE [dbo].[students] DROP CONSTRAINT [fk_students_parentid1_parents_parentid];
IF OBJECT_ID(N'dbo.fk_students_parentid2_parents_parentid', 'F') IS NOT NULL
ALTER TABLE [dbo].[students] DROP CONSTRAINT [fk_students_parentid2_parents_parentid];
GO

-- Drop Tables in reverse dependency order
IF OBJECT_ID(N'dbo.academic_records', 'U') IS NOT NULL
    DROP TABLE [dbo].[academic_records];
IF OBJECT_ID(N'dbo.attendance', 'U') IS NOT NULL
    DROP TABLE [dbo].[attendance];
IF OBJECT_ID(N'dbo.extracurricular_activities', 'U') IS NOT NULL
    DROP TABLE [dbo].[extracurricular_activities];
IF OBJECT_ID(N'dbo.interventions', 'U') IS NOT NULL
    DROP TABLE [dbo].[interventions];
IF OBJECT_ID(N'dbo.psychological_assessments', 'U') IS NOT NULL
    DROP TABLE [dbo].[psychological_assessments];
IF OBJECT_ID(N'dbo.student_years', 'U') IS NOT NULL
    DROP TABLE [dbo].[student_years];
IF OBJECT_ID(N'dbo.school_staff', 'U') IS NOT NULL
    DROP TABLE [dbo].[school_staff];
IF OBJECT_ID(N'dbo.students', 'U') IS NOT NULL
    DROP TABLE [dbo].[students];
IF OBJECT_ID(N'dbo.schools', 'U') IS NOT NULL
    DROP TABLE [dbo].[schools];
IF OBJECT_ID(N'dbo.districts', 'U') IS NOT NULL
    DROP TABLE [dbo].[districts];
IF OBJECT_ID(N'dbo.parents', 'U') IS NOT NULL
    DROP TABLE [dbo].[parents];
IF OBJECT_ID(N'dbo.subjects', 'U') IS NOT NULL
    DROP TABLE [dbo].[subjects];
IF OBJECT_ID(N'dbo.provinces', 'U') IS NOT NULL
    DROP TABLE [dbo].[provinces];

-- Drop all lookup tables
IF OBJECT_ID(N'dbo.academic_assessment_type_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[academic_assessment_type_lookup];
IF OBJECT_ID(N'dbo.access_to_healthcare_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[access_to_healthcare_lookup];
IF OBJECT_ID(N'dbo.access_to_specialized_programs_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[access_to_specialized_programs_lookup];
IF OBJECT_ID(N'dbo.allocation_category_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[allocation_category_lookup];
IF OBJECT_ID(N'dbo.attendance_status_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[attendance_status_lookup];
IF OBJECT_ID(N'dbo.device_access_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[device_access_lookup];
IF OBJECT_ID(N'dbo.digital_literacy_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[digital_literacy_lookup];
IF OBJECT_ID(N'dbo.digital_literacy_support_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[digital_literacy_support_lookup];
IF OBJECT_ID(N'dbo.disability_status_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[disability_status_lookup];
IF OBJECT_ID(N'dbo.disciplinary_incidents_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[disciplinary_incidents_lookup];
IF OBJECT_ID(N'dbo.dropout_reason_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[dropout_reason_lookup];
IF OBJECT_ID(N'dbo.engagement_level_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[engagement_level_lookup];
IF OBJECT_ID(N'dbo.extracurricular_activity_type_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[extracurricular_activity_type_lookup];
IF OBJECT_ID(N'dbo.extracurricular_role_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[extracurricular_role_lookup];
IF OBJECT_ID(N'dbo.funding_model_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[funding_model_lookup];
IF OBJECT_ID(N'dbo.gender_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[gender_lookup];
IF OBJECT_ID(N'dbo.geographic_density_classification_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[geographic_density_classification_lookup];
IF OBJECT_ID(N'dbo.health_conditions_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[health_conditions_lookup];
IF OBJECT_ID(N'dbo.highest_qualification_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[highest_qualification_lookup];
IF OBJECT_ID(N'dbo.home_learning_environment_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[home_learning_environment_lookup];
IF OBJECT_ID(N'dbo.internet_access_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[internet_access_lookup];
IF OBJECT_ID(N'dbo.internet_access_quality_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[internet_access_quality_lookup];
IF OBJECT_ID(N'dbo.intervention_outcome_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[intervention_outcome_lookup];
IF OBJECT_ID(N'dbo.intervention_type_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[intervention_type_lookup];
IF OBJECT_ID(N'dbo.language_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[language_lookup];
IF OBJECT_ID(N'dbo.learning_resources_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[learning_resources_lookup];
IF OBJECT_ID(N'dbo.local_municipality_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[local_municipality_lookup];
IF OBJECT_ID(N'dbo.mental_health_support_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[mental_health_support_lookup];
IF OBJECT_ID(N'dbo.nutrition_status_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[nutrition_status_lookup];
IF OBJECT_ID(N'dbo.parental_education_level_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[parental_education_level_lookup];
IF OBJECT_ID(N'dbo.parental_employment_status_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[parental_employment_status_lookup];
IF OBJECT_ID(N'dbo.parental_marital_status_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[parental_marital_status_lookup];
IF OBJECT_ID(N'dbo.parental_tech_support_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[parental_tech_support_lookup];
IF OBJECT_ID(N'dbo.psychological_assessment_type_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[psychological_assessment_type_lookup];
IF OBJECT_ID(N'dbo.race_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[race_lookup];
IF OBJECT_ID(N'dbo.school_infrastructure_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[school_infrastructure_lookup];
IF OBJECT_ID(N'dbo.school_phase_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[school_phase_lookup];
IF OBJECT_ID(N'dbo.school_prototype_size_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[school_prototype_size_lookup];
IF OBJECT_ID(N'dbo.school_safety_perception_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[school_safety_perception_lookup];
IF OBJECT_ID(N'dbo.school_specialization_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[school_specialization_lookup];
IF OBJECT_ID(N'dbo.school_status_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[school_status_lookup];
IF OBJECT_ID(N'dbo.school_type_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[school_type_lookup];
IF OBJECT_ID(N'dbo.social_grants_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[social_grants_lookup];
IF OBJECT_ID(N'dbo.socioeconomic_classification_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[socioeconomic_classification_lookup];
IF OBJECT_ID(N'dbo.software_platform_access_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[software_platform_access_lookup];
IF OBJECT_ID(N'dbo.study_environment_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[study_environment_lookup];
IF OBJECT_ID(N'dbo.study_habits_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[study_habits_lookup];
IF OBJECT_ID(N'dbo.teacher_effectiveness_rating_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[teacher_effectiveness_rating_lookup];
IF OBJECT_ID(N'dbo.teacher_student_ratio_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[teacher_student_ratio_lookup];
IF OBJECT_ID(N'dbo.urban_rural_classification_lookup', 'U') IS NOT NULL
    DROP TABLE [dbo].[urban_rural_classification_lookup];
IF OBJECT_ID(N'dbo.public_holidays', 'U') IS NOT NULL
    DROP TABLE [dbo].[public_holidays];
IF OBJECT_ID(N'dbo.chatbot_knowledge_base', 'U') IS NOT NULL
    DROP TABLE [dbo].chatbot_knowledge_base;
GO

-- Create tables in dependency order

CREATE TABLE [dbo].[academic_assessment_type_lookup] (
    [assessment_type_id] INT IDENTITY(1000,1) NOT NULL PRIMARY KEY,
    [assessment_type_name] VARCHAR(50) NOT NULL,
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[access_to_healthcare_lookup] (
    [access_to_healthcare_id] INT IDENTITY(1010,1) NOT NULL PRIMARY KEY,
    [access_to_healthcare_name] VARCHAR(50) NOT NULL,
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[access_to_specialized_programs_lookup] (
    [access_to_specialized_programs_id] INT IDENTITY(1020,1) NOT NULL PRIMARY KEY,
    [access_to_specialized_programs_name] VARCHAR(10) NOT NULL,
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[allocation_category_lookup] (
    [allocation_category_id] INT IDENTITY(1030,1) NOT NULL PRIMARY KEY,
    [allocation_category_name] VARCHAR(50) NOT NULL,
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[attendance_status_lookup] (
    [attendance_status_id] INT IDENTITY(1040,1) NOT NULL PRIMARY KEY,
    [attendance_status_name] VARCHAR(50) NOT NULL,
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[chatbot_knowledge_base] (
    [chatbot_id] INT IDENTITY(900,1) NOT NULL PRIMARY KEY,
    [question_category] NVARCHAR(50) NOT NULL,
    [question] NVARCHAR(300) NOT NULL,
    [answer] VARCHAR(8000) NOT NULL,
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL    
);

GO

CREATE TABLE [dbo].[device_access_lookup] (
    [device_access_id] INT IDENTITY(1050,1) NOT NULL PRIMARY KEY,
    [device_access_name] VARCHAR(50) NOT NULL,
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[digital_literacy_lookup] (
    [digital_literacy_id] INT IDENTITY(1060,1) NOT NULL PRIMARY KEY,
    [digital_literacy_name] VARCHAR(50) NOT NULL,
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[digital_literacy_support_lookup] (
    [digital_literacy_support_id] INT IDENTITY(1080,1) NOT NULL PRIMARY KEY,
    [digital_literacy_support_name] VARCHAR(50) NOT NULL,
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[disability_status_lookup] (
    [disability_status_id] INT IDENTITY(1090,1) NOT NULL PRIMARY KEY,
    [disability_status_name] VARCHAR(50) NOT NULL,
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[disciplinary_incidents_lookup] (
    [disciplinary_incidents_id] INT IDENTITY(100000,1) NOT NULL PRIMARY KEY,
    [disciplinary_incidents_name] VARCHAR(50) NOT NULL,
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[dropout_reason_lookup] (
    [dropout_reason_id] INT IDENTITY(1100,1) NOT NULL PRIMARY KEY,
    [dropout_reason_name] VARCHAR(100) NOT NULL,
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[engagement_level_lookup] (
    [engagement_level_id] INT IDENTITY(1110,1) NOT NULL PRIMARY KEY,
    [engagement_level_name] VARCHAR(50) NOT NULL,
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[extracurricular_activity_type_lookup] (
    [activity_type_id] INT IDENTITY(1120,1) NOT NULL PRIMARY KEY,
    [activity_type_name] VARCHAR(50) NOT NULL,
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[extracurricular_role_lookup] (
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL,
    [role_id] INT IDENTITY(1130,1) NOT NULL PRIMARY KEY,
    [role_name] VARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[funding_model_lookup] (
    [funding_model_id] INT IDENTITY(1140,1) NOT NULL PRIMARY KEY,
    [funding_model_name] VARCHAR(50) NOT NULL,
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[gender_lookup] (
    [gender_id] INT IDENTITY(1150,1) NOT NULL PRIMARY KEY,
    [gender_name] VARCHAR(20) NOT NULL,
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[geographic_density_classification_lookup] (
    [geographic_density_classification_id] INT IDENTITY(1160,1) NOT NULL PRIMARY KEY,
    [geographic_density_classification_name] VARCHAR(50) NOT NULL,
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[health_conditions_lookup] (
    [health_conditions_id] INT IDENTITY(1170,1) NOT NULL PRIMARY KEY,
    [health_conditions_name] VARCHAR(50) NOT NULL,
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[highest_qualification_lookup] (
    [highest_qualification_id] INT IDENTITY(1180,1) NOT NULL PRIMARY KEY,
    [highest_qualification_name] VARCHAR(100) NOT NULL,
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[home_learning_environment_lookup] (
    [home_learning_environment_id] INT IDENTITY(1190,1) NOT NULL PRIMARY KEY,
    [home_learning_environment_name] VARCHAR(50) NOT NULL,
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[internet_access_lookup] (
    [internet_access_id] INT IDENTITY(1200,1) NOT NULL PRIMARY KEY,
    [internet_access_name] VARCHAR(50) NOT NULL,
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[internet_access_quality_lookup] (
    [internet_access_quality_id] INT IDENTITY(1210,1) NOT NULL PRIMARY KEY,
    [internet_access_quality_name] VARCHAR(50) NOT NULL,
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[intervention_outcome_lookup] (
    [intervention_outcome_id] INT IDENTITY(1220,1) NOT NULL PRIMARY KEY,
    [intervention_outcome_name] VARCHAR(50) NOT NULL,
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[intervention_type_lookup] (
    [intervention_type_id] INT IDENTITY(1230,1) NOT NULL PRIMARY KEY,
    [intervention_type_name] VARCHAR(50) NOT NULL,
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[language_lookup] (
    [language_id] INT IDENTITY(1240,1) NOT NULL PRIMARY KEY,
    [language_name] VARCHAR(50) NOT NULL,
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[learning_resources_lookup] (
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL,
    [learning_resources_id] INT IDENTITY(1300,1) NOT NULL PRIMARY KEY,
    [learning_resources_name] VARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[local_municipality_lookup] (
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL,
    [local_municipality_id] INT IDENTITY(1400,1) NOT NULL PRIMARY KEY,
    [local_municipality_name] VARCHAR(100) NOT NULL
);

GO

CREATE TABLE [dbo].[mental_health_support_lookup] (
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL,
    [mental_health_support_id] INT IDENTITY(13310,1) NOT NULL PRIMARY KEY,
    [mental_health_support_name] VARCHAR(100) NOT NULL
);

GO

CREATE TABLE [dbo].[nutrition_status_lookup] (
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL,
    [nutrition_status_id] INT IDENTITY(1340,1) NOT NULL PRIMARY KEY,
    [nutrition_status_name] VARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[parental_education_level_lookup] (
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL,
    [parental_education_level_id] INT IDENTITY(1350,1) NOT NULL PRIMARY KEY,
    [parental_education_level_name] VARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[parental_employment_status_lookup] (
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL,
    [parental_employment_status_id] INT IDENTITY(1360,1) NOT NULL PRIMARY KEY,
    [parental_employment_status_name] VARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[parental_marital_status_lookup] (
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL,
    [parental_marital_status_id] INT IDENTITY(1370,1) NOT NULL PRIMARY KEY,
    [parental_marital_status_name] VARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[parental_tech_support_lookup] (
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL,
    [parental_tech_support_id] INT IDENTITY(1380,1) NOT NULL PRIMARY KEY,
    [parental_tech_support_name] VARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[parents] (
    [address] VARCHAR(MAX) NULL,
    [city] VARCHAR(MAX) NULL,
    [email] VARCHAR(MAX) NULL,
    [firstname] VARCHAR(MAX) NULL,
    [lastname] VARCHAR(MAX) NULL,
    [parentid] INT IDENTITY(300000,1) NOT NULL PRIMARY KEY,
    [phonenumber] VARCHAR(MAX) NULL,
    [state] VARCHAR(MAX) NULL,
    [zipcode] VARCHAR(MAX) NULL,
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[provinces] (
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL,
    [province_name] NVARCHAR(100) NOT NULL,
    [provinceid] INT IDENTITY(2000,1) NOT NULL PRIMARY KEY
);

GO

CREATE TABLE [dbo].[psychological_assessment_type_lookup] (
    [assessment_type_id] INT IDENTITY(3000,1) NOT NULL PRIMARY KEY,
    [assessment_type_name] VARCHAR(50) NOT NULL,
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL
);

GO

CREATE TABLE public_holidays (
    [public_holiday_id] INT IDENTITY(8000,1) NOT NULL PRIMARY KEY,
    [from_date] DATE,
    [to_date] DATE,
    [duration_days] INT,
    [holiday_name] NVARCHAR(255),
    [holiday_type] NVARCHAR(255),
    [comments] NVARCHAR(MAX),
    last_update_date DATETIME DEFAULT GETDATE(),
    last_update_userid NVARCHAR(50) DEFAULT 'sysgen'
);

GO

CREATE TABLE [dbo].[race_lookup] (
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL,
    [race_id] INT IDENTITY(3010,1) NOT NULL PRIMARY KEY,
    [race_name] VARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[school_infrastructure_lookup] (
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL,
    [school_infrastructure_id] INT IDENTITY(3030,1) NOT NULL PRIMARY KEY,
    [school_infrastructure_name] VARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[school_phase_lookup] (
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL,
    [school_phase_id] INT IDENTITY(3040,1) NOT NULL PRIMARY KEY,
    [school_phase_name] VARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[school_prototype_size_lookup] (
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL,
    [school_prototype_size_id] INT IDENTITY(3050,1) NOT NULL PRIMARY KEY,
    [school_prototype_size_name] VARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[school_safety_perception_lookup] (
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL,
    [school_safety_perception_id] INT IDENTITY(3070,1) NOT NULL PRIMARY KEY,
    [school_safety_perception_name] VARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[school_specialization_lookup] (
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL,
    [school_specialization_id] INT IDENTITY(3090,1) NOT NULL PRIMARY KEY,
    [school_specialization_name] VARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[school_status_lookup] (
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL,
    [school_status_id] INT IDENTITY(3100,1) NOT NULL PRIMARY KEY,
    [school_status_name] VARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[school_type_lookup] (
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL,
    [school_type_id] INT IDENTITY(3110,1) NOT NULL PRIMARY KEY,
    [school_type_name] VARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[schools] (
    [addressline1] VARCHAR(MAX) NULL,
    [addressline2] VARCHAR(MAX) NULL,
    [city] VARCHAR(MAX) NULL,
    [contactemail] VARCHAR(MAX) NULL,
    [contactphone] VARCHAR(MAX) NULL,
    [postalcode] VARCHAR(MAX) NULL,
    [schoolid] BIGINT IDENTITY(400000,1) NOT NULL PRIMARY KEY,
    [schoolname] VARCHAR(MAX) NULL,
    [schooltype] VARCHAR(MAX) NULL,
	[quintile] int NOT NULL,
	[infrastructurescore] int NOT NULL,
	[teacherabsenteeismrate] decimal(17, 15) NOT NULL,
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL,
    [stateprovince] VARCHAR(MAX) NULL
);

GO

CREATE TABLE [dbo].[social_grants_lookup] (
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL,
    [social_grants_id] INT IDENTITY(3600,1) NOT NULL PRIMARY KEY,
    [social_grants_name] VARCHAR(10) NOT NULL
);

GO

CREATE TABLE [dbo].[socioeconomic_classification_lookup] (
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL,
    [socioeconomic_classification_id] INT IDENTITY(3610,1) NOT NULL PRIMARY KEY,
    [socioeconomic_classification_name] VARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[software_platform_access_lookup] (
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL,
    [software_platform_access_id] INT IDENTITY(3620,1) NOT NULL PRIMARY KEY,
    [software_platform_access_name] VARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[students] (
    [addressline1] VARCHAR(MAX) NULL,
    [addressline2] VARCHAR(MAX) NULL,
    [city] VARCHAR(MAX) NULL,
    [dateofbirth] DATE NULL,
    [email] VARCHAR(MAX) NULL,
    [enrollmentdate] DATE NULL,
    [firstname] VARCHAR(MAX) NULL,
    [gender] VARCHAR(MAX) NULL,
    [gradelevel] BIGINT NULL,
    [lastname] VARCHAR(MAX) NULL,
    [parentid1] INT NULL,
    [parentid2] INT NULL,
    [phonenumber] VARCHAR(MAX) NULL,
    [postalcode] VARCHAR(MAX) NULL,
    [stateprovince] VARCHAR(MAX) NULL,
    [studentid] NVARCHAR(50) NOT NULL PRIMARY KEY,
    [currentschoolid] BIGINT NOT NULL,
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[study_environment_lookup] (
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL,
    [study_environment_id] INT IDENTITY(3650,1) NOT NULL PRIMARY KEY,
    [study_environment_name] VARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[study_habits_lookup] (
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL,
    [study_habits_id] INT IDENTITY(3800,1) NOT NULL PRIMARY KEY,
    [study_habits_name] VARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[subjects] (
    [subject_description] NVARCHAR(500) NULL,
    [grade_applicable] NVARCHAR(50) NULL,
    [last_update_date] DATETIME NULL,
    [last_update_userid] NVARCHAR(50) NULL,
    [subject_name] NVARCHAR(100) NOT NULL,
    [subject_type] NVARCHAR(50) NULL,
    [subjectid] INT IDENTITY(4000,1) NOT NULL PRIMARY KEY
);

GO

CREATE TABLE [dbo].[teacher_effectiveness_rating_lookup] (
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL,
    [teacher_effectiveness_rating_id] INT IDENTITY(4010,1) NOT NULL PRIMARY KEY,
    [teacher_effectiveness_rating_name] VARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[teacher_student_ratio_lookup] (
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL,
    [teacher_student_ratio_id] INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    [teacher_student_ratio_name] VARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[urban_rural_classification_lookup] (
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL,
    [urban_rural_classification_id] INT IDENTITY(4020,1) NOT NULL PRIMARY KEY,
    [urban_rural_classification_name] VARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[districts] (
    [district_name] NVARCHAR(100) NOT NULL,
    [districtid] INT IDENTITY(4040,1) NOT NULL PRIMARY KEY,
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL,
    [provinceid] INT NOT NULL
);

GO

CREATE TABLE [dbo].[school_staff] (
    [staff_id] VARCHAR(20) NOT NULL PRIMARY KEY,
    [highest_qualification_id] INT NULL,
    [last_update_date] DATETIME NULL,
    [last_update_user_id] VARCHAR(50) NULL,
    [professional_development_hours_annual] INT NULL,
    [school_id] BIGINT NULL,
    [school_role] VARCHAR(50) NULL,
    [subject_taught_id] INT NULL,
    [teacher_effectiveness_rating_id] INT NULL,
    [years_of_experience] INT NULL
);

GO

CREATE TABLE [dbo].[academic_records] (
    [recordid] INT IDENTITY(5000,1) NOT NULL PRIMARY KEY,
    [academicyear] BIGINT NULL,
    [completiondate] DATE NULL,
    [enrollmentdate] DATE NULL,
    [grade] BIGINT NULL,
    [mark] BIGINT NULL,
    [passstatus] VARCHAR(MAX) NULL,
    [schoolid] BIGINT NULL,
    [studentid] NVARCHAR(50) NULL,
    [subjectid] INT NULL,
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[attendance] (
    [attendanceid] INT IDENTITY(1000000,1) NOT NULL PRIMARY KEY,
    [attendancedate] DATE NOT NULL,
    [status] NVARCHAR(50) NOT NULL,
    [studentid] NVARCHAR(50) NOT NULL,
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[extracurricular_activities] (
    [activityid] INT IDENTITY(4100,1) NOT NULL PRIMARY KEY,
    [activityname] NVARCHAR(255) NOT NULL,
    [completiondate] DATE NULL,
    [enrollmentdate] DATE NOT NULL,
    [studentid] NVARCHAR(50) NOT NULL,
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[interventions] (
    [interventionid] INT IDENTITY(4200,1) NOT NULL PRIMARY KEY,
    [description] NVARCHAR(MAX) NULL,
    [interventiondate] DATE NOT NULL,
    [interventiontype] NVARCHAR(255) NOT NULL,
    [studentid] NVARCHAR(50) NOT NULL,
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[psychological_assessments] (
    [assessmentid] INT IDENTITY(4300,1) NOT NULL PRIMARY KEY,
    [assessmentdate] DATE NOT NULL,
    [assessmenttype] NVARCHAR(255) NOT NULL,
    [result] NVARCHAR(MAX) NULL,
    [studentid] NVARCHAR(50) NOT NULL,
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL
);

GO

CREATE TABLE [dbo].[student_years] (
    [studentyearid] INT IDENTITY(4400,1) NOT NULL PRIMARY KEY,
    [academicyear] BIGINT NULL,
    [enrollmentstatus] VARCHAR(MAX) NULL,
    [grade] BIGINT NULL,
    [schoolid] BIGINT NULL,
    [studentid] NVARCHAR(50) NULL,
    [last_update_date] DATETIME NOT NULL,
    [last_update_userid] NVARCHAR(50) NOT NULL
);

GO

-- Add Foreign Key Constraints
ALTER TABLE [dbo].[academic_records] ADD CONSTRAINT [fk_academic_records_studentid_students_studentid]
    FOREIGN KEY ([studentid]) REFERENCES [dbo].[students] ([studentid]);

ALTER TABLE [dbo].[academic_records] ADD CONSTRAINT [fk_academic_records_schoolid_schools_schoolid]
    FOREIGN KEY ([schoolid]) REFERENCES [dbo].[schools] ([schoolid]);

ALTER TABLE [dbo].[academic_records] ADD CONSTRAINT [fk_academic_records_subjectid_subjects_subjectid]
    FOREIGN KEY ([subjectid]) REFERENCES [dbo].[subjects] ([subjectid]);

ALTER TABLE [dbo].[attendance] ADD CONSTRAINT [fk_attendance_studentid_students_studentid]
    FOREIGN KEY ([studentid]) REFERENCES [dbo].[students] ([studentid]);

ALTER TABLE [dbo].[districts] ADD CONSTRAINT [fk_districts_provinceid_provinces_provinceid]
    FOREIGN KEY ([provinceid]) REFERENCES [dbo].[provinces] ([provinceid]);

ALTER TABLE [dbo].[extracurricular_activities] ADD CONSTRAINT [fk_extracurricular_activities_studentid_students_studentid]
    FOREIGN KEY ([studentid]) REFERENCES [dbo].[students] ([studentid]);

ALTER TABLE [dbo].[interventions] ADD CONSTRAINT [fk_interventions_studentid_students_studentid]
    FOREIGN KEY ([studentid]) REFERENCES [dbo].[students] ([studentid]);

ALTER TABLE [dbo].[psychological_assessments] ADD CONSTRAINT [fk_psychological_assessments_studentid_students_studentid]
    FOREIGN KEY ([studentid]) REFERENCES [dbo].[students] ([studentid]);

ALTER TABLE [dbo].[school_staff] ADD CONSTRAINT [fk_school_staff_highest_qualification_id_highest_qualification_lookup_highest_qualification_id]
    FOREIGN KEY ([highest_qualification_id]) REFERENCES [dbo].[highest_qualification_lookup] ([highest_qualification_id]);

ALTER TABLE [dbo].[school_staff] ADD CONSTRAINT [fk_school_staff_teacher_effectiveness_rating_id_teacher_effectiveness_rating_lookup_teacher_effectiveness_rating_id]
    FOREIGN KEY ([teacher_effectiveness_rating_id]) REFERENCES [dbo].[teacher_effectiveness_rating_lookup] ([teacher_effectiveness_rating_id]);

ALTER TABLE [dbo].[school_staff] ADD CONSTRAINT [fk_school_staff_school_id_schools_schoolid]
    FOREIGN KEY ([school_id]) REFERENCES [dbo].[schools] ([schoolid]);

ALTER TABLE [dbo].[school_staff] ADD CONSTRAINT [fk_school_staff_subject_taught_id_subjects_subjectid]
    FOREIGN KEY ([subject_taught_id]) REFERENCES [dbo].[subjects] ([subjectid]);

ALTER TABLE [dbo].[student_years] ADD CONSTRAINT [fk_student_years_studentid_students_studentid]
    FOREIGN KEY ([studentid]) REFERENCES [dbo].[students] ([studentid]);

ALTER TABLE [dbo].[student_years] ADD CONSTRAINT [fk_student_years_schoolid_schools_schoolid]
    FOREIGN KEY ([schoolid]) REFERENCES [dbo].[schools] ([schoolid]);

ALTER TABLE [dbo].[students] ADD CONSTRAINT [fk_students_parentid1_parents_parentid]
    FOREIGN KEY ([parentid1]) REFERENCES [dbo].[parents] ([parentid]);

ALTER TABLE [dbo].[students] ADD CONSTRAINT [fk_students_parentid2_parents_parentid]
    FOREIGN KEY ([parentid2]) REFERENCES [dbo].[parents] ([parentid]);

GO