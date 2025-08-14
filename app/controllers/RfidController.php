<?php
// RFID Controller

class RfidController extends Controller {
    private $studentModel;
    private $busModel;
    private $boardingHistoryModel;
    private $parentModel;
    
    public function __construct() {
        parent::__construct();
        $this->studentModel = new Student();
        $this->busModel = new Bus();
        $this->boardingHistoryModel = new BoardingHistory();
        $this->parentModel = new Parent();
    }
    
    // Handle RFID scan
    public function scan() {
        // Allow both JSON and form data
        $data = [];
        if (isset($_SERVER['CONTENT_TYPE']) && strpos($_SERVER['CONTENT_TYPE'], 'application/json') !== false) {
            $input = file_get_contents('php://input');
            $data = json_decode($input, true);
        } else {
            $data = $_POST;
        }
        
        // Extract required data
        $rfid = $data['rfid'] ?? null;
        $bus_id = $data['bus_id'] ?? null;
        $gps_location = $data['gps_location'] ?? '';
        $action = $data['action'] ?? 'board';
        
        // Validate required fields
        if (!$rfid) {
            $this->sendJson(['status' => 'error', 'message' => 'RFID is required.'], 400);
            return;
        }
        
        if (!$bus_id) {
            $this->sendJson(['status' => 'error', 'message' => 'Bus ID is required.'], 400);
            return;
        }
        
        try {
            // Find student by RFID
            $student = $this->studentModel->findByRfid($rfid);
            if (!$student) {
                $this->sendJson(['status' => 'error', 'message' => 'Student not found.'], 404);
                return;
            }
            
            // Find bus by ID
            $bus = $this->busModel->find($bus_id);
            if (!$bus) {
                $this->sendJson(['status' => 'error', 'message' => 'Bus not found.'], 404);
                return;
            }
            
            // Create boarding history record
            $this->boardingHistoryModel->create([
                'student_id' => $student['id'],
                'bus_id' => $bus['id'],
                'action' => $action,
                'gps_location' => $gps_location
            ]);
            
            // Get parent phone number
            $parent = $this->parentModel->find($student['parent_id']);
            $parent_phone = $parent ? $parent['phone_number'] : '';
            
            // Return success response
            $this->sendJson([
                'student_name' => $student['name'],
                'parent_phone_number' => $parent_phone
            ]);
        } catch (Exception $e) {
            $this->sendJson(['status' => 'error', 'message' => 'An unexpected server error occurred.'], 500);
        }
    }
}