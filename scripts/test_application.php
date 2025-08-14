#!/usr/bin/env php
<?php
// Script to test the PHP application

// Include the autoloader
require_once __DIR__ . '/../config/bootstrap.php';

echo "Testing School Bus Monitoring System - PHP Version\n";
echo "====================================================\n";

// Test database connection
echo "Testing database connection...\n";
try {
    $pdo = Connection::getPDO();
    echo "  ✓ Database connection successful\n";
} catch (Exception $e) {
    echo "  ✗ Database connection failed: " . $e->getMessage() . "\n";
    exit(1);
}

// Test model instantiation
echo "Testing model instantiation...\n";
try {
    $userModel = new User();
    $parentModel = new Parent();
    $driverModel = new Driver();
    $busModel = new Bus();
    $routeModel = new Route();
    $studentModel = new Student();
    $boardingHistoryModel = new BoardingHistory();
    echo "  ✓ All models instantiated successfully\n";
} catch (Exception $e) {
    echo "  ✗ Model instantiation failed: " . $e->getMessage() . "\n";
    exit(1);
}

// Test database tables
echo "Testing database tables...\n";
try {
    $tables = [
        'users', 'parents', 'drivers', 'buses', 'routes', 'students', 'boarding_history'
    ];
    
    foreach ($tables as $table) {
        $stmt = $pdo->prepare("SELECT 1 FROM `$table` LIMIT 1");
        $stmt->execute();
        echo "  ✓ Table `$table` exists and is accessible\n";
    }
} catch (Exception $e) {
    echo "  ✗ Database table test failed: " . $e->getMessage() . "\n";
    exit(1);
}

// Test configuration
echo "Testing configuration...\n";
$configVars = [
    'DB_HOST', 'DB_NAME', 'DB_USER', 'APP_NAME', 'MAP_BASE_URL'
];

foreach ($configVars as $var) {
    if (defined($var)) {
        echo "  ✓ Configuration variable `$var` is defined\n";
    } else {
        echo "  ✗ Configuration variable `$var` is not defined\n";
    }
}

echo "\nAll tests completed successfully!\n";
echo "The application should be ready to run.\n";
exit(0);