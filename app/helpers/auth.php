<?php
// Authentication helper functions

// Check if user is logged in
function isLoggedIn() {
    return isset($_SESSION['user_id']);
}

// Get current user ID
function getCurrentUserId() {
    return $_SESSION['user_id'] ?? null;
}

// Get current user role
function getCurrentUserRole() {
    return $_SESSION['role'] ?? 'unknown';
}

// Redirect to login if not authenticated
function requireLogin() {
    if (!isLoggedIn()) {
        header('Location: /auth/login.php');
        exit();
    }
}

// Redirect to dashboard based on role
function redirectToDashboard() {
    $role = getCurrentUserRole();
    switch ($role) {
        case 'admin':
            header('Location: /admin/dashboard.php');
            break;
        case 'parent':
            header('Location: /parent/dashboard.php');
            break;
        case 'driver':
            header('Location: /driver/dashboard.php');
            break;
        default:
            header('Location: /auth/choose_role.php');
            break;
    }
    exit();
}

// Check if user is admin
function isAdmin() {
    return getCurrentUserRole() === 'admin';
}

// Check if user is parent
function isParent() {
    return getCurrentUserRole() === 'parent';
}

// Check if user is driver
function isDriver() {
    return getCurrentUserRole() === 'driver';
}

// Require admin access
function requireAdmin() {
    requireLogin();
    if (!isAdmin()) {
        http_response_code(403);
        die('Access denied. Admins only.');
    }
}

// Require parent access
function requireParent() {
    requireLogin();
    if (!isParent()) {
        http_response_code(403);
        die('Access denied. Parents only.');
    }
}

// Require driver access
function requireDriver() {
    requireLogin();
    if (!isDriver()) {
        http_response_code(403);
        die('Access denied. Drivers only.');
    }
}

// Hash password
function hashPassword($password) {
    return password_hash($password, PASSWORD_DEFAULT);
}

// Verify password
function verifyPassword($password, $hash) {
    return password_verify($password, $hash);
}

// Set user session
function setUserSession($user_id, $role) {
    $_SESSION['user_id'] = $user_id;
    $_SESSION['role'] = $role;
}

// Clear user session
function clearUserSession() {
    unset($_SESSION['user_id']);
    unset($_SESSION['role']);
    session_destroy();
}