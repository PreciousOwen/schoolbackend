<?php
// Authentication Controller

class AuthController extends Controller {
    private $userModel;
    private $parentModel;
    private $driverModel;
    
    public function __construct() {
        parent::__construct();
        $this->userModel = new User();
        $this->parentModel = new Parent();
        $this->driverModel = new Driver();
    }
    
    // Show login form
    public function showLogin() {
        $this->render('auth/login.php');
    }
    
    // Handle login
    public function login() {
        $username = $_POST['username'] ?? '';
        $password = $_POST['password'] ?? '';
        
        if (empty($username) || empty($password)) {
            $this->render('auth/login.php', ['error' => 'Please fill in all fields']);
            return;
        }
        
        // Find user by username
        $user = $this->userModel->findByUsername($username);
        if (!$user) {
            $this->render('auth/login.php', ['error' => 'Invalid credentials']);
            return;
        }
        
        // Verify password
        if (!verifyPassword($password, $user['password'])) {
            $this->render('auth/login.php', ['error' => 'Invalid credentials']);
            return;
        }
        
        // Update last login time
        $this->userModel->updateLastLogin($user['id']);
        
        // Determine user role
        $role = 'unknown';
        if ($user['is_superuser']) {
            $role = 'admin';
        } else {
            // Check if user is a parent
            $parent = $this->parentModel->findByUserId($user['id']);
            if ($parent) {
                $role = 'parent';
            }
            
            // Check if user is a driver
            $driver = $this->driverModel->findByUserId($user['id']);
            if ($driver) {
                $role = 'driver';
            }
        }
        
        // Set user session
        setUserSession($user['id'], $role);
        
        // Redirect based on role
        redirectToDashboard();
    }
    
    // Show choose role page
    public function chooseRole() {
        $this->render('auth/choose_role.php');
    }
    
    // Handle logout
    public function logout() {
        clearUserSession();
        $this->redirect('/auth/login.php');
    }
}