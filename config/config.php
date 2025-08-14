<?php
// Configuration file for the application

// Database configuration
define('DB_HOST', $_ENV['DB_HOST'] ?? 'db');
define('DB_NAME', $_ENV['DB_NAME'] ?? 'schoolbus_monitoring');
define('DB_USER', $_ENV['DB_USER'] ?? 'root');
define('DB_PASS', $_ENV['DB_PASSWORD'] ?? 'root');

// Application configuration
define('APP_NAME', 'School Bus Monitoring System');
define('APP_URL', 'http://localhost:8081');

// Session configuration
define('SESSION_LIFETIME', 3600); // 1 hour

// Security configuration
define('SECRET_KEY', 'your-secret-key-here');

// Map configuration
define('MAP_BASE_URL', 'https://schoolroute.silicon4forge.org');

// Error reporting
error_reporting(E_ALL);
ini_set('display_errors', 1);