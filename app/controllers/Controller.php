<?php
// Base Controller class

class Controller {
    protected $pdo;
    
    public function __construct() {
        $this->pdo = Connection::getPDO();
    }
    
    // Render a template
    protected function render($template, $data = []) {
        // Extract data to variables
        extract($data);
        
        // Include the template
        include TEMPLATES_PATH . '/' . $template;
    }
    
    // Redirect to a URL
    protected function redirect($url) {
        header('Location: ' . $url);
        exit();
    }
    
    // Get POST data
    protected function getPostData() {
        return $_POST;
    }
    
    // Get GET data
    protected function getGetData() {
        return $_GET;
    }
    
    // Get JSON data
    protected function getJsonData() {
        $input = file_get_contents('php://input');
        return json_decode($input, true);
    }
    
    // Send JSON response
    protected function sendJson($data, $statusCode = 200) {
        http_response_code($statusCode);
        header('Content-Type: application/json');
        echo json_encode($data);
        exit();
    }
    
    // Show error message
    protected function showError($message) {
        $this->render('error.php', ['error' => $message]);
    }
    
    // Show success message
    protected function showSuccess($message) {
        $this->render('success.php', ['message' => $message]);
    }
}