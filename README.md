# School Bus Student Monitoring System

This Django project is designed to monitor students on school buses using RFID cards and GPS tracking. It features role-based dashboards for admins, parents, and drivers, and supports real-time tracking, route management, and reporting.

## Features
- Student check-in/out via RFID
- GPS tracking of buses and route optimization
- Role-based dashboards:
  - **Admin:** View all buses, routes, students, and download reports
  - **Parent:** View their children’s bus and route in real time
  - **Driver:** View assigned route and students
- Student-parent-driver-route relationships
- Admin can register users and download Excel reports

## Setup
1. Create and activate a virtual environment (already set up)
2. Install dependencies:
   ```
pip install -r requirements.txt
   ```
3. Run migrations:
   ```
python manage.py migrate
   ```
4. Create a superuser:
   ```
python manage.py createsuperuser
   ```
5. Start the development server:
   ```
python manage.py runserver
   ```

## Requirements
- Python 3.10+
- Django 5.x

## Next Steps
- Implement models for Student, Parent, Driver, Bus, Route, BoardingHistory
- Set up authentication and permissions for each role
- Integrate RFID and GPS logic
- Build dashboards for each user type
- Add reporting and export features

See `README.txt` for full requirements.
