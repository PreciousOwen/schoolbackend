<?php
// Parent model

class Parent extends Model {
    protected function getTableName() {
        return 'parents';
    }
    
    public function __construct() {
        parent::__construct();
    }
    
    // Create a new parent
    public function create($data) {
        $stmt = $this->pdo->prepare("INSERT INTO parents (user_id, phone_number) VALUES (?, ?)");
        return $stmt->execute([
            $data['user_id'],
            $data['phone_number']
        ]);
    }
    
    // Find parent by user ID
    public function findByUserId($user_id) {
        return $this->findBy('user_id', $user_id);
    }
    
    // Get children of a parent
    public function getChildren($parent_id) {
        $stmt = $this->pdo->prepare("SELECT * FROM students WHERE parent_id = ?");
        $stmt->execute([$parent_id]);
        return $stmt->fetchAll();
    }
}