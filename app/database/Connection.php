<?php
// Database connection class

class Connection {
    private static $pdo = null;
    
    public static function getPDO() {
        if (self::$pdo === null) {
            try {
                $dsn = 'mysql:host=' . DB_HOST . ';dbname=' . DB_NAME . ';charset=utf8mb4';
                self::$pdo = new PDO($dsn, DB_USER, DB_PASS, [
                    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
                    PDO::ATTR_EMULATE_PREPARES => false,
                ]);
            } catch (PDOException $e) {
                die('Database connection failed: ' . $e->getMessage());
            }
        }
        
        return self::$pdo;
    }
    
    // Prevent cloning of the connection
    private function __clone() {}
    
    // Prevent unserializing of the connection
    private function __wakeup() {}
}