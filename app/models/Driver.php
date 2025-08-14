<?php
// Driver model

class Driver extends Model {
    protected function getTableName() {
        return 'drivers';
    }
    
    public function __construct() {
        parent::__construct();
    }
    
    // Create a new driver
    public function create($data) {
        $stmt = $this->pdo->prepare("INSERT INTO drivers (user_id, phone_number) VALUES (?, ?)");
        return $stmt->execute([
            $data['user_id'],
            $data['phone_number']
        ]);
    }
    
    // Find driver by user ID
    public function findByUserId($user_id) {
        return $this->findBy('user_id', $user_id);
    }
}