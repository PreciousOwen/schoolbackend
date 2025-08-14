#!/usr/bin/env php
<?php
// Script to run database migrations

// Include the autoloader
require_once __DIR__ . '/../config/bootstrap.php';

echo "Running database migrations...\n";

// Get list of migration files
$migrationsDir = __DIR__ . '/../migrations';
$migrationFiles = glob($migrationsDir . '/*.sql');

// Sort migrations by filename
usort($migrationFiles, function($a, $b) {
    return strcmp(basename($a), basename($b));
});

// Connect to database
try {
    $pdo = Connection::getPDO();
    echo "Connected to database successfully.\n";
} catch (Exception $e) {
    echo "Failed to connect to database: " . $e->getMessage() . "\n";
    exit(1);
}

// Run each migration
foreach ($migrationFiles as $migrationFile) {
    echo "Running migration: " . basename($migrationFile) . "\n";
    
    // Read migration file
    $sql = file_get_contents($migrationFile);
    
    if (empty($sql)) {
        echo "  Skipping empty migration file.\n";
        continue;
    }
    
    // Execute migration
    try {
        $pdo->exec($sql);
        echo "  Migration completed successfully.\n";
    } catch (Exception $e) {
        echo "  Failed to run migration: " . $e->getMessage() . "\n";
        exit(1);
    }
}

echo "All migrations completed successfully.\n";
exit(0);