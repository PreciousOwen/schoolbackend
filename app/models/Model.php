<?php
// Base Model class

class Model {
    protected $pdo;
    protected $table;
    
    public function __construct() {
        $this->pdo = Connection::getPDO();
        $this->table = $this->getTableName();
    }
    
    // Get the table name (to be implemented by child classes)
    protected function getTableName() {
        return '';
    }
    
    // Find a record by ID
    public function find($id) {
        $stmt = $this->pdo->prepare("SELECT * FROM {$this->table} WHERE id = ?");
        $stmt->execute([$id]);
        return $stmt->fetch();
    }
    
    // Find all records
    public function findAll() {
        $stmt = $this->pdo->query("SELECT * FROM {$this->table}");
        return $stmt->fetchAll();
    }
    
    // Find records by a specific column value
    public function findBy($column, $value) {
        $stmt = $this->pdo->prepare("SELECT * FROM {$this->table} WHERE {$column} = ?");
        $stmt->execute([$value]);
        return $stmt->fetch();
    }
    
    // Find all records by a specific column value
    public function findAllBy($column, $value) {
        $stmt = $this->pdo->prepare("SELECT * FROM {$this->table} WHERE {$column} = ?");
        $stmt->execute([$value]);
        return $stmt->fetchAll();
    }
    
    // Delete a record by ID
    public function delete($id) {
        $stmt = $this->pdo->prepare("DELETE FROM {$this->table} WHERE id = ?");
        return $stmt->execute([$id]);
    }
}