-- Database schema for School Bus Monitoring System

-- Users table (replaces Django's auth_user)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL,
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    is_superuser BOOLEAN DEFAULT FALSE,
    is_staff BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    date_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL
);

-- Parents table
CREATE TABLE IF NOT EXISTS parents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    phone_number VARCHAR(20),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Drivers table
CREATE TABLE IF NOT EXISTS drivers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    phone_number VARCHAR(20),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Buses table
CREATE TABLE IF NOT EXISTS buses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    number_plate VARCHAR(20) UNIQUE NOT NULL,
    driver_id INT UNIQUE NULL,
    current_latitude FLOAT NULL,
    current_longitude FLOAT NULL,
    FOREIGN KEY (driver_id) REFERENCES drivers(id) ON DELETE SET NULL
);

-- Routes table
CREATE TABLE IF NOT EXISTS routes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    bus_id INT UNIQUE NULL,
    start_location VARCHAR(255),
    end_location VARCHAR(255),
    FOREIGN KEY (bus_id) REFERENCES buses(id) ON DELETE SET NULL
);

-- Students table
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    rfid VARCHAR(50) UNIQUE NOT NULL,
    parent_id INT NOT NULL,
    route_id INT NULL,
    FOREIGN KEY (parent_id) REFERENCES parents(id) ON DELETE CASCADE,
    FOREIGN KEY (route_id) REFERENCES routes(id) ON DELETE SET NULL
);

-- Boarding History table
CREATE TABLE IF NOT EXISTS boarding_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    bus_id INT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    action ENUM('board', 'alight') NOT NULL,
    gps_location VARCHAR(255),
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (bus_id) REFERENCES buses(id) ON DELETE CASCADE
);

-- Indexes for better performance
CREATE INDEX idx_students_parent ON students(parent_id);
CREATE INDEX idx_students_route ON students(route_id);
CREATE INDEX idx_boarding_student ON boarding_history(student_id);
CREATE INDEX idx_boarding_bus ON boarding_history(bus_id);
CREATE INDEX idx_boarding_timestamp ON boarding_history(timestamp);