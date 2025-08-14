<?php
// Admin Controller

class AdminController extends Controller {
    private $studentModel;
    private $parentModel;
    private $driverModel;
    private $busModel;
    private $routeModel;
    private $boardingHistoryModel;
    
    public function __construct() {
        parent::__construct();
        $this->studentModel = new Student();
        $this->parentModel = new Parent();
        $this->driverModel = new Driver();
        $this->busModel = new Bus();
        $this->routeModel = new Route();
        $this->boardingHistoryModel = new BoardingHistory();
    }
    
    // Show admin dashboard
    public function dashboard() {
        // Get all students with parent and route information
        $stmt = $this->pdo->query("SELECT s.*, p.phone_number as parent_phone, r.name as route_name FROM students s LEFT JOIN parents p ON s.parent_id = p.id LEFT JOIN routes r ON s.route_id = r.id");
        $students = $stmt->fetchAll();
        
        // Get all parents with user information
        $stmt = $this->pdo->query("SELECT p.*, u.first_name, u.last_name FROM parents p JOIN users u ON p.user_id = u.id");
        $parents = $stmt->fetchAll();
        
        // Get all drivers with user information
        $stmt = $this->pdo->query("SELECT d.*, u.first_name, u.last_name FROM drivers d JOIN users u ON d.user_id = u.id");
        $drivers = $stmt->fetchAll();
        
        // Get all buses with driver information
        $stmt = $this->pdo->query("SELECT b.*, d.phone_number as driver_phone, u.first_name, u.last_name FROM buses b LEFT JOIN drivers d ON b.driver_id = d.id LEFT JOIN users u ON d.user_id = u.id");
        $buses = $stmt->fetchAll();
        
        // Get all routes with bus information
        $stmt = $this->pdo->query("SELECT r.*, b.number_plate FROM routes r LEFT JOIN buses b ON r.bus_id = b.id");
        $routes = $stmt->fetchAll();
        
        // Get boarding history with student and bus information
        $boarding_history = $this->boardingHistoryModel->getAllWithDetails();
        
        $this->render('admin/dashboard.php', [
            'students' => $students,
            'parents' => $parents,
            'drivers' => $drivers,
            'buses' => $buses,
            'routes' => $routes,
            'boarding_history' => $boarding_history
        ]);
    }
}