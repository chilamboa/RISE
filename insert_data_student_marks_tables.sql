-- Insert sample data into Schools
INSERT INTO Schools (SchoolName, Address, Capacity) VALUES
('Greenwood High', '123 Oak Ave', 1200),
('Riverside Academy', '456 Pine St', 1500);

-- Insert sample data into Parents
INSERT INTO Parents (FirstName, LastName, Email) VALUES
('John', 'Doe', 'john.doe@example.com'),
('Jane', 'Smith', 'jane.smith@example.com');

-- Insert sample data into Students
INSERT INTO Students (StudentID, FirstName, LastName, SchoolID, ParentID) VALUES
('S00001', 'Alice', 'Doe', 1, 1),
('S00002', 'Bob', 'Smith', 2, 2);

-- Insert sample data into AcademicHistory
INSERT INTO AcademicHistory (StudentID, Year, Subject, Grade) VALUES
('S00001', 2023, 'Math', 'A'),
('S00001', 2023, 'Science', 'B'),
('S00002', 2023, 'Math', 'B'),
('S00002', 2023, 'Science', 'C');

-- Insert sample data into Attendance
INSERT INTO Attendance (StudentID, AttendanceDate, Status) VALUES
('S00001', '2023-10-01', 'Present'),
('S00001', '2023-10-02', 'Present'),
('S00002', '2023-10-01', 'Present'),
('S00002', '2023-10-02', 'Absent');
