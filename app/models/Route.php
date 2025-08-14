<?php
// Route model

class Route extends Model {
    protected function getTableName() {
        return 'routes';
    }
    
    public function __construct() {
        parent::__construct();
    }
    
    // Create a new route
    public function create($data) {
        $stmt = $this->pdo->prepare("INSERT INTO routes (name, bus_id, start_location, end_location) VALUES (?, ?, ?, ?)");
        return $stmt->execute([
            $data['name'],
            $data['bus_id'] ?? null,
            $data['start_location'],
            $data['end_location']
        ]);
    }
    
    // Get students on a route
    public function getStudents($route_id) {
        $stmt = $this->pdo->prepare("SELECT s.* FROM students s WHERE s.route_id = ?");
        $stmt->execute([$route_id]);
        return $stmt->fetchAll();
    }
}