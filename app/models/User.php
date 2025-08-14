<?php
// User model

class User extends Model {
    protected function getTableName() {
        return 'users';
    }
    
    public function __construct() {
        parent::__construct();
    }
    
    // Create a new user
    public function create($data) {
        $stmt = $this->pdo->prepare("INSERT INTO users (username, email, password, first_name, last_name, is_superuser) VALUES (?, ?, ?, ?, ?, ?)");
        return $stmt->execute([
            $data['username'],
            $data['email'],
            $data['password'],
            $data['first_name'] ?? '',
            $data['last_name'] ?? '',
            $data['is_superuser'] ?? false
        ]);
    }
    
    // Find user by username
    public function findByUsername($username) {
        return $this->findBy('username', $username);
    }
    
    // Find user by email
    public function findByEmail($email) {
        return $this->findBy('email', $email);
    }
    
    // Update last login time
    public function updateLastLogin($user_id) {
        $stmt = $this->pdo->prepare("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?");
        return $stmt->execute([$user_id]);
    }
}