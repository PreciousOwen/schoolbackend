<?php
// BoardingHistory model

class BoardingHistory extends Model {
    protected function getTableName() {
        return 'boarding_history';
    }
    
    public function __construct() {
        parent::__construct();
    }
    
    // Create a new boarding history record
    public function create($data) {
        $stmt = $this->pdo->prepare("INSERT INTO boarding_history (student_id, bus_id, action, gps_location) VALUES (?, ?, ?, ?)");
        return $stmt->execute([
            $data['student_id'],
            $data['bus_id'],
            $data['action'],
            $data['gps_location']
        ]);
    }
    
    // Get all boarding history with student and bus details
    public function getAllWithDetails() {
        $stmt = $this->pdo->query("SELECT bh.*, s.name as student_name, b.number_plate as bus_number_plate FROM boarding_history bh JOIN students s ON bh.student_id = s.id JOIN buses b ON bh.bus_id = b.id ORDER BY bh.timestamp DESC");
        return $stmt->fetchAll();
    }
    
    // Get latest boarding record for a student
    public function getLatestBoarding($student_id) {
        $stmt = $this->pdo->prepare("SELECT * FROM boarding_history WHERE student_id = ? AND action = 'board' ORDER BY timestamp DESC LIMIT 1");
        $stmt->execute([$student_id]);
        return $stmt->fetch();
    }
}