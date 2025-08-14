<?php
// Map Controller

class MapController extends Controller {
    private $routeModel;
    private $studentModel;
    private $parentModel;
    private $driverModel;
    private $busModel;
    
    public function __construct() {
        parent::__construct();
        $this->routeModel = new Route();
        $this->studentModel = new Student();
        $this->parentModel = new Parent();
        $this->driverModel = new Driver();
        $this->busModel = new Bus();
    }
    
    // Show route map
    public function routeMap($route_id) {
        $route = $this->routeModel->find($route_id);
        
        if (!$route) {
            http_response_code(404);
            echo "Route not found";
            return;
        }
        
        $origin = urlencode($route['start_location']);
        $destination = urlencode($route['end_location']);
        $map_url = MAP_BASE_URL . "?origin={$origin}&destination={$destination}";
        
        // Redirect to map URL
        header("Location: {$map_url}");
        exit();
    }
    
    // Show student map
    public function studentMap($student_id) {
        $student = $this->studentModel->find($student_id);
        
        if (!$student) {
            http_response_code(404);
            echo "Student not found";
            return;
        }
        
        // Get parent to verify access
        $user_id = getCurrentUserId();
        $parent = $this->parentModel->findByUserId($user_id);
        
        if (!$parent || $parent['id'] != $student['parent_id']) {
            http_response_code(403);
            echo "Access denied";
            return;
        }
        
        // Get latest boarding record with action 'board'
        $boarding = (new BoardingHistory())->getLatestBoarding($student['id']);
        
        if (!$boarding || !$student['route_id']) {
            // Show warning message and redirect to parent dashboard
            // In a real application, you might show a proper warning page
            $this->redirect('/parent/dashboard.php');
            return;
        }
        
        $origin = urlencode($boarding['gps_location']);
        $route = $this->routeModel->find($student['route_id']);
        $destination = urlencode($route['end_location']);
        $map_url = MAP_BASE_URL . "?origin={$origin}&destination={$destination}";
        
        // Redirect to map URL
        header("Location: {$map_url}");
        exit();
    }
    
    // Show driver map
    public function driverMap() {
        $user_id = getCurrentUserId();
        $driver = $this->driverModel->findByUserId($user_id);
        
        if (!$driver) {
            http_response_code(403);
            echo "Access denied";
            return;
        }
        
        $bus = $this->busModel->findByDriverId($driver['id']);
        // Get route directly from routes table where bus_id matches
        $route = $bus ? $this->routeModel->findBy('bus_id', $bus['id']) : null;
        
        if (!$route) {
            // Redirect to driver dashboard
            $this->redirect('/driver/dashboard.php');
            return;
        }
        
        $origin = urlencode($route['start_location']);
        $destination = urlencode($route['end_location']);
        $map_url = MAP_BASE_URL . "?origin={$origin}&destination={$destination}";
        
        // Redirect to map URL
        header("Location: {$map_url}");
        exit();
    }
}