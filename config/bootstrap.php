<?php
// Bootstrap file for the application
// This file is included at the beginning of all scripts

// Load environment variables
$envFile = __DIR__ . '/../.env';
if (file_exists($envFile)) {
    $envLines = file($envFile, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    foreach ($envLines as $line) {
        // Skip comments
        if (strpos($line, '#') === 0) {
            continue;
        }
        
        // Split on first equals sign
        $parts = explode('=', $line, 2);
        if (count($parts) === 2) {
            $key = trim($parts[0]);
            $value = trim($parts[1]);
            
            // Remove quotes if present
            if (strpos($value, '"') === 0 && strrpos($value, '"') === strlen($value) - 1) {
                $value = substr($value, 1, -1);
            }
            
            // Set environment variable
            $_ENV[$key] = $value;
        }
    }
}

// Define application paths
define('APP_ROOT', dirname(__DIR__));
define('CONFIG_PATH', APP_ROOT . '/config');
define('APP_PATH', APP_ROOT . '/app');
define('PUBLIC_PATH', APP_ROOT . '/public');
define('TEMPLATES_PATH', APP_ROOT . '/templates');
define('MIGRATIONS_PATH', APP_ROOT . '/migrations');
define('SCRIPTS_PATH', APP_ROOT . '/scripts');

// Include configuration
require_once CONFIG_PATH . '/config.php';

// Include database connection
require_once APP_PATH . '/database/Connection.php';

// Include models
foreach (glob(APP_PATH . '/models/*.php') as $model) {
    require_once $model;
}

// Include controllers
foreach (glob(APP_PATH . '/controllers/*.php') as $controller) {
    require_once $controller;
}

// Include helpers
foreach (glob(APP_PATH . '/helpers/*.php') as $helper) {
    require_once $helper;
}