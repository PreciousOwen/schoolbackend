<?php
// Public entry point for the application

// Include the autoloader
require_once '../config/bootstrap.php';

// Start the session
session_start();

// Create router instance
$router = new Router();

// Define routes
$router->get('/', function() {
    if (!isLoggedIn()) {
        header('Location: /auth/login.php');
        exit();
    }
    redirectToDashboard();
});

$router->get('/admin/dashboard', function() {
    requireAdmin();
    require_once APP_PATH . '/controllers/AdminController.php';
    $controller = new AdminController();
    $controller->dashboard();
});

$router->get('/parent/dashboard', function() {
    requireParent();
    require_once APP_PATH . '/controllers/ParentController.php';
    $controller = new ParentController();
    $controller->dashboard();
});

$router->get('/driver/dashboard', function() {
    requireDriver();
    require_once APP_PATH . '/controllers/DriverController.php';
    $controller = new DriverController();
    $controller->dashboard();
});

// Auth routes
$router->get('/auth/login', function() {
    require_once APP_PATH . '/controllers/AuthController.php';
    $controller = new AuthController();
    $controller->showLogin();
});

$router->post('/auth/login', function() {
    require_once APP_PATH . '/controllers/AuthController.php';
    $controller = new AuthController();
    $controller->login();
});

$router->get('/auth/choose-role', function() {
    require_once APP_PATH . '/controllers/AuthController.php';
    $controller = new AuthController();
    $controller->chooseRole();
});

$router->get('/auth/logout', function() {
    require_once APP_PATH . '/controllers/AuthController.php';
    $controller = new AuthController();
    $controller->logout();
});

// RFID scan route
$router->post('/rfid-scan', function() {
    require_once APP_PATH . '/controllers/RfidController.php';
    $controller = new RfidController();
    $controller->scan();
});

// Map routes
$router->get('/route/{id}/map', function($id) {
    require_once APP_PATH . '/controllers/MapController.php';
    $controller = new MapController();
    $controller->routeMap($id);
});

// Resolve the current request
$result = $router->resolve($_SERVER['REQUEST_URI'], $_SERVER['REQUEST_METHOD']);

// If no route matched, show 404
if ($result === false) {
    http_response_code(404);
    echo "Page not found";
}