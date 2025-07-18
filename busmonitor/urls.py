from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', login_required(views.dashboard), name='dashboard'),
    path('parent/', login_required(views.parent_dashboard), name='parent_dashboard'),
    path('driver/', login_required(views.driver_dashboard), name='driver_dashboard'),
    path('dashboard/', login_required(views.admin_dashboard), name='admin_dashboard'),
    path('dashboard/register-all/', views.admin_register_all, name='admin_register_all'),
    path('dashboard/students/add/', views.student_create, name='student_add'),
    path('dashboard/students/<int:pk>/edit/', views.student_update, name='student_edit'),
    path('dashboard/students/<int:pk>/delete/', views.student_delete, name='student_delete'),
    path('dashboard/parents/add/', views.parent_create, name='parent_add'),
    path('dashboard/parents/<int:pk>/edit/', views.parent_update, name='parent_edit'),
    path('dashboard/parents/<int:pk>/delete/', views.parent_delete, name='parent_delete'),
    path('dashboard/drivers/add/', views.driver_create, name='driver_add'),
    path('dashboard/drivers/<int:pk>/edit/', views.driver_update, name='driver_edit'),
    path('dashboard/drivers/<int:pk>/delete/', views.driver_delete, name='driver_delete'),
    path('dashboard/buses/add/', views.bus_create, name='bus_add'),
    path('dashboard/buses/<int:pk>/edit/', views.bus_update, name='bus_edit'),
    path('dashboard/buses/<int:pk>/delete/', views.bus_delete, name='bus_delete'),
    path('dashboard/routes/add/', views.route_create, name='route_add'),
    path('dashboard/routes/<int:pk>/edit/', views.route_update, name='route_edit'),
    path('dashboard/routes/<int:pk>/delete/', views.route_delete, name='route_delete'),
    path('register/parent/', views.register_parent, name='register_parent'),
    path('register/driver/', views.register_driver, name='register_driver'),
    path('register/student/', views.register_student, name='register_student'),
    path('rfid-scan/', views.rfid_scan, name='rfid_scan'),
    path('export/boarding-history/', views.export_boarding_history, name='export_boarding_history'),
    path('route/<int:route_id>/map/', views.route_map, name='route_map'),
    path('bus/update-location/', views.update_bus_location, name='update_bus_location'),
    path('parent/bus-map/', views.parent_bus_map, name='parent_bus_map'),
    path('driver/bus-map/', views.driver_bus_map, name='driver_bus_map'),
    path('driver/bus-map-redirect/', views.driver_map_redirect, name='driver_map_redirect'),
    path('choose-role/', views.choose_role, name='choose_role'),
    path('login/', auth_views.LoginView.as_view(template_name='busmonitor/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='choose_role'), name='logout'),
    path('admin-login/', views.custom_admin_login, name='custom_admin_login'),
    path('parent/student/<int:student_id>/map/', views.student_map_redirect, name='student_map_redirect'),
]
