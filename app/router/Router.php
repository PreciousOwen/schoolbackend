<?php
// Simple router class

class Router {
    private $routes = [];
    
    // Add a route
    public function addRoute($method, $pattern, $callback) {
        $this->routes[] = [
            'method' => $method,
            'pattern' => $pattern,
            'callback' => $callback
        ];
    }
    
    // Add a GET route
    public function get($pattern, $callback) {
        $this->addRoute('GET', $pattern, $callback);
    }
    
    // Add a POST route
    public function post($pattern, $callback) {
        $this->addRoute('POST', $pattern, $callback);
    }
    
    // Resolve the current request
    public function resolve($request_uri, $method) {
        // Remove query string from request URI
        $request_uri = parse_url($request_uri, PHP_URL_PATH);
        
        // Try to match the request to a route
        foreach ($this->routes as $route) {
            if ($route['method'] !== $method) {
                continue;
            }
            
            // Convert route pattern to regex
            $pattern = preg_replace('/\{([^}]+)\}/', '([^/]+)', $route['pattern']);
            $pattern = '#^' . $pattern . '$#';
            
            // Check if the pattern matches
            if (preg_match($pattern, $request_uri, $matches)) {
                // Remove the full match
                array_shift($matches);
                
                // Call the callback with the matched parameters
                return call_user_func_array($route['callback'], $matches);
            }
        }
        
        // No route matched
        return false;
    }
}