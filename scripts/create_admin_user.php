#!/usr/bin/env php
<?php
// Script to create a default admin user

// Include the autoloader
require_once __DIR__ . '/../config/bootstrap.php';

echo "Creating default admin user...\n";

// Connect to database
try {
    $pdo = Connection::getPDO();
    echo "Connected to database successfully.\n";
} catch (Exception $e) {
    echo "Failed to connect to database: " . $e->getMessage() . "\n";
    exit(1);
}

// Create default admin user
$username = 'leticiajackson';
$email = 'precioustwaya1@gmail.com';
$password = '12345678';
$firstName = 'Leticia';
$lastName = 'Jackson';

// Hash password (using bcrypt)
$hashedPassword = password_hash($password, PASSWORD_DEFAULT);

// Insert user
try {
    $stmt = $pdo->prepare("INSERT IGNORE INTO users (username, email, password, first_name, last_name, is_superuser, is_staff, is_active) VALUES (?, ?, ?, ?, ?, ?, ?, ?)");
    $stmt->execute([
        $username,
        $email,
        $hashedPassword,
        $firstName,
        $lastName,
        1, // is_superuser
        1, // is_staff
        1  // is_active
    ]);
    
    echo "Admin user created successfully.\n";
} catch (Exception $e) {
    echo "Failed to create admin user: " . $e->getMessage() . "\n";
    exit(1);
}

// Create parent record for admin user
try {
    // Get user ID
    $stmt = $pdo->prepare("SELECT id FROM users WHERE username = ?");
    $stmt->execute([$username]);
    $user = $stmt->fetch();
    
    if ($user) {
        $stmt = $pdo->prepare("INSERT IGNORE INTO parents (user_id, phone_number) VALUES (?, ?)");
        $stmt->execute([$user['id'], '1234567890']);
        echo "Parent record created for admin user.\n";
    }
} catch (Exception $e) {
    echo "Failed to create parent record: " . $e->getMessage() . "\n";
    exit(1);
}

echo "Default admin user setup completed.\n";
exit(0);