-- Drop tables if they exist
DROP TABLE IF EXISTS Attendance;
DROP TABLE IF EXISTS AcademicHistory;
DROP TABLE IF EXISTS Students;
DROP TABLE IF EXISTS Parents;
DROP TABLE IF EXISTS Schools;

-- Create Schools table
CREATE TABLE Schools (
    SchoolID INT PRIMARY KEY IDENTITY(1,1),
    SchoolName NVARCHAR(255) NOT NULL,
    Address NVARCHAR(255),
    Capacity INT
);

-- Create Parents table
CREATE TABLE Parents (
    ParentID INT PRIMARY KEY IDENTITY(1,1),
    FirstName NVARCHAR(100),
    LastName NVARCHAR(100),
    Email NVARCHAR(255) UNIQUE
);

-- Create Students table
CREATE TABLE Students (
    StudentID NVARCHAR(50) PRIMARY KEY,
    FirstName NVARCHAR(100),
    LastName NVARCHAR(100),
    SchoolID INT,
    ParentID INT,
    FOREIGN KEY (SchoolID) REFERENCES Schools(SchoolID),
    FOREIGN KEY (ParentID) REFERENCES Parents(ParentID)
);

-- Create AcademicHistory table
CREATE TABLE AcademicHistory (
    HistoryID INT PRIMARY KEY IDENTITY(1,1),
    StudentID NVARCHAR(50),
    Year INT,
    Subject NVARCHAR(100),
    Grade NVARCHAR(2),
    FOREIGN KEY (StudentID) REFERENCES Students(StudentID)
);

-- Create Attendance table
CREATE TABLE Attendance (
    AttendanceID INT PRIMARY KEY IDENTITY(1,1),
    StudentID NVARCHAR(50),
    AttendanceDate DATE,
    Status NVARCHAR(50),
    FOREIGN KEY (StudentID) REFERENCES Students(StudentID)
);
