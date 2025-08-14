<?php
// Bus model

class Bus extends Model {
    protected function getTableName() {
        return 'buses';
    }
    
    public function __construct() {
        parent::__construct();
    }
    
    // Create a new bus
    public function create($data) {
        $stmt = $this->pdo->prepare("INSERT INTO buses (number_plate, driver_id, current_latitude, current_longitude) VALUES (?, ?, ?, ?)");
        return $stmt->execute([
            $data['number_plate'],
            $data['driver_id'] ?? null,
            $data['current_latitude'] ?? null,
            $data['current_longitude'] ?? null
        ]);
    }
    
    // Find bus by driver ID
    public function findByDriverId($driver_id) {
        return $this->findBy('driver_id', $driver_id);
    }
    
    // Update bus location
    public function updateLocation($bus_id, $latitude, $longitude) {
        $stmt = $this->pdo->prepare("UPDATE buses SET current_latitude = ?, current_longitude = ? WHERE id = ?");
        return $stmt->execute([$latitude, $longitude, $bus_id]);
    }
}