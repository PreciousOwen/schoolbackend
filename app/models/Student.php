<?php
// Student model

class Student extends Model {
    protected function getTableName() {
        return 'students';
    }
    
    public function __construct() {
        parent::__construct();
    }
    
    // Create a new student
    public function create($data) {
        $stmt = $this->pdo->prepare("INSERT INTO students (name, rfid, parent_id, route_id) VALUES (?, ?, ?, ?)");
        return $stmt->execute([
            $data['name'],
            $data['rfid'],
            $data['parent_id'],
            $data['route_id'] ?? null
        ]);
    }
    
    // Find student by RFID
    public function findByRfid($rfid) {
        return $this->findBy('rfid', $rfid);
    }
    
    // Find student by parent ID
    public function findByParentId($parent_id) {
        return $this->findAllBy('parent_id', $parent_id);
    }
}