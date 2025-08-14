# School Bus Monitoring System - PHP Version

This is a PHP conversion of the original Django School Bus Monitoring System.

## Project Structure

- `public/` - Publicly accessible files (entry point for the application)
- `app/` - Application core (controllers, models, views)
- `config/` - Configuration files
- `migrations/` - Database migration files
- `templates/` - Template files for views
- `scripts/` - Utility scripts for setup and maintenance

## Features

- Admin dashboard for managing students, parents, drivers, buses, and routes
- Parent dashboard for viewing children's information
- Driver dashboard for viewing route information
- RFID scanning functionality for student boarding/unboarding
- Map integration for route visualization
- Authentication system for different user roles

## Requirements

- PHP 8.1 or higher
- MySQL 8.0 or higher
- Apache or Nginx web server
- Composer (optional, for dependency management)

## Installation

### Using Docker (Recommended)

1. Clone the repository:
   ```
   git clone <repository-url>
   cd schoolbus-monitoring-php
   ```

2. Start the application using Docker Compose:
   ```
   docker-compose up -d
   ```

3. Run database migrations:
   ```
   docker-compose exec web php scripts/run_migrations.php
   ```

4. Create default admin user:
   ```
   docker-compose exec web php scripts/create_admin_user.php
   ```

5. Access the application at http://localhost:8081

### Manual Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd schoolbus-monitoring-php
   ```

2. Configure your web server to serve files from the `public/` directory.

3. Create a MySQL database:
   ```
   CREATE DATABASE schoolbus_monitoring;
   ```

4. Update the database configuration in `.env` file:
   ```
   DB_HOST=localhost
   DB_NAME=schoolbus_monitoring
   DB_USER=your_username
   DB_PASSWORD=your_password
   ```

5. Run database migrations:
   ```
   php scripts/run_migrations.php
   ```

6. Create default admin user:
   ```
   php scripts/create_admin_user.php
   ```

7. Access the application through your web server.

## Default Admin Credentials

Username: leetiajackson
Password: 12345678

## Development

To run database migrations:
```
php scripts/run_migrations.php
```

To create a default admin user:
```
php scripts/create_admin_user.php
```

## API Endpoints

- RFID Scan: POST `/rfid-scan`
- Route Map: GET `/route/{id}/map`
- Student Map: GET `/student/{id}/map`
- Driver Map: GET `/driver/map`

## License

This project is licensed under the MIT License.
