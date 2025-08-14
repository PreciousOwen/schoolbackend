<?php
// Parent Controller

class ParentController extends Controller {
    private $parentModel;
    private $studentModel;
    
    public function __construct() {
        parent::__construct();
        $this->parentModel = new Parent();
        $this->studentModel = new Student();
    }
    
    // Show parent dashboard
    public function dashboard() {
        $user_id = getCurrentUserId();
        $parent = $this->parentModel->findByUserId($user_id);
        
        if (!$parent) {
            $this->redirect('/auth/choose_role.php');
            return;
        }
        
        // Get children of this parent with route information
        $children = $this->parentModel->getChildren($parent['id']);
        
        // Add route information to each child
        for ($i = 0; $i < count($children); $i++) {
            if ($children[$i]['route_id']) {
                $route = (new Route())->find($children[$i]['route_id']);
                $children[$i]['route'] = $route;
            }
        }
        
        $this->render('parent/dashboard.php', [
            'children' => $children
        ]);
    }
    
    // Show parent bus map
    public function busMap() {
        $user_id = getCurrentUserId();
        $parent = $this->parentModel->findByUserId($user_id);
        
        if (!$parent) {
            $this->redirect('/auth/choose_role.php');
            return;
        }
        
        // Get children with their buses
        $children = $this->parentModel->getChildren($parent['id']);
        $buses = [];
        
        foreach ($children as $child) {
            if ($child['route_id']) {
                $route = (new Route())->find($child['route_id']);
                if ($route && $route['bus_id']) {
                    $bus = (new Bus())->find($route['bus_id']);
                    if ($bus) {
                        $buses[] = [
                            'student' => $child,
                            'bus' => $bus
                        ];
                    }
                }
            }
        }
        
        $this->render('parent/bus_map.php', [
            'buses' => $buses
        ]);
    }
}