USE [StudentMarks];
GO

-- Set IDENTITY_INSERT ON for tables where we explicitly provide IDs (for lookup tables)
-- This is generally not needed for tables where IDs are auto-generated and not provided.
-- We will only use this if we need to insert specific IDs for lookup tables.
-- For now, let's assume IDENTITY is handled by the database and we don't insert IDs for IDENTITY columns.

-- Insert data into academic_assessment_type_lookup
INSERT INTO [dbo].[academic_assessment_type_lookup] ([assessment_type_name], [last_update_date], [last_update_userid]) VALUES
('Formative Assessment', GETDATE(), 'SYSGEN'),
('Summative Assessment', GETDATE(), 'SYSGEN'),
('Diagnostic Assessment', GETDATE(), 'SYSGEN'),
('Baseline Assessment', GETDATE(), 'SYSGEN'),
('Continuous Assessment', GETDATE(), 'SYSGEN');
GO

-- Insert data into access_to_healthcare_lookup
INSERT INTO [dbo].[access_to_healthcare_lookup] ([access_to_healthcare_name], [last_update_date], [last_update_userid]) VALUES
('Excellent', GETDATE(), 'SYSGEN'),
('Good', GETDATE(), 'SYSGEN'),
('Fair', GETDATE(), 'SYSGEN'),
('Poor', GETDATE(), 'SYSGEN'),
('Very Poor', GETDATE(), 'SYSGEN');
GO

-- Insert data into access_to_specialized_programs_lookup
INSERT INTO [dbo].[access_to_specialized_programs_lookup] ([access_to_specialized_programs_name], [last_update_date], [last_update_userid]) VALUES
('Yes', GETDATE(), 'SYSGEN'),
('No', GETDATE(), 'SYSGEN');
GO

-- Insert data into allocation_category_lookup (assuming quintile-based categories for SA schools)
INSERT INTO [dbo].[allocation_category_lookup] ([allocation_category_name], [last_update_date], [last_update_userid]) VALUES
('Quintile 1', GETDATE(), 'SYSGEN'),
('Quintile 2', GETDATE(), 'SYSGEN'),
('Quintile 3', GETDATE(), 'SYSGEN'),
('Quintile 4', GETDATE(), 'SYSGEN'),
('Quintile 5', GETDATE(), 'SYSGEN');
GO

-- Insert data into attendance_status_lookup
INSERT INTO [dbo].[attendance_status_lookup] ([attendance_status_name], [last_update_date], [last_update_userid]) VALUES
('Present', GETDATE(), 'SYSGEN'),
('Absent (Excused)', GETDATE(), 'SYSGEN'),
('Absent (Unexcused)', GETDATE(), 'SYSGEN'),
('Late', GETDATE(), 'SYSGEN'),
('Suspended', GETDATE(), 'SYSGEN');
GO

-- Insert data into device_access_lookup
INSERT INTO [dbo].[device_access_lookup] ([device_access_name], [last_update_date], [last_update_userid]) VALUES
('Own Laptop', GETDATE(), 'SYSGEN'),
('Own Smartphone', GETDATE(), 'SYSGEN'),
('Shared Device at Home', GETDATE(), 'SYSGEN'),
('School Provided Device', GETDATE(), 'SYSGEN'),
('No Device Access', GETDATE(), 'SYSGEN');
GO

-- Insert data into digital_literacy_lookup
INSERT INTO [dbo].[digital_literacy_lookup] ([digital_literacy_name], [last_update_date], [last_update_userid]) VALUES
('High', GETDATE(), 'SYSGEN'),
('Medium', GETDATE(), 'SYSGEN'),
('Low', GETDATE(), 'SYSGEN'),
('None', GETDATE(), 'SYSGEN');
GO

-- Insert data into digital_literacy_support_lookup
INSERT INTO [dbo].[digital_literacy_support_lookup] ([digital_literacy_support_name], [last_update_date], [last_update_userid]) VALUES
('Formal Training', GETDATE(), 'SYSGEN'),
('Informal Support', GETDATE(), 'SYSGEN'),
('Self-Taught', GETDATE(), 'SYSGEN'),
('No Support', GETDATE(), 'SYSGEN');
GO

-- Insert data into disability_status_lookup
INSERT INTO [dbo].[disability_status_lookup] ([disability_status_name], [last_update_date], [last_update_userid]) VALUES
('None', GETDATE(), 'SYSGEN'),
('Physical Disability', GETDATE(), 'SYSGEN'),
('Learning Disability', GETDATE(), 'SYSGEN'),
('Sensory Impairment', GETDATE(), 'SYSGEN'),
('Intellectual Disability', GETDATE(), 'SYSGEN'),
('Multiple Disabilities', GETDATE(), 'SYSGEN');
GO

-- Insert data into disciplinary_incidents_lookup
INSERT INTO [dbo].[disciplinary_incidents_lookup] ([disciplinary_incidents_name], [last_update_date], [last_update_userid]) VALUES
('None', GETDATE(), 'SYSGEN'),
('Minor Infraction', GETDATE(), 'SYSGEN'),
('Moderate Infraction', GETDATE(), 'SYSGEN'),
('Serious Infraction', GETDATE(), 'SYSGEN'),
('Expulsion', GETDATE(), 'SYSGEN');
GO

-- Insert data into dropout_reason_lookup
INSERT INTO [dbo].[dropout_reason_lookup] ([dropout_reason_name], [last_update_date], [last_update_userid]) VALUES
('Financial Hardship', GETDATE(), 'SYSGEN'),
('Lack of Interest', GETDATE(), 'SYSGEN'),
('Family Responsibilities', GETDATE(), 'SYSGEN'),
('Poor Academic Performance', GETDATE(), 'SYSGEN'),
('Health Reasons', GETDATE(), 'SYSGEN'),
('Relocation', GETDATE(), 'SYSGEN'),
('Early Marriage/Pregnancy', GETDATE(), 'SYSGEN'),
('Gang Violence/Safety Concerns', GETDATE(), 'SYSGEN'),
('Other', GETDATE(), 'SYSGEN');
GO

-- Insert data into engagement_level_lookup
INSERT INTO [dbo].[engagement_level_lookup] ([engagement_level_name], [last_update_date], [last_update_userid]) VALUES
('Highly Engaged', GETDATE(), 'SYSGEN'),
('Moderately Engaged', GETDATE(), 'SYSGEN'),
('Slightly Engaged', GETDATE(), 'SYSGEN'),
('Disengaged', GETDATE(), 'SYSGEN');
GO

-- Insert data into extracurricular_activity_type_lookup
INSERT INTO [dbo].[extracurricular_activity_type_lookup] ([activity_type_name], [last_update_date], [last_update_userid]) VALUES
('Sports', GETDATE(), 'SYSGEN'),
('Arts & Culture', GETDATE(), 'SYSGEN'),
('Academic Clubs', GETDATE(), 'SYSGEN'),
('Community Service', GETDATE(), 'SYSGEN'),
('Leadership', GETDATE(), 'SYSGEN');
GO

-- Insert data into extracurricular_role_lookup
INSERT INTO [dbo].[extracurricular_role_lookup] ([role_name], [last_update_date], [last_update_userid]) VALUES
('Participant', GETDATE(), 'SYSGEN'),
('Team Captain', GETDATE(), 'SYSGEN'),
('Club Leader', GETDATE(), 'SYSGEN'),
('Committee Member', GETDATE(), 'SYSGEN'),
('Volunteer', GETDATE(), 'SYSGEN');
GO

-- Insert data into funding_model_lookup (e.g., government, private, mixed)
INSERT INTO [dbo].[funding_model_lookup] ([funding_model_name], [last_update_date], [last_update_userid]) VALUES
('Government Funded', GETDATE(), 'SYSGEN'),
('Private Funded', GETDATE(), 'SYSGEN'),
('Mixed Funding', GETDATE(), 'SYSGEN');
GO

-- Insert data into gender_lookup
INSERT INTO [dbo].[gender_lookup] ([gender_name], [last_update_date], [last_update_userid]) VALUES
('Male', GETDATE(), 'SYSGEN'),
('Female', GETDATE(), 'SYSGEN'),
('Other', GETDATE(), 'SYSGEN');
GO

-- Insert data into geographic_density_classification_lookup
INSERT INTO [dbo].[geographic_density_classification_lookup] ([geographic_density_classification_name], [last_update_date], [last_update_userid]) VALUES
('Urban', GETDATE(), 'SYSGEN'),
('Peri-Urban', GETDATE(), 'SYSGEN'),
('Rural', GETDATE(), 'SYSGEN');
GO

-- Insert data into health_conditions_lookup
INSERT INTO [dbo].[health_conditions_lookup] ([health_conditions_name], [last_update_date], [last_update_userid]) VALUES
('None', GETDATE(), 'SYSGEN'),
('Asthma', GETDATE(), 'SYSGEN'),
('Diabetes', GETDATE(), 'SYSGEN'),
('Epilepsy', GETDATE(), 'SYSGEN'),
('Allergies', GETDATE(), 'SYSGEN'),
('Vision Impairment', GETDATE(), 'SYSGEN'),
('Hearing Impairment', GETDATE(), 'SYSGEN'),
('Chronic Illness', GETDATE(), 'SYSGEN');
GO

-- Insert data into highest_qualification_lookup (for school staff)
INSERT INTO [dbo].[highest_qualification_lookup] ([highest_qualification_name], [last_update_date], [last_update_userid]) VALUES
('Matric', GETDATE(), 'SYSGEN'),
('Diploma', GETDATE(), 'SYSGEN'),
('Bachelor''s Degree', GETDATE(), 'SYSGEN'),
('Honours Degree', GETDATE(), 'SYSGEN'),
('Master''s Degree', GETDATE(), 'SYSGEN'),
('Doctorate', GETDATE(), 'SYSGEN');
GO

-- Insert data into home_learning_environment_lookup
INSERT INTO [dbo].[home_learning_environment_lookup] ([home_learning_environment_name], [last_update_date], [last_update_userid]) VALUES
('Conducive', GETDATE(), 'SYSGEN'),
('Adequate', GETDATE(), 'SYSGEN'),
('Challenging', GETDATE(), 'SYSGEN'),
('Poor', GETDATE(), 'SYSGEN');
GO

-- Insert data into internet_access_lookup
INSERT INTO [dbo].[internet_access_lookup] ([internet_access_name], [last_update_date], [last_update_userid]) VALUES
('Fibre', GETDATE(), 'SYSGEN'),
('ADSL', GETDATE(), 'SYSGEN'),
('Mobile Data', GETDATE(), 'SYSGEN'),
('Community Wi-Fi', GETDATE(), 'SYSGEN'),
('No Access', GETDATE(), 'SYSGEN');
GO

-- Insert data into internet_access_quality_lookup
INSERT INTO [dbo].[internet_access_quality_lookup] ([internet_access_quality_name], [last_update_date], [last_update_userid]) VALUES
('High Speed', GETDATE(), 'SYSGEN'),
('Medium Speed', GETDATE(), 'SYSGEN'),
('Low Speed', GETDATE(), 'SYSGEN'),
('Unreliable', GETDATE(), 'SYSGEN');
GO

-- Insert data into intervention_outcome_lookup
INSERT INTO [dbo].[intervention_outcome_lookup] ([intervention_outcome_name], [last_update_date], [last_update_userid]) VALUES
('Successful', GETDATE(), 'SYSGEN'),
('Partially Successful', GETDATE(), 'SYSGEN'),
('Unsuccessful', GETDATE(), 'SYSGEN'),
('Ongoing', GETDATE(), 'SYSGEN');
GO

-- Insert data into intervention_type_lookup
INSERT INTO [dbo].[intervention_type_lookup] ([intervention_type_name], [last_update_date], [last_update_userid]) VALUES
('Academic Support', GETDATE(), 'SYSGEN'),
('Behavioral Counseling', GETDATE(), 'SYSGEN'),
('Psychological Therapy', GETDATE(), 'SYSGEN'),
('Nutritional Support', GETDATE(), 'SYSGEN'),
('Social Work Intervention', GETDATE(), 'SYSGEN');
GO

-- Insert data into language_lookup (Official languages of South Africa)
INSERT INTO [dbo].[language_lookup] ([language_name], [last_update_date], [last_update_userid]) VALUES
('Afrikaans', GETDATE(), 'SYSGEN'),
('English', GETDATE(), 'SYSGEN'),
('isiNdebele', GETDATE(), 'SYSGEN'),
('isiXhosa', GETDATE(), 'SYSGEN'),
('isiZulu', GETDATE(), 'SYSGEN'),
('Sepedi', GETDATE(), 'SYSGEN'),
('Sesotho', GETDATE(), 'SYSGEN'),
('Setswana', GETDATE(), 'SYSGEN'),
('siSwati', GETDATE(), 'SYSGEN'),
('Tshivenda', GETDATE(), 'SYSGEN'),
('Xitsonga', GETDATE(), 'SYSGEN');
GO

-- Insert data into learning_resources_lookup
INSERT INTO [dbo].[learning_resources_lookup] ([learning_resources_name], [last_update_date], [last_update_userid]) VALUES
('Textbooks', GETDATE(), 'SYSGEN'),
('Online Platforms', GETDATE(), 'SYSGEN'),
('Library Access', GETDATE(), 'SYSGEN'),
('Tutoring Services', GETDATE(), 'SYSGEN'),
('No Resources', GETDATE(), 'SYSGEN');
GO

-- Insert data into local_municipality_lookup (Placeholder, as these are numerous. Will use districts for now)
INSERT INTO [dbo].[local_municipality_lookup] ([local_municipality_name], [last_update_date], [last_update_userid]) VALUES
('Placeholder Municipality A', GETDATE(), 'SYSGEN'),
('Placeholder Municipality B', GETDATE(), 'SYSGEN');
GO

-- Insert data into mental_health_support_lookup
INSERT INTO [dbo].[mental_health_support_lookup] ([mental_health_support_name], [last_update_date], [last_update_userid]) VALUES
('Available at School', GETDATE(), 'SYSGEN'),
('Referred to External Services', GETDATE(), 'SYSGEN'),
('No Access', GETDATE(), 'SYSGEN');
GO

-- Insert data into nutrition_status_lookup
INSERT INTO [dbo].[nutrition_status_lookup] ([nutrition_status_name], [last_update_date], [last_update_userid]) VALUES
('Well-nourished', GETDATE(), 'SYSGEN'),
('At Risk of Malnutrition', GETDATE(), 'SYSGEN'),
('Malnourished', GETDATE(), 'SYSGEN');
GO

-- Insert data into parental_education_level_lookup
INSERT INTO [dbo].[parental_education_level_lookup] ([parental_education_level_name], [last_update_date], [last_update_userid]) VALUES
('No Formal Education', GETDATE(), 'SYSGEN'),
('Primary School', GETDATE(), 'SYSGEN'),
('Some High School', GETDATE(), 'SYSGEN'),
('Matric/Grade 12', GETDATE(), 'SYSGEN'),
('Post-Matric Certificate/Diploma', GETDATE(), 'SYSGEN'),
('Bachelor''s Degree', GETDATE(), 'SYSGEN'),
('Postgraduate Degree', GETDATE(), 'SYSGEN');
GO

-- Insert data into parental_employment_status_lookup
INSERT INTO [dbo].[parental_employment_status_lookup] ([parental_employment_status_name], [last_update_date], [last_update_userid]) VALUES
('Employed Full-time', GETDATE(), 'SYSGEN'),
('Employed Part-time', GETDATE(), 'SYSGEN'),
('Self-Employed', GETDATE(), 'SYSGEN'),
('Unemployed', GETDATE(), 'SYSGEN'),
('Retired', GETDATE(), 'SYSGEN');
GO

-- Insert data into parental_marital_status_lookup
INSERT INTO [dbo].[parental_marital_status_lookup] ([parental_marital_status_name], [last_update_date], [last_update_userid]) VALUES
('Married', GETDATE(), 'SYSGEN'),
('Single', GETDATE(), 'SYSGEN'),
('Divorced', GETDATE(), 'SYSGEN'),
('Widowed', GETDATE(), 'SYSGEN');
GO

-- Insert data into parental_tech_support_lookup
INSERT INTO [dbo].[parental_tech_support_lookup] ([parental_tech_support_name], [last_update_date], [last_update_userid]) VALUES
('High', GETDATE(), 'SYSGEN'),
('Medium', GETDATE(), 'SYSGEN'),
('Low', GETDATE(), 'SYSGEN'),
('None', GETDATE(), 'SYSGEN');
GO

-- Insert data into psychological_assessment_type_lookup
INSERT INTO [dbo].[psychological_assessment_type_lookup] ([assessment_type_name], [last_update_date], [last_update_userid]) VALUES
('Cognitive Assessment', GETDATE(), 'SYSGEN'),
('Emotional Assessment', GETDATE(), 'SYSGEN'),
('Behavioral Assessment', GETDATE(), 'SYSGEN'),
('Developmental Assessment', GETDATE(), 'SYSGEN');
GO

-- Insert data into race_lookup (South African racial classifications)
INSERT INTO [dbo].[race_lookup] ([race_name], [last_update_date], [last_update_userid]) VALUES
('Black African', GETDATE(), 'SYSGEN'),
('Coloured', GETDATE(), 'SYSGEN'),
('Indian', GETDATE(), 'SYSGEN'),
('White', GETDATE(), 'SYSGEN'),
('Other', GETDATE(), 'SYSGEN');
GO

-- Insert data into school_infrastructure_lookup
INSERT INTO [dbo].[school_infrastructure_lookup] ([school_infrastructure_name], [last_update_date], [last_update_userid]) VALUES
('Excellent', GETDATE(), 'SYSGEN'),
('Good', GETDATE(), 'SYSGEN'),
('Adequate', GETDATE(), 'SYSGEN'),
('Poor', GETDATE(), 'SYSGEN'),
('Very Poor', GETDATE(), 'SYSGEN');
GO

-- Insert data into school_phase_lookup (South African school phases)
INSERT INTO [dbo].[school_phase_lookup] ([school_phase_name], [last_update_date], [last_update_userid]) VALUES
('Foundation Phase', GETDATE(), 'SYSGEN'), -- Grades R-3
('Intermediate Phase', GETDATE(), 'SYSGEN'), -- Grades 4-6
('Senior Phase', GETDATE(), 'SYSGEN'), -- Grades 7-9
('FET Phase', GETDATE(), 'SYSGEN'); -- Grades 10-12
GO

-- Insert data into school_prototype_size_lookup
INSERT INTO [dbo].[school_prototype_size_lookup] ([school_prototype_size_name], [last_update_date], [last_update_userid]) VALUES
('Small', GETDATE(), 'SYSGEN'),
('Medium', GETDATE(), 'SYSGEN'),
('Large', GETDATE(), 'SYSGEN'),
('Mega', GETDATE(), 'SYSGEN');
GO

-- Insert data into school_safety_perception_lookup
INSERT INTO [dbo].[school_safety_perception_lookup] ([school_safety_perception_name], [last_update_date], [last_update_userid]) VALUES
('Very Safe', GETDATE(), 'SYSGEN'),
('Safe', GETDATE(), 'SYSGEN'),
('Neutral', GETDATE(), 'SYSGEN'),
('Unsafe', GETDATE(), 'SYSGEN'),
('Very Unsafe', GETDATE(), 'SYSGEN');
GO

-- Insert data into school_specialization_lookup
INSERT INTO [dbo].[school_specialization_lookup] ([school_specialization_name], [last_update_date], [last_update_userid]) VALUES
('General', GETDATE(), 'SYSGEN'),
('Technical', GETDATE(), 'SYSGEN'),
('Agricultural', GETDATE(), 'SYSGEN'),
('Arts', GETDATE(), 'SYSGEN'),
('Sports', GETDATE(), 'SYSGEN'),
('Special Needs', GETDATE(), 'SYSGEN');
GO

-- Insert data into school_status_lookup
INSERT INTO [dbo].[school_status_lookup] ([school_status_name], [last_update_date], [last_update_userid]) VALUES
('Operational', GETDATE(), 'SYSGEN'),
('Under Construction', GETDATE(), 'SYSGEN'),
('Closed', GETDATE(), 'SYSGEN');
GO

-- Insert data into school_type_lookup (Public, Independent/Private)
INSERT INTO [dbo].[school_type_lookup] ([school_type_name], [last_update_date], [last_update_userid]) VALUES
('Public', GETDATE(), 'SYSGEN'),
('Independent', GETDATE(), 'SYSGEN');
GO

-- Insert data into social_grants_lookup
INSERT INTO [dbo].[social_grants_lookup] ([social_grants_name], [last_update_date], [last_update_userid]) VALUES
('CSG', GETDATE(), 'SYSGEN'), -- Child Support Grant
('FCG', GETDATE(), 'SYSGEN'), -- Foster Child Grant
('Disability', GETDATE(), 'SYSGEN'),
('Old Age', GETDATE(), 'SYSGEN'),
('None', GETDATE(), 'SYSGEN');
GO

-- Insert data into socioeconomic_classification_lookup
INSERT INTO [dbo].[socioeconomic_classification_lookup] ([socioeconomic_classification_name], [last_update_date], [last_update_userid]) VALUES
('Low Income', GETDATE(), 'SYSGEN'),
('Lower-Middle Income', GETDATE(), 'SYSGEN'),
('Middle Income', GETDATE(), 'SYSGEN'),
('Upper-Middle Income', GETDATE(), 'SYSGEN'),
('High Income', GETDATE(), 'SYSGEN');
GO

-- Insert data into software_platform_access_lookup
INSERT INTO [dbo].[software_platform_access_lookup] ([software_platform_access_name], [last_update_date], [last_update_userid]) VALUES
('Microsoft Teams', GETDATE(), 'SYSGEN'),
('Google Classroom', GETDATE(), 'SYSGEN'),
('Moodle', GETDATE(), 'SYSGEN'),
('Zoom', GETDATE(), 'SYSGEN'),
('None', GETDATE(), 'SYSGEN');
GO

-- Insert data into study_environment_lookup
INSERT INTO [dbo].[study_environment_lookup] ([study_environment_name], [last_update_date], [last_update_userid]) VALUES
('Quiet Home', GETDATE(), 'SYSGEN'),
('Shared Space Home', GETDATE(), 'SYSGEN'),
('Public Library', GETDATE(), 'SYSGEN'),
('School After-Hours', GETDATE(), 'SYSGEN'),
('Challenging Home', GETDATE(), 'SYSGEN');
GO

-- Insert data into study_habits_lookup
INSERT INTO [dbo].[study_habits_lookup] ([study_habits_name], [last_update_date], [last_update_userid]) VALUES
('Regular & Structured', GETDATE(), 'SYSGEN'),
('Irregular but Effective', GETDATE(), 'SYSGEN'),
('Cramming', GETDATE(), 'SYSGEN'),
('Minimal Study', GETDATE(), 'SYSGEN'),
('No Study Habits', GETDATE(), 'SYSGEN');
GO

-- Insert data into teacher_effectiveness_rating_lookup
INSERT INTO [dbo].[teacher_effectiveness_rating_lookup] ([teacher_effectiveness_rating_name], [last_update_date], [last_update_userid]) VALUES
('Highly Effective', GETDATE(), 'SYSGEN'),
('Effective', GETDATE(), 'SYSGEN'),
('Developing', GETDATE(), 'SYSGEN'),
('Needs Improvement', GETDATE(), 'SYSGEN');
GO

-- Insert data into teacher_student_ratio_lookup
INSERT INTO [dbo].[teacher_student_ratio_lookup] ([teacher_student_ratio_name], [last_update_date], [last_update_userid]) VALUES
('Low (1:10-1:20)', GETDATE(), 'SYSGEN'),
('Medium (1:21-1:35)', GETDATE(), 'SYSGEN'),
('High (1:36-1:50+)', GETDATE(), 'SYSGEN');
GO

-- Insert data into urban_rural_classification_lookup
INSERT INTO [dbo].[urban_rural_classification_lookup] ([urban_rural_classification_name], [last_update_date], [last_update_userid]) VALUES
('Urban', GETDATE(), 'SYSGEN'),
('Rural', GETDATE(), 'SYSGEN'),
('Peri-Urban', GETDATE(), 'SYSGEN');
GO

-- Insert data into provinces (All 9 South African Provinces)
INSERT INTO [dbo].[provinces] ([province_name], [last_update_date], [last_update_userid]) VALUES
('Eastern Cape', GETDATE(), 'SYSGEN'),
('Free State', GETDATE(), 'SYSGEN'),
('Gauteng', GETDATE(), 'SYSGEN'),
('KwaZulu-Natal', GETDATE(), 'SYSGEN'),
('Limpopo', GETDATE(), 'SYSGEN'),
('Mpumalanga', GETDATE(), 'SYSGEN'),
('North West', GETDATE(), 'SYSGEN'),
('Northern Cape', GETDATE(), 'SYSGEN'),
('Western Cape', GETDATE(), 'SYSGEN');
GO

-- Insert data into districts (Educational Districts by Province) - Aiming for 86 total districts
-- Eastern Cape Districts (8 existing + 5 generic = 13)
INSERT INTO [dbo].[districts] ([district_name], [provinceid], [last_update_date], [last_update_userid]) VALUES
('Amathole', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Eastern Cape'), GETDATE(), 'SYSGEN'),
('Buffalo City', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Eastern Cape'), GETDATE(), 'SYSGEN'),
('Chris Hani', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Eastern Cape'), GETDATE(), 'SYSGEN'),
('Nelson Mandela Bay', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Eastern Cape'), GETDATE(), 'SYSGEN'),
('OR Tambo', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Eastern Cape'), GETDATE(), 'SYSGEN'),
('Sarah Baartman', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Eastern Cape'), GETDATE(), 'SYSGEN'),
('Alfred Nzo', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Eastern Cape'), GETDATE(), 'SYSGEN'),
('Joe Gqabi', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Eastern Cape'), GETDATE(), 'SYSGEN'),
('Eastern Cape District 1', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Eastern Cape'), GETDATE(), 'SYSGEN'),
('Eastern Cape District 2', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Eastern Cape'), GETDATE(), 'SYSGEN'),
('Eastern Cape District 3', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Eastern Cape'), GETDATE(), 'SYSGEN'),
('Eastern Cape District 4', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Eastern Cape'), GETDATE(), 'SYSGEN'),
('Eastern Cape District 5', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Eastern Cape'), GETDATE(), 'SYSGEN');
GO

-- Free State Districts (5 existing = 5)
INSERT INTO [dbo].[districts] ([district_name], [provinceid], [last_update_date], [last_update_userid]) VALUES
('Fezile Dabi', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Free State'), GETDATE(), 'SYSGEN'),
('Lejweleputswa', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Free State'), GETDATE(), 'SYSGEN'),
('Motheo', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Free State'), GETDATE(), 'SYSGEN'),
('Thabo Mofutsanyane', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Free State'), GETDATE(), 'SYSGEN'),
('Xhariep', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Free State'), GETDATE(), 'SYSGEN');
GO

-- Gauteng Districts (15 existing + 5 generic = 20)
INSERT INTO [dbo].[districts] ([district_name], [provinceid], [last_update_date], [last_update_userid]) VALUES
('Johannesburg Central', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Gauteng'), GETDATE(), 'SYSGEN'),
('Johannesburg North', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Gauteng'), GETDATE(), 'SYSGEN'),
('Johannesburg West', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Gauteng'), GETDATE(), 'SYSGEN'),
('Johannesburg South', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Gauteng'), GETDATE(), 'SYSGEN'),
('Johannesburg East', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Gauteng'), GETDATE(), 'SYSGEN'),
('Gauteng East', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Gauteng'), GETDATE(), 'SYSGEN'),
('Ekurhuleni South', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Gauteng'), GETDATE(), 'SYSGEN'),
('Ekurhuleni North', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Gauteng'), GETDATE(), 'SYSGEN'),
('Tshwane South', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Gauteng'), GETDATE(), 'SYSGEN'),
('Tshwane North', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Gauteng'), GETDATE(), 'SYSGEN'),
('Tshwane West', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Gauteng'), GETDATE(), 'SYSGEN'),
('Gauteng North', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Gauteng'), GETDATE(), 'SYSGEN'),
('Sedibeng East', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Gauteng'), GETDATE(), 'SYSGEN'),
('Sedibeng West', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Gauteng'), GETDATE(), 'SYSGEN'),
('West Rand', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Gauteng'), GETDATE(), 'SYSGEN'),
('Gauteng District 1', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Gauteng'), GETDATE(), 'SYSGEN'),
('Gauteng District 2', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Gauteng'), GETDATE(), 'SYSGEN'),
('Gauteng District 3', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Gauteng'), GETDATE(), 'SYSGEN'),
('Gauteng District 4', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Gauteng'), GETDATE(), 'SYSGEN'),
('Gauteng District 5', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Gauteng'), GETDATE(), 'SYSGEN');
GO

-- KwaZulu-Natal Districts (11 existing + 5 generic = 16)
INSERT INTO [dbo].[districts] ([district_name], [provinceid], [last_update_date], [last_update_userid]) VALUES
('Amajuba', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'KwaZulu-Natal'), GETDATE(), 'SYSGEN'),
('eThekwini', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'KwaZulu-Natal'), GETDATE(), 'SYSGEN'),
('Harry Gwala', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'KwaZulu-Natal'), GETDATE(), 'SYSGEN'),
('iLembe', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'KwaZulu-Natal'), GETDATE(), 'SYSGEN'),
('King Cetshwayo', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'KwaZulu-Natal'), GETDATE(), 'SYSGEN'),
('Ugu', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'KwaZulu-Natal'), GETDATE(), 'SYSGEN'),
('uMgungundlovu', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'KwaZulu-Natal'), GETDATE(), 'SYSGEN'),
('uMzinyathi', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'KwaZulu-Natal'), GETDATE(), 'SYSGEN'),
('uThukela', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'KwaZulu-Natal'), GETDATE(), 'SYSGEN'),
('Zululand', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'KwaZulu-Natal'), GETDATE(), 'SYSGEN'),
('Umkhanyakude', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'KwaZulu-Natal'), GETDATE(), 'SYSGEN'),
('KZN District 1', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'KwaZulu-Natal'), GETDATE(), 'SYSGEN'),
('KZN District 2', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'KwaZulu-Natal'), GETDATE(), 'SYSGEN'),
('KZN District 3', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'KwaZulu-Natal'), GETDATE(), 'SYSGEN'),
('KZN District 4', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'KwaZulu-Natal'), GETDATE(), 'SYSGEN'),
('KZN District 5', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'KwaZulu-Natal'), GETDATE(), 'SYSGEN');
GO

-- Limpopo Districts (5 existing + 2 generic = 7)
INSERT INTO [dbo].[districts] ([district_name], [provinceid], [last_update_date], [last_update_userid]) VALUES
('Capricorn', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Limpopo'), GETDATE(), 'SYSGEN'),
('Greater Sekhukhune', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Limpopo'), GETDATE(), 'SYSGEN'),
('Mopani', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Limpopo'), GETDATE(), 'SYSGEN'),
('Vhembe', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Limpopo'), GETDATE(), 'SYSGEN'),
('Waterberg', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Limpopo'), GETDATE(), 'SYSGEN'),
('Limpopo District 1', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Limpopo'), GETDATE(), 'SYSGEN'),
('Limpopo District 2', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Limpopo'), GETDATE(), 'SYSGEN');
GO

-- Mpumalanga Districts (4 existing + 1 generic = 5)
INSERT INTO [dbo].[districts] ([district_name], [provinceid], [last_update_date], [last_update_userid]) VALUES
('Ehlanzeni', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Mpumalanga'), GETDATE(), 'SYSGEN'),
('Gert Sibande', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Mpumalanga'), GETDATE(), 'SYSGEN'),
('Nkangala', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Mpumalanga'), GETDATE(), 'SYSGEN'),
('Bohlabela', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Mpumalanga'), GETDATE(), 'SYSGEN'),
('Mpumalanga District 1', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Mpumalanga'), GETDATE(), 'SYSGEN');
GO

-- North West Districts (4 existing + 1 generic = 5)
INSERT INTO [dbo].[districts] ([district_name], [provinceid], [last_update_date], [last_update_userid]) VALUES
('Bojanala Platinum', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'North West'), GETDATE(), 'SYSGEN'),
('Dr Kenneth Kaunda', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'North West'), GETDATE(), 'SYSGEN'),
('Ngaka Modiri Molema', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'North West'), GETDATE(), 'SYSGEN'),
('Dr Ruth Segomotsi Mompati', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'North West'), GETDATE(), 'SYSGEN'),
('North West District 1', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'North West'), GETDATE(), 'SYSGEN');
GO

-- Northern Cape Districts (5 existing + 1 generic = 6)
INSERT INTO [dbo].[districts] ([district_name], [provinceid], [last_update_date], [last_update_userid]) VALUES
('Frances Baard', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Northern Cape'), GETDATE(), 'SYSGEN'),
('John Taolo Gaetsewe', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Northern Cape'), GETDATE(), 'SYSGEN'),
('Namakwa', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Northern Cape'), GETDATE(), 'SYSGEN'),
('Pixley ka Seme', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Northern Cape'), GETDATE(), 'SYSGEN'),
('ZF Mgcawu', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Northern Cape'), GETDATE(), 'SYSGEN'),
('Northern Cape District 1', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Northern Cape'), GETDATE(), 'SYSGEN');
GO

-- Western Cape Districts (9 existing = 9)
INSERT INTO [dbo].[districts] ([district_name], [provinceid], [last_update_date], [last_update_userid]) VALUES
('Cape Winelands', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Western Cape'), GETDATE(), 'SYSGEN'),
('Eden', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Western Cape'), GETDATE(), 'SYSGEN'),
('Central Karoo', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Western Cape'), GETDATE(), 'SYSGEN'),
('Overberg', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Western Cape'), GETDATE(), 'SYSGEN'),
('West Coast', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Western Cape'), GETDATE(), 'SYSGEN'),
('Metro Central', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Western Cape'), GETDATE(), 'SYSGEN'),
('Metro East', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Western Cape'), GETDATE(), 'SYSGEN'),
('Metro North', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Western Cape'), GETDATE(), 'SYSGEN'),
('Metro South', (SELECT provinceid FROM [dbo].[provinces] WHERE province_name = 'Western Cape'), GETDATE(), 'SYSGEN');
GO

-- insert subjects
insert into [dbo].[subjects] (subject_name, subject_type, grade_applicable, subject_description, last_update_date, last_update_userid) values
('afrikaans home language', 'language', '1-12', 'language subject for afrikaans speakers', getdate(), 'sysgen'),
('english home language', 'language', '1-12', 'language subject for english speakers', getdate(), 'sysgen'),
('isizulu home language', 'language', '1-12', 'language subject for isizulu speakers', getdate(), 'sysgen'),
('isixhosa home language', 'language', '1-12', 'language subject for isixhosa speakers', getdate(), 'sysgen'),
('mathematics', 'core', '1-12', 'mathematics subject for all grades', getdate(), 'sysgen'),
('life skills', 'core', '1-6', 'covers personal and social well-being, creative arts, and physical education', getdate(), 'sysgen'),
('natural sciences', 'core', '4-9', 'science subject including biology, physics, and chemistry', getdate(), 'sysgen'),
('social sciences', 'core', '4-9', 'includes history and geography', getdate(), 'sysgen'),
('technology', 'core', '7-9', 'basic technology and engineering concepts', getdate(), 'sysgen'),
('economic and management sciences', 'core', '7-9', 'basic economics and business studies', getdate(), 'sysgen'),
('creative arts', 'core', '7-9', 'includes visual arts, music, drama, and dance', getdate(), 'sysgen'),
('life orientation', 'core', '10-12', 'covers personal development, health, and career guidance', getdate(), 'sysgen'),
('physical sciences', 'elective', '10-12', 'advanced physics and chemistry', getdate(), 'sysgen'),
('life sciences', 'elective', '10-12', 'advanced biology', getdate(), 'sysgen'),
('geography', 'elective', '10-12', 'advanced geography', getdate(), 'sysgen'),
('history', 'elective', '10-12', 'advanced history', getdate(), 'sysgen'),
('accounting', 'elective', '10-12', 'financial accounting principles', getdate(), 'sysgen'),
('business studies', 'elective', '10-12', 'business management and entrepreneurship', getdate(), 'sysgen'),
('economics', 'elective', '10-12', 'economic principles and theories', getdate(), 'sysgen'),
('information technology', 'elective', '10-12', 'programming and computer science', getdate(), 'sysgen'),
('computer applications technology', 'elective', '10-12', 'practical computer applications', getdate(), 'sysgen'),
('tourism', 'elective', '10-12', 'tourism industry and management', getdate(), 'sysgen'),
('engineering graphics and design', 'elective', '10-12', 'technical drawing and design', getdate(), 'sysgen'),
('consumer studies', 'elective', '10-12', 'consumer behavior and home management', getdate(), 'sysgen'),
('hospitality studies', 'elective', '10-12', 'hospitality industry and services', getdate(), 'sysgen'),
('agricultural sciences', 'elective', '10-12', 'agriculture and farming practices', getdate(), 'sysgen'),
('dance studies', 'elective', '10-12', 'theory and practice of dance', getdate(), 'sysgen'),
('design', 'elective', '10-12', 'visual design principles', getdate(), 'sysgen'),
('dramatic arts', 'elective', '10-12', 'theory and practice of drama', getdate(), 'sysgen'),
('music', 'elective', '10-12', 'musical theory and practice', getdate(), 'sysgen'),
('visual arts', 'elective', '10-12', 'theory and practice of visual arts', getdate(), 'sysgen');
go


-- Insert data into public_holidays table
INSERT INTO public_holidays ([from_date], [to_date], [duration_days], [holiday_name], [holiday_type], [comments]) VALUES
('2017-01-01', '2017-01-01', 1, 'New Year''s Day', 'Public Holiday', ''),
('2017-01-02', '2017-01-02', 1, 'New Year''s Day (Observed)', 'Public Holiday', 'In lieu of Jan 01 (Sunday)'),
('2017-03-21', '2017-03-21', 1, 'Human Rights Day', 'Public Holiday', ''),
('2017-03-31', '2017-04-17', 18, 'Term 1 Break', 'School Holiday', 'Easter break'),
('2017-04-14', '2017-04-14', 1, 'Good Friday', 'Public Holiday', ''),
('2017-04-17', '2017-04-17', 1, 'Family Day', 'Public Holiday', ''),
('2017-04-27', '2017-04-27', 1, 'Freedom Day', 'Public Holiday', ''),
('2017-05-01', '2017-05-01', 1, 'Workers'' Day', 'Public Holiday', ''),
('2017-06-16', '2017-06-16', 1, 'Youth Day', 'Public Holiday', ''),
('2017-06-30', '2017-07-24', 25, 'Term 2 Break', 'School Holiday', ''),
('2017-08-09', '2017-08-09', 1, 'National Women''s Day', 'Public Holiday', ''),
('2017-09-24', '2017-09-24', 1, 'Heritage Day', 'Public Holiday', ''),
('2017-09-25', '2017-09-25', 1, 'Heritage Day (Observed)', 'Public Holiday', 'In lieu of Sep 24 (Sunday)'),
('2017-09-29', '2017-10-09', 11, 'Term 3 Break', 'School Holiday', ''),
('2017-12-16', '2017-12-16', 1, 'Day of Reconciliation', 'Public Holiday', ''),
('2017-12-25', '2017-12-25', 1, 'Christmas Day', 'Public Holiday', ''),
('2017-12-26', '2017-12-26', 1, 'Day of Goodwill', 'Public Holiday', ''),
('2017-12-13', '2018-01-09', 28, 'Term 4 Break', 'School Holiday', ''),
('2018-01-01', '2018-01-01', 1, 'New Year''s Day', 'Public Holiday', ''),
('2018-03-21', '2018-03-21', 1, 'Human Rights Day', 'Public Holiday', ''),
('2018-03-29', '2018-04-10', 13, 'Term 1 Break', 'School Holiday', 'Easter break'),
('2018-03-30', '2018-03-30', 1, 'Good Friday', 'Public Holiday', ''),
('2018-04-02', '2018-04-02', 1, 'Family Day', 'Public Holiday', ''),
('2018-04-27', '2018-04-27', 1, 'Freedom Day', 'Public Holiday', ''),
('2018-05-01', '2018-05-01', 1, 'Workers'' Day', 'Public Holiday', ''),
('2018-06-16', '2018-06-16', 1, 'Youth Day', 'Public Holiday', ''),
('2018-06-29', '2018-07-23', 25, 'Term 2 Break', 'School Holiday', ''),
('2018-08-09', '2018-08-09', 1, 'National Women''s Day', 'Public Holiday', ''),
('2018-09-24', '2018-09-24', 1, 'Heritage Day', 'Public Holiday', ''),
('2018-09-28', '2018-10-08', 11, 'Term 3 Break', 'School Holiday', ''),
('2018-12-16', '2018-12-16', 1, 'Day of Reconciliation', 'Public Holiday', ''),
('2018-12-17', '2018-12-17', 1, 'Day of Reconciliation (Observed)', 'Public Holiday', 'In lieu of Dec 16 (Sunday)'),
('2018-12-25', '2018-12-25', 1, 'Christmas Day', 'Public Holiday', ''),
('2018-12-26', '2018-12-26', 1, 'Day of Goodwill', 'Public Holiday', ''),
('2018-12-12', '2019-01-08', 28, 'Term 4 Break', 'School Holiday', ''),
('2019-01-01', '2019-01-01', 1, 'New Year''s Day', 'Public Holiday', ''),
('2019-03-21', '2019-03-21', 1, 'Human Rights Day', 'Public Holiday', ''),
('2019-03-20', '2019-04-02', 14, 'Term 1 Break', 'School Holiday', 'Easter break'),
('2019-04-19', '2019-04-19', 1, 'Good Friday', 'Public Holiday', ''),
('2019-04-22', '2019-04-22', 1, 'Family Day', 'Public Holiday', ''),
('2019-04-27', '2019-04-27', 1, 'Freedom Day', 'Public Holiday', ''),
('2019-05-01', '2019-05-01', 1, 'Workers'' Day', 'Public Holiday', ''),
('2019-06-16', '2019-06-16', 1, 'Youth Day', 'Public Holiday', ''),
('2019-06-17', '2019-06-17', 1, 'Youth Day (Observed)', 'Public Holiday', 'In lieu of Jun 16 (Sunday)'),
('2019-06-28', '2019-07-22', 25, 'Term 2 Break', 'School Holiday', ''),
('2019-08-09', '2019-08-09', 1, 'National Women''s Day', 'Public Holiday', ''),
('2019-09-24', '2019-09-24', 1, 'Heritage Day', 'Public Holiday', ''),
('2019-09-27', '2019-10-07', 11, 'Term 3 Break', 'School Holiday', ''),
('2019-12-16', '2019-12-16', 1, 'Day of Reconciliation', 'Public Holiday', ''),
('2019-12-25', '2019-12-25', 1, 'Christmas Day', 'Public Holiday', ''),
('2019-12-26', '2019-12-26', 1, 'Day of Goodwill', 'Public Holiday', ''),
('2019-12-11', '2020-01-07', 28, 'Term 4 Break', 'School Holiday', ''),
('2020-01-01', '2020-01-01', 1, 'New Year''s Day', 'Public Holiday', ''),
('2020-03-21', '2020-03-21', 1, 'Human Rights Day', 'Public Holiday', ''),
('2020-03-20', '2020-03-31', 12, 'Term 1 Break', 'School Holiday', 'Easter break (extrapolated)'),
('2020-04-10', '2020-04-10', 1, 'Good Friday', 'Public Holiday', ''),
('2020-04-13', '2020-04-13', 1, 'Family Day', 'Public Holiday', ''),
('2020-04-27', '2020-04-27', 1, 'Freedom Day', 'Public Holiday', ''),
('2020-05-01', '2020-05-01', 1, 'Workers'' Day', 'Public Holiday', ''),
('2020-06-16', '2020-06-16', 1, 'Youth Day', 'Public Holiday', ''),
('2020-06-26', '2020-07-20', 25, 'Term 2 Break', 'School Holiday', ''),
('2020-08-09', '2020-08-09', 1, 'National Women''s Day', 'Public Holiday', ''),
('2020-08-10', '2020-08-10', 1, 'National Women''s Day (Observed)', 'Public Holiday', 'In lieu of Aug 09 (Sunday)'),
('2020-09-24', '2020-09-24', 1, 'Heritage Day', 'Public Holiday', ''),
('2020-09-25', '2020-10-05', 11, 'Term 3 Break', 'School Holiday', ''),
('2020-12-16', '2020-12-16', 1, 'Day of Reconciliation', 'Public Holiday', ''),
('2020-12-25', '2020-12-25', 1, 'Christmas Day', 'Public Holiday', ''),
('2020-12-26', '2020-12-26', 1, 'Day of Goodwill', 'Public Holiday', ''),
('2020-12-10', '2021-01-06', 28, 'Term 4 Break', 'School Holiday', ''),
('2021-01-01', '2021-01-01', 1, 'New Year''s Day', 'Public Holiday', ''),
('2021-03-21', '2021-03-21', 1, 'Human Rights Day', 'Public Holiday', ''),
('2021-03-22', '2021-03-22', 1, 'Human Rights Day (Observed)', 'Public Holiday', 'In lieu of Mar 21 (Sunday)'),
('2021-03-26', '2021-04-12', 18, 'Term 1 Break', 'School Holiday', 'Easter break (extrapolated)'),
('2021-04-02', '2021-04-02', 1, 'Good Friday', 'Public Holiday', ''),
('2021-04-05', '2021-04-05', 1, 'Family Day', 'Public Holiday', ''),
('2021-04-27', '2021-04-27', 1, 'Freedom Day', 'Public Holiday', ''),
('2021-05-01', '2021-05-01', 1, 'Workers'' Day', 'Public Holiday', ''),
('2021-06-16', '2021-06-16', 1, 'Youth Day', 'Public Holiday', ''),
('2021-07-02', '2021-07-26', 25, 'Term 2 Break', 'School Holiday', ''),
('2021-08-09', '2021-08-09', 1, 'National Women''s Day', 'Public Holiday', ''),
('2021-09-24', '2021-09-24', 1, 'Heritage Day', 'Public Holiday', ''),
('2021-10-01', '2021-10-11', 11, 'Term 3 Break', 'School Holiday', ''),
('2021-12-16', '2021-12-16', 1, 'Day of Reconciliation', 'Public Holiday', ''),
('2021-12-25', '2021-12-25', 1, 'Christmas Day', 'Public Holiday', ''),
('2021-12-26', '2021-12-26', 1, 'Day of Goodwill', 'Public Holiday', ''),
('2021-12-27', '2021-12-27', 1, 'Day of Goodwill (Observed)', 'Public Holiday', 'In lieu of Dec 26 (Sunday)'),
('2021-12-15', '2022-01-11', 28, 'Term 4 Break', 'School Holiday', ''),
('2022-01-01', '2022-01-01', 1, 'New Year''s Day', 'Public Holiday', ''),
('2022-01-03', '2022-01-03', 1, 'New Year''s Day (Observed)', 'Public Holiday', 'In lieu of Jan 01 (Saturday)'),
('2022-03-21', '2022-03-21', 1, 'Human Rights Day', 'Public Holiday', ''),
('2022-03-25', '2022-04-11', 18, 'Term 1 Break', 'School Holiday', 'Easter break (extrapolated)'),
('2022-04-15', '2022-04-15', 1, 'Good Friday', 'Public Holiday', ''),
('2022-04-18', '2022-04-18', 1, 'Family Day', 'Public Holiday', ''),
('2022-04-27', '2022-04-27', 1, 'Freedom Day', 'Public Holiday', ''),
('2022-05-01', '2022-05-01', 1, 'Workers'' Day', 'Public Holiday', ''),
('2022-05-02', '2022-05-02', 1, 'Workers'' Day (Observed)', 'Public Holiday', 'In lieu of May 01 (Sunday)'),
('2022-06-16', '2022-06-16', 1, 'Youth Day', 'Public Holiday', ''),
('2022-07-01', '2022-07-25', 25, 'Term 2 Break', 'School Holiday', ''),
('2022-08-09', '2022-08-09', 1, 'National Women''s Day', 'Public Holiday', ''),
('2022-09-24', '2022-09-24', 1, 'Heritage Day', 'Public Holiday', ''),
('2022-09-30', '2022-10-10', 11, 'Term 3 Break', 'School Holiday', ''),
('2022-12-16', '2022-12-16', 1, 'Day of Reconciliation', 'Public Holiday', ''),
('2022-12-25', '2022-12-25', 1, 'Christmas Day', 'Public Holiday', ''),
('2022-12-26', '2022-12-26', 1, 'Day of Goodwill', 'Public Holiday', ''),
('2022-12-14', '2023-01-10', 28, 'Term 4 Break', 'School Holiday', ''),
('2023-01-01', '2023-01-01', 1, 'New Year''s Day', 'Public Holiday', ''),
('2023-01-02', '2023-01-02', 1, 'New Year''s Day (Observed)', 'Public Holiday', 'In lieu of Jan 01 (Sunday)'),
('2023-03-21', '2023-03-21', 1, 'Human Rights Day', 'Public Holiday', ''),
('2023-03-24', '2023-04-11', 19, 'Term 1 Break', 'School Holiday', 'Easter break (extrapolated)'),
('2023-04-07', '2023-04-07', 1, 'Good Friday', 'Public Holiday', ''),
('2023-04-10', '2023-04-10', 1, 'Family Day', 'Public Holiday', ''),
('2023-04-27', '2023-04-27', 1, 'Freedom Day', 'Public Holiday', ''),
('2023-05-01', '2023-05-01', 1, 'Workers'' Day', 'Public Holiday', ''),
('2023-06-16', '2023-06-16', 1, 'Youth Day', 'Public Holiday', ''),
('2023-06-30', '2023-07-24', 25, 'Term 2 Break', 'School Holiday', ''),
('2023-08-09', '2023-08-09', 1, 'National Women''s Day', 'Public Holiday', ''),
('2023-09-24', '2023-09-24', 1, 'Heritage Day', 'Public Holiday', ''),
('2023-09-25', '2023-09-25', 1, 'Heritage Day (Observed)', 'Public Holiday', 'In lieu of Sep 24 (Sunday)'),
('2023-09-29', '2023-10-09', 11, 'Term 3 Break', 'School Holiday', ''),
('2023-12-16', '2023-12-16', 1, 'Day of Reconciliation', 'Public Holiday', ''),
('2023-12-25', '2023-12-25', 1, 'Christmas Day', 'Public Holiday', ''),
('2023-12-26', '2023-12-26', 1, 'Day of Goodwill', 'Public Holiday', ''),
('2023-12-13', '2024-01-09', 28, 'Term 4 Break', 'School Holiday', ''),
('2024-01-01', '2024-01-01', 1, 'New Year''s Day', 'Public Holiday', ''),
('2024-03-21', '2024-03-21', 1, 'Human Rights Day', 'Public Holiday', ''),
('2024-03-22', '2024-04-09', 19, 'Term 1 Break', 'School Holiday', 'Easter break (extrapolated)'),
('2024-03-29', '2024-03-29', 1, 'Good Friday', 'Public Holiday', ''),
('2024-04-01', '2024-04-01', 1, 'Family Day', 'Public Holiday', ''),
('2024-04-27', '2024-04-27', 1, 'Freedom Day', 'Public Holiday', ''),
('2024-05-01', '2024-05-01', 1, 'Workers'' Day', 'Public Holiday', ''),
('2024-06-16', '2024-06-16', 1, 'Youth Day', 'Public Holiday', ''),
('2024-06-17', '2024-06-17', 1, 'Youth Day (Observed)', 'Public Holiday', 'In lieu of Jun 16 (Sunday)'),
('2024-06-28', '2024-07-22', 25, 'Term 2 Break', 'School Holiday', ''),
('2024-08-09', '2024-08-09', 1, 'National Women''s Day', 'Public Holiday', ''),
('2024-09-24', '2024-09-24', 1, 'Heritage Day', 'Public Holiday', ''),
('2024-09-27', '2024-10-07', 11, 'Term 3 Break', 'School Holiday', ''),
('2024-12-16', '2024-12-16', 1, 'Day of Reconciliation', 'Public Holiday', ''),
('2024-12-25', '2024-12-25', 1, 'Christmas Day', 'Public Holiday', ''),
('2024-12-26', '2024-12-26', 1, 'Day of Goodwill', 'Public Holiday', ''),
('2024-12-11', '2025-01-07', 28, 'Term 4 Break', 'School Holiday', ''),
('2025-01-01', '2025-01-01', 1, 'New Year''s Day', 'Public Holiday', ''),
('2025-03-21', '2025-03-21', 1, 'Human Rights Day', 'Public Holiday', ''),
('2025-03-28', '2025-04-14', 18, 'Term 1 Break', 'School Holiday', 'Easter break (extrapolated)'),
('2025-04-18', '2025-04-18', 1, 'Good Friday', 'Public Holiday', ''),
('2025-04-21', '2025-04-21', 1, 'Family Day', 'Public Holiday', ''),
('2025-04-27', '2025-04-27', 1, 'Freedom Day', 'Public Holiday', ''),
('2025-04-28', '2025-04-28', 1, 'Freedom Day (Observed)', 'Public Holiday', 'In lieu of Apr 27 (Sunday)'),
('2025-05-01', '2025-05-01', 1, 'Workers'' Day', 'Public Holiday', ''),
('2025-06-16', '2025-06-16', 1, 'Youth Day', 'Public Holiday', ''),
('2025-07-04', '2025-07-28', 25, 'Term 2 Break', 'School Holiday', ''),
('2025-08-09', '2025-08-09', 1, 'National Women''s Day', 'Public Holiday', ''),
('2025-09-24', '2025-09-24', 1, 'Heritage Day', 'Public Holiday', ''),
('2025-10-03', '2025-10-13', 11, 'Term 3 Break', 'School Holiday', ''),
('2025-12-16', '2025-12-16', 1, 'Day of Reconciliation', 'Public Holiday', ''),
('2025-12-25', '2025-12-25', 1, 'Christmas Day', 'Public Holiday', ''),
('2025-12-26', '2025-12-26', 1, 'Day of Goodwill', 'Public Holiday', ''),
('2025-12-17', '2026-01-13', 28, 'Term 4 Break', 'School Holiday', ''),
('2026-01-01', '2026-01-01', 1, 'New Year''s Day', 'Public Holiday', ''),
('2026-03-21', '2026-03-21', 1, 'Human Rights Day', 'Public Holiday', ''),
('2026-03-27', '2026-04-14', 19, 'Term 1 Break', 'School Holiday', 'Easter break (extrapolated)'),
('2026-04-03', '2026-04-03', 1, 'Good Friday', 'Public Holiday', ''),
('2026-04-06', '2026-04-06', 1, 'Family Day', 'Public Holiday', ''),
('2026-04-27', '2026-04-27', 1, 'Freedom Day', 'Public Holiday', ''),
('2026-05-01', '2026-05-01', 1, 'Workers'' Day', 'Public Holiday', ''),
('2026-06-16', '2026-06-16', 1, 'Youth Day', 'Public Holiday', ''),
('2026-07-03', '2026-07-27', 25, 'Term 2 Break', 'School Holiday', ''),
('2026-08-09', '2026-08-09', 1, 'National Women''s Day', 'Public Holiday', ''),
('2026-08-10', '2026-08-10', 1, 'National Women''s Day (Observed)', 'Public Holiday', 'In lieu of Aug 09 (Sunday)'),
('2026-09-24', '2026-09-24', 1, 'Heritage Day', 'Public Holiday', ''),
('2026-10-02', '2026-10-12', 11, 'Term 3 Break', 'School Holiday', ''),
('2026-12-16', '2026-12-16', 1, 'Day of Reconciliation', 'Public Holiday', ''),
('2026-12-25', '2026-12-25', 1, 'Christmas Day', 'Public Holiday', ''),
('2026-12-26', '2026-12-26', 1, 'Day of Goodwill', 'Public Holiday', ''),
('2026-12-16', '2027-01-12', 28, 'Term 4 Break', 'School Holiday', ''),
('2027-01-01', '2027-01-01', 1, 'New Year''s Day', 'Public Holiday', ''),
('2027-03-21', '2027-03-21', 1, 'Human Rights Day', 'Public Holiday', ''),
('2027-03-22', '2027-03-22', 1, 'Human Rights Day (Observed)', 'Public Holiday', 'In lieu of Mar 21 (Sunday)'),
('2027-03-26', '2027-04-12', 18, 'Term 1 Break', 'School Holiday', 'Easter break (extrapolated)'),
('2027-03-26', '2027-03-26', 1, 'Good Friday', 'Public Holiday', ''),
('2027-03-29', '2027-03-29', 1, 'Family Day', 'Public Holiday', ''),
('2027-04-27', '2027-04-27', 1, 'Freedom Day', 'Public Holiday', ''),
('2027-05-01', '2027-05-01', 1, 'Workers'' Day', 'Public Holiday', ''),
('2027-06-16', '2027-06-16', 1, 'Youth Day', 'Public Holiday', ''),
('2027-07-02', '2027-07-26', 25, 'Term 2 Break', 'School Holiday', ''),
('2027-08-09', '2027-08-09', 1, 'National Women''s Day', 'Public Holiday', ''),
('2027-09-24', '2027-09-24', 1, 'Heritage Day', 'Public Holiday', ''),
('2027-10-01', '2027-10-11', 11, 'Term 3 Break', 'School Holiday', ''),
('2027-12-16', '2027-12-16', 1, 'Day of Reconciliation', 'Public Holiday', ''),
('2027-12-25', '2027-12-25', 1, 'Christmas Day', 'Public Holiday', ''),
('2027-12-26', '2027-12-26', 1, 'Day of Goodwill', 'Public Holiday', ''),
('2027-12-27', '2027-12-27', 1, 'Day of Goodwill (Observed)', 'Public Holiday', 'In lieu of Dec 26 (Sunday)'),
('2027-12-15', '2028-01-11', 28, 'Term 4 Break', 'School Holiday', ''),
('2028-01-01', '2028-01-01', 1, 'New Year''s Day', 'Public Holiday', ''),
('2028-01-03', '2028-01-03', 1, 'New Year''s Day (Observed)', 'Public Holiday', 'In lieu of Jan 01 (Saturday)'),
('2028-03-21', '2028-03-21', 1, 'Human Rights Day', 'Public Holiday', ''),
('2028-03-24', '2028-04-10', 18, 'Term 1 Break', 'School Holiday', 'Easter break (extrapolated)'),
('2028-04-14', '2028-04-14', 1, 'Good Friday', 'Public Holiday', ''),
('2028-04-17', '2028-04-17', 1, 'Family Day', 'Public Holiday', ''),
('2028-04-27', '2028-04-27', 1, 'Freedom Day', 'Public Holiday', ''),
('2028-05-01', '2028-05-01', 1, 'Workers'' Day', 'Public Holiday', ''),
('2028-06-16', '2028-06-16', 1, 'Youth Day', 'Public Holiday', ''),
('2028-06-30', '2028-07-24', 25, 'Term 2 Break', 'School Holiday', ''),
('2028-08-09', '2028-08-09', 1, 'National Women''s Day', 'Public Holiday', ''),
('2028-09-24', '2028-09-24', 1, 'Heritage Day', 'Public Holiday', ''),
('2028-09-25', '2028-09-25', 1, 'Heritage Day (Observed)', 'Public Holiday', 'In lieu of Sep 24 (Sunday)'),
('2028-09-29', '2028-10-09', 11, 'Term 3 Break', 'School Holiday', ''),
('2028-12-16', '2028-12-16', 1, 'Day of Reconciliation', 'Public Holiday', ''),
('2028-12-25', '2028-12-25', 1, 'Christmas Day', 'Public Holiday', ''),
('2028-12-26', '2028-12-26', 1, 'Day of Goodwill', 'Public Holiday', ''),
('2028-12-13', '2029-01-09', 28, 'Term 4 Break', 'School Holiday', ''),
('2029-01-01', '2029-01-01', 1, 'New Year''s Day', 'Public Holiday', ''),
('2029-03-21', '2029-03-21', 1, 'Human Rights Day', 'Public Holiday', ''),
('2029-03-23', '2029-04-09', 18, 'Term 1 Break', 'School Holiday', 'Easter break (extrapolated)'),
('2029-03-30', '2029-03-30', 1, 'Good Friday', 'Public Holiday', ''),
('2029-04-02', '2029-04-02', 1, 'Family Day', 'Public Holiday', ''),
('2029-04-27', '2029-04-27', 1, 'Freedom Day', 'Public Holiday', ''),
('2029-05-01', '2029-05-01', 1, 'Workers'' Day', 'Public Holiday', ''),
('2029-06-16', '2029-06-16', 1, 'Youth Day', 'Public Holiday', ''),
('2029-06-29', '2029-07-23', 25, 'Term 2 Break', 'School Holiday', ''),
('2029-08-09', '2029-08-09', 1, 'National Women''s Day', 'Public Holiday', ''),
('2029-09-24', '2029-09-24', 1, 'Heritage Day', 'Public Holiday', ''),
('2029-09-28', '2029-10-08', 11, 'Term 3 Break', 'School Holiday', ''),
('2029-12-16', '2029-12-16', 1, 'Day of Reconciliation', 'Public Holiday', ''),
('2029-12-17', '2029-12-17', 1, 'Day of Reconciliation (Observed)', 'Public Holiday', 'In lieu of Dec 16 (Sunday)'),
('2029-12-25', '2029-12-25', 1, 'Christmas Day', 'Public Holiday', ''),
('2029-12-26', '2029-12-26', 1, 'Day of Goodwill', 'Public Holiday', ''),
('2029-12-12', '2030-01-08', 28, 'Term 4 Break', 'School Holiday', ''),
('2030-01-01', '2030-01-01', 1, 'New Year''s Day', 'Public Holiday', ''),
('2030-03-21', '2030-03-21', 1, 'Human Rights Day', 'Public Holiday', ''),
('2030-03-29', '2030-04-14', 17, 'Term 1 Break', 'School Holiday', 'Easter break (extrapolated)'),
('2030-04-19', '2030-04-19', 1, 'Good Friday', 'Public Holiday', ''),
('2030-04-22', '2030-04-22', 1, 'Family Day', 'Public Holiday', ''),
('2030-04-27', '2030-04-27', 1, 'Freedom Day', 'Public Holiday', ''),
('2030-05-01', '2030-05-01', 1, 'Workers'' Day', 'Public Holiday', ''),
('2030-06-16', '2030-06-16', 1, 'Youth Day', 'Public Holiday', ''),
('2030-06-17', '2030-06-17', 1, 'Youth Day (Observed)', 'Public Holiday', 'In lieu of Jun 16 (Sunday)');

go


INSERT INTO chatbot_knowledge_base (question_category, question, answer, last_update_date, last_update_userid)
VALUES
    ('Model Functionality', 'How does Naledi predict student marks?', 'RISE predicts student marks by leveraging a machine learning model. Here''s a breakdown of the process:

Data Generation and Combination: I first generate and combine various datasets related to students, including academic history, attendance, and other relevant information.

Model Training: A machine learning model,is trained using this comprehensive dataset. This training process involves:

Feature Selection: Identifying relevant columns from the combined dataset (e.g., academic history, attendance records, student demographics) as features.

Target Variable Definition: Setting student marks (which are continuous numerical values) as the target variable that the model needs to predict.

Training Algorithm: An algorithm is used to learn patterns and relationships between the input features and the student marks.

Prediction: Once the model is trained, it can then be used to predict future student marks based on new or unseen student data. The functionality in the application utilizes this trained model to generate predictions.

Evaluation (Implicit): A number of techniques are then used to test for performance during training.', GETDATE(), 'system_import'),
    ('Model Functionality', 'What data does Naledi use to make predictions?', 'RISE uses a comprehensive, combined dataset to make predictions about student marks. This dataset is compiled from various sourcesand includes information related to:

Academic Records: Details about student grades, assessment types, and past performance.

Student Information: Student demographics, enrollment details, and associations with schools.

Parent Information: Data about the parents of the students.

School Information: Details about the schools students attend.

Subject Information: Data related to the subjects students are enrolled in.

Student Years: Information pertaining to the academic years students have completed.

Attendance Records: Data on student attendance.', GETDATE(), 'system_import'),
    ('Model Functionality', 'Can Naledi predict final exam results?', 'The RISE application, which Naledi is part of, uses a number of machine learning models and is trained on comprehensive academic records and other student data. This "student marks" prediction capability is designed to forecast overall student performance, which inherently includes final exam results as a key component of academic assessment.

Important Note: These predictions are based on historical data and patterns. They are merely indicators and it is always strongly encouraged for students to actively engage in their learning, study diligently, and seek help when needed to achieve their full potential.', GETDATE(), 'system_import'),
    ('Model Functionality', 'How accurate are Naledi’s predictions?', 'RISE''s prediction accuracy is quantified using standard machine learning evaluation metrics, calculated when the prediction model is trained. 
Since student marks are continuous numerical values, the following regression metrics are used to assess the model''s performance:

Mean Absolute Error (MAE): This measures the average magnitude of the errors in a set of predictions, without considering their direction.
 It''s the average of the absolute differences between predicted and actual values. A lower MAE indicates higher accuracy.

Mean Squared Error (MSE): This calculates the average of the squares of the errors. It penalizes larger errors more heavily than MAE. A lower MSE indicates higher accuracy.

R-squared (R2 Score): This represents the proportion of the variance in the dependent variable (student marks) that is predictable from the independent variables (input data). 
It ranges from 0 to 1, with 1 indicating that the model perfectly predicts the actual values. A higher R2 score indicates a better fit of the model to the data.

It''s important to note that as Naledi is trained with more and more data, the prediction model''s accuracy is expected to improve. ', GETDATE(), 'system_import'),
    ('Model Functionality', 'Does Naledi consider attendance in predictions?', 'Yes, RISE does consider attendance in its predictions.

Attendance records are part of the comprehensive combined dataset that the machine learning model uses for training. 
By incorporating attendance data, Naledi can utilize this information as a factor when predicting student marks.', GETDATE(), 'system_import'),
    ('Model Functionality', 'Can Naledi identify students at risk of failing?', 'Yes, RISE can identify students at risk of failing.

Since Naledi predicts student marks, the system can leverage these predictions to flag students whose projected performance falls below a predefined passing threshold. 
By analyzing the predicted marks, educators can then identify students who may be at risk and intervene to provide necessary support and resources.', GETDATE(), 'system_import'),
    ('Model Functionality', 'How often should student data be updated?', 'For RISE''s predictions and student evaluation to be most effective and accurate, student data should be updated as often as possible.

Regular and timely updates ensure that the machine learning model has the most current information, which is crucial for:

Accuracy of Predictions: Fresh data helps Naledi''s model capture the latest trends in student performance, attendance, and other relevant factors, leading to more reliable predictions.

Early Identification of At-Risk Students: Frequent updates mean that changes in a student''s performance or attendance that might indicate a risk of failing can be identified much sooner, allowing for timely interventions.

Relevant Insights: The insights provided by Naledi will be more pertinent and actionable if they are based on the student''s current status rather than outdated information.

It is highly encouraged that all relevant stakeholders contribute to keeping the student data updated. 
This includes, but is not limited to, teachers, administrators, and potentially even parents, as their collective input provides a holistic and up-to-date view of each student''s academic journey.', GETDATE(), 'system_import'),
    ('Model Functionality', 'What is the confidence level of Naledi’s predictions?', '', GETDATE(), 'system_import'),
    ('Model Functionality', 'Can Naledi predict performance in specific subjects?', '', GETDATE(), 'system_import'),
    ('Model Functionality', 'How does Naledi handle missing data?', 'RISE handles missing data during the data preparation phase, before the machine learning model is trained. The system is designed to implement imputation strategies to address any gaps in the dataset.

While the specific method (e.g., filling with 0, the mean, or the median) for each data point isn''t explicitly detailed, the process ensures that all necessary information is accounted for to prevent errors and maintain the integrity of the predictive model.', GETDATE(), 'system_import'),
    ('South African Education System', 'What is CAPS?', 'CAPS stands for the National Curriculum and Assessment Policy Statement. It is a single, concise, and comprehensive policy document introduced by the Department of Basic Education (DBE) in South Africa.

This document outlines the curriculum and assessment guidelines for all approved subjects in South African schools, from Grade R to Grade 12. 
CAPS provides detailed guidance for teachers on what to teach, how to teach it, and how to assess learners consistently across the country.

You can find more information about CAPS on the official South African Government website:

What is CAPS? - South African Government (https://www.gov.za/faq/education/what-caps)

Curriculum Assessment Policy Statements (CAPS) - Department of Basic Education (https://www.education.gov.za/Curriculum/CurriculumAssessmentPolicyStatements(CAPS).aspx)', GETDATE(), 'system_import'),
    ('South African Education System', 'What are the ANA assessments?', 'The Annual National Assessments (ANA) were standardized tests introduced by the South African Department of Basic Education (DBE) to 
evaluate the performance of learners in key subjects like Literacy and Numeracy (Foundation Phase) and Language and 
Mathematics (Intermediate and Senior Phases). Here''s a summary of what ANA assessments were about:

Purpose of ANA
To monitor the quality of education in public schools.
To provide diagnostic information to teachers, schools, and education officials.
To help identify learning gaps and improve teaching strategies.
To track progress in learner achievement over time', GETDATE(), 'system_import'),
    ('South African Education System', 'How is student performance measured in SA?', 'Student performance in South Africa is measured through a combination of standardized assessments, school-based evaluations, and national examinations, 
all coordinated by the Department of Basic Education (DBE). Here''s a breakdown of the key methods used in 2025:

1. National Senior Certificate (NSC)
The NSC, commonly known as matric, is the final exam for Grade 12 learners.
It includes subjects like Mathematics, Physical Sciences, Life Sciences, Languages, and more.
Performance is graded and used for university admission, employment, and national statistics.
In 2024, only 51% of learners who started Grade 1 in 2013 completed matric 1.
2. School-Based Assessments (SBAs)
These are continuous assessments conducted by teachers throughout the year.
They include tests, projects, assignments, and oral presentations.
SBAs contribute 25% to 50% of the final mark depending on the grade and subject.
3. Systemic Evaluations
These are national diagnostic tests aimed at measuring literacy and numeracy levels.
They replaced the suspended Annual National Assessments (ANA).
Conducted every three three years to track long-term progress and inform policy 2.
4. Provincial and District Monitoring
Provinces and districts conduct their own assessments to monitor school performance.
These include benchmark tests and moderation of SBAs.
5. Performance Indicators
According to the DBE’s 2025/26 Annual Performance Plan 2, performance is tracked using:

Learner achievement rates in key subjects.
Dropout and repetition rates.
Bachelor’s pass rates (needed for university entry).
Progression rates from one grade to the next.
Challenges Affecting Performance
Overcrowded classrooms and staff shortages in over 70% of schools 3.
Budget constraints leading to reduced infrastructure and educator posts.
Digital divide affecting access to online learning and assessments.', GETDATE(), 'system_import'),
    ('South African Education System', 'What are common challenges in SA public schools?', '1. Infrastructure Deficiencies
Many schools lack basic facilities like proper classrooms, toilets, libraries, and laboratories.
Rural schools are especially affected, with some still using pit latrines despite government efforts to eradicate them.
2. Overcrowded Classrooms
High learner-to-teacher ratios, especially in urban and township schools.
This limits individual attention and affects the quality of teaching.
3. Teacher Shortages and Quality
Shortage of qualified teachers in critical subjects like Maths and Science.
Inconsistent teacher training and professional development.
Absenteeism and low morale among educators due to poor working conditions.
4. Language Barriers
Learners often receive instruction in a language that is not their home language, especially in early grades.
This affects comprehension and academic performance.
5. Socioeconomic Challenges
Poverty, hunger, and lack of access to learning materials at home.
Many learners rely on school feeding schemes for their only daily meal.
6. Curriculum and Assessment Issues
Frequent changes to the curriculum can confuse educators and learners.
Assessments may not always align with learners'' real-world needs or capabilities.
7. Digital Divide
Limited access to technology and internet, especially in rural areas.
This gap became more evident during the COVID-19 pandemic and continues to affect e-learning efforts.
8. Safety and Discipline
Issues with bullying, violence, and drug use in some schools.
Lack of adequate security measures and support staff.', GETDATE(), 'system_import'),
    ('South African Education System', 'How does socioeconomic status affect performance?', '1. Access to Resources
Low-SES learners often lack access to textbooks, stationery, internet, and quiet study spaces.
High-SES learners are more likely to attend well-resourced schools and receive extra tuition or support at home.
2. Nutrition and Health
Poor nutrition affects concentration, memory, and energy levels.
Many learners from low-income families rely on school feeding schemes for their main meal.
3. Parental Support and Education
Parents in low-SES households may have limited education, making it harder to assist with homework or navigate the school system.
High-SES families often provide academic support, enrichment activities, and motivation.
4. School Quality
Low-SES learners are more likely to attend underperforming schools with overcrowded classrooms, fewer qualified teachers, and poor infrastructure.
High-SES learners often attend private or well-funded public schools with better facilities and teaching.
5. Psychological and Social Factors
Learners from disadvantaged backgrounds may face stress, trauma, or instability at home.
This can lead to lower self-esteem, behavioral issues, and absenteeism, all of which affect academic performance.
6. Language and Literacy
SES influences early language development. Children from higher-SES families are exposed to more vocabulary and reading from a young age.
This gap widens over time, especially in reading comprehension and writing skills.
Evidence from South Africa
Studies consistently show that learners from quintile 1–3 schools (serving the poorest communities) perform significantly worse in national assessments than those from quintile 4–5 schools.
The Progress in International Reading Literacy Study (PIRLS) found that South African learners from low-SES backgrounds scored among the lowest globally in reading.', GETDATE(), 'system_import'),
    ('South African Education System', 'What is the pass rate for matric in SA?', '""Real"" Matric Pass Rate
When considering the number of learners who started Grade 1 in 2013, only about 50% actually made it through to pass matric in 2024 2.
This figure accounts for dropouts and those who never reached Grade 12.
Of the 1.22 million learners who began school in 2013, only 614,562 passed matric.
Provincial Highlights (2024)
Free State: 91% (highest in the country)
KwaZulu-Natal: 89.5%
Gauteng: 88.4%
Western Cape: 86.6%
Eastern Cape & Limpopo: 85%
Northern Cape: 84.2%
North West: 87.5%
Mpumalanga: 85% ', GETDATE(), 'system_import'),
    ('South African Education System', 'How do rural schools compare to urban ones?', '1. Infrastructure and Resources
Urban Schools: Generally better equipped with libraries, laboratories, internet access, and modern classrooms.
Rural Schools: Often lack basic infrastructure like electricity, running water, and proper sanitation. Some still use pit latrines 1.
2. Teacher Availability and Quality
Urban: Attract more qualified and experienced teachers due to better living conditions and professional opportunities.
Rural: Struggle with teacher shortages, especially in Maths and Science. Some teachers are underqualified or overburdened, and absenteeism is more common 2.
3. Learning Environment
Urban: Though often overcrowded due to migration from rural areas, urban schools tend to have more structured learning environments.
Rural: Classrooms are frequently overcrowded, and teaching quality can be inconsistent. In some cases, teachers are distracted by side businesses or lack motivation 2.
4. Student Performance
Urban learners consistently outperform rural learners in national and international assessments like TIMSS and PIRLS.
The urban-rural learning gap is largely due to differences in school and family characteristics, including parental education and access to learning materials 3.
5. Access to Technology
Urban: More likely to have access to digital tools and online learning platforms.
Rural: The digital divide is stark, with many learners having no access to computers or internet at home or school.
6. Transportation and Attendance
Urban: Learners usually live closer to schools or have access to public transport.
Rural: Long distances and lack of transport often lead to irregular attendance or dropouts.', GETDATE(), 'system_import'),
    ('South African Education System', 'What is the role of DBE in student assessment?', 'The Department of Basic Education (DBE) in South Africa plays a central role in student assessment, ensuring that evaluations are aligned with national education goals and standards. Here''s a breakdown of its responsibilities and initiatives:

1. Policy and Framework Development
The DBE sets the national curriculum and assessment policies, including the Curriculum and Assessment Policy Statements (CAPS).
It defines learning outcomes, assessment standards, and grading criteria for all subjects and grades 1.
2. National Examinations
The DBE administers the National Senior Certificate (NSC) exams for Grade 12 learners.
It ensures standardization, moderation, and security of exam papers across provinces.
It also oversees marking centers and result verification processes.
3. Systemic Evaluations
Following the suspension of the Annual National Assessments (ANA), the DBE introduced systemic evaluations every three years to monitor literacy and numeracy trends 2.
These are used to diagnose learning gaps and inform policy interventions.
4. School-Based Assessments (SBAs)
The DBE provides guidelines for continuous assessment conducted by teachers.
SBAs contribute significantly to final marks, especially in Grades 10–12.
5. Competency-Based Assessment Initiatives
The DBE is exploring 21st-century competency assessments, focusing on skills like critical thinking, collaboration, and digital literacy 3.
This includes developing learning progressions and making student learning more visible through innovative practices.
6. Monitoring and Reporting
Through its Annual Performance Plans, the DBE tracks learner achievement, dropout rates, and progression statistics 1.
It uses this data to evaluate the effectiveness of teaching strategies and resource allocation.
7. Support and Capacity Building
The DBE trains teachers on assessment practices, moderation, and data use.
It also provides standardized workbooks and lesson plans to support consistent assessment across schools 2.', GETDATE(), 'system_import'),
    ('South African Education System', 'How do teacher qualifications affect student marks?', 'Teacher qualifications have a direct and measurable impact on student performance. Here''s how they influence learner outcomes, especially in the South African context:

1. Subject Knowledge
Teachers with formal qualifications in the subjects they teach (e.g., a degree in Mathematics for math teachers) are more likely to deliver accurate, engaging, and effective lessons.
Learners taught by qualified teachers tend to perform better in standardized assessments and school-based evaluations.
2. Pedagogical Skills
Qualified teachers are trained in instructional strategies, classroom management, and assessment techniques.
This leads to better lesson planning, learner engagement, and differentiated instruction for diverse learning needs.
3. Confidence and Motivation
Teachers with proper training and credentials often feel more confident and motivated, which positively affects their teaching quality.
Learners respond better to teachers who are enthusiastic and well-prepared.
4. Impact on Student Marks
Studies in South Africa show that learners taught by unqualified or underqualified teachers score significantly lower in subjects like Mathematics and Science.
In rural schools, where teacher qualifications are often lower, student marks tend to lag behind urban counterparts.
5. Professional Development
Ongoing training and development help teachers stay updated with curriculum changes, technology integration, and inclusive education practices.
Schools that invest in teacher development often see improved learner outcomes over time.', GETDATE(), 'system_import'),
    ('Data & Analytics', 'What types of data improve prediction accuracy?', 'Several types of data can improve the prediction accuracy of a student marks prediction model, particularly within the South African educational context. These include:

Socio-economic indicators: Factors like eligibility for school nutrition programs or fee exemptions are strong predictors of academic performance and educational risk.

Attendance patterns: Chronic absenteeism or declining attendance over time are crucial indicators.

Performance in foundational subjects: Strong performance in subjects like mathematics and language is highly predictive of overall academic success.

Behavioral records: Where available, data on disciplinary incidents can also contribute to prediction accuracy.

Assessment data: The structure and consistency of assessment data, including School-Based Assessments (SBA) and examination marks, are critical for reliable predictions.

Teacher qualifications and quality: The uneven distribution of qualified teachers, particularly in low-income communities, directly impacts instructional quality and learner outcomes.

Resource allocation per student: Disparities in funding and resources available per learner between different quintile schools (wealthier vs. poorer schools) also play a significant role.

Access to Early Childhood Development (ECD) programs: Uneven access to quality ECD programs can lead to early disadvantages that have long-term implications for cognitive and social development, contributing to persistent learning gaps.

Regional disparities: Challenges in rural and peri-urban areas, such as lack of basic infrastructure, difficulty in recruiting qualified teachers, and socio-economic stressors, influence educational access and quality.

Language of instruction: When learners are taught in a language they do not fully understand, it can impede comprehension and academic progress.

Overcrowded classrooms: Large class sizes negatively impact the quality of education by limiting individualized attention and effective classroom management.', GETDATE(), 'system_import');


go