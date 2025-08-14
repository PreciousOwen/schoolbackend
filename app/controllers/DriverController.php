<?php
// Driver Controller

class DriverController extends Controller {
    private $driverModel;
    private $busModel;
    private $routeModel;
    private $studentModel;
    
    public function __construct() {
        parent::__construct();
        $this->driverModel = new Driver();
        $this->busModel = new Bus();
        $this->routeModel = new Route();
        $this->studentModel = new Student();
    }
    
    // Show driver dashboard
    public function dashboard() {
        $user_id = getCurrentUserId();
        $driver = $this->driverModel->findByUserId($user_id);
        
        if (!$driver) {
            $this->redirect('/auth/choose_role.php');
            return;
        }
        
        // Get bus assigned to this driver
        $bus = $this->busModel->findByDriverId($driver['id']);
        
        // Get route for this bus
        $route = null;
        $students = [];
        if ($bus && $bus['id']) {
            // Get route directly from routes table where bus_id matches
            $route = $this->routeModel->findBy('bus_id', $bus['id']);
            if ($route) {
                $students = $this->routeModel->getStudents($route['id']);
            }
        }
        
        $this->render('driver/dashboard.php', [
            'bus' => $bus,
            'route' => $route,
            'students' => $students
        ]);
    }
    
    // Show driver bus map
    public function busMap() {
        $user_id = getCurrentUserId();
        $driver = $this->driverModel->findByUserId($user_id);
        
        if (!$driver) {
            $this->redirect('/auth/choose_role.php');
            return;
        }
        
        // Get bus assigned to this driver
        $bus = $this->busModel->findByDriverId($driver['id']);
        
        $this->render('driver/bus_map.php', [
            'bus' => $bus
        ]);
    }
    
    // Handle bus location update
    public function updateLocation() {
        if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
            http_response_code(405);
            echo json_encode(['status' => 'error', 'message' => 'Method not allowed']);
            return;
        }
        
        $bus_id = $_POST['bus_id'] ?? null;
        $lat = $_POST['lat'] ?? null;
        $lng = $_POST['lng'] ?? null;
        
        if (!$bus_id || !$lat || !$lng) {
            http_response_code(400);
            echo json_encode(['status' => 'error', 'message' => 'Missing required parameters']);
            return;
        }
        
        try {
            $this->busModel->updateLocation($bus_id, $lat, $lng);
            echo json_encode(['status' => 'success']);
        } catch (Exception $e) {
            http_response_code(500);
            echo json_encode(['status' => 'error', 'message' => 'Failed to update location']);
        }
    }
}