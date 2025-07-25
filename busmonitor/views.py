from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Student, Parent, Driver, Bus, Route, BoardingHistory
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.http import HttpResponseRedirect
from django import forms
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.http import JsonResponse
import csv
from django.http import HttpResponse

def get_user_role(user):
    if user.is_superuser:
        return 'admin'
    if hasattr(user, 'parent'):
        return 'parent'
    if hasattr(user, 'driver'):
        return 'driver'
    return 'unknown'

@login_required
def dashboard(request):
    role = get_user_role(request.user)
    if role == 'admin':
        return redirect('admin_dashboard')
    elif role == 'parent':
        return redirect('parent_dashboard')
    elif role == 'driver':
        return redirect('driver_dashboard')
    else:
        return render(request, 'busmonitor/unknown_role.html')

@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('dashboard')
    students = Student.objects.select_related('parent', 'route').all()
    buses = Bus.objects.all()
    routes = Route.objects.all()
    boarding_history = BoardingHistory.objects.select_related('student', 'bus').all()
    parents = Parent.objects.select_related('user').all()
    drivers = Driver.objects.select_related('user').all()
    return render(request, 'busmonitor/admin_dashboard.html', {
        'students': students,
        'buses': buses,
        'routes': routes,
        'boarding_history': boarding_history,
        'parents': parents,
        'drivers': drivers,
    })

@login_required
def parent_dashboard(request):
    parent = getattr(request.user, 'parent', None)
    if not parent:
        return redirect('dashboard')
    children = parent.children.select_related('route').all()
    return render(request, 'busmonitor/parent_dashboard.html', {
        'children': children,
    })

@login_required
def driver_dashboard(request):
    driver = getattr(request.user, 'driver', None)
    if not driver:
        import logging
        logging.error(f"No Driver object found for user {request.user.username} (ID: {request.user.id})")
        messages.error(request, 'No driver profile found for your account. Please contact admin.')
        return redirect('dashboard')
    bus = Bus.objects.filter(driver=driver).first()
    if not bus:
        import logging
        logging.warning(f"No Bus assigned to driver {driver.id} ({driver.user.username})")
    route = Route.objects.filter(bus=bus).first() if bus else None
    if not route:
        import logging
        logging.warning(f"No Route assigned to bus {bus.id if bus else 'None'} for driver {driver.id}")
    students = Student.objects.filter(route=route) if route else []
    return render(request, 'busmonitor/driver_dashboard.html', {
        'bus': bus,
        'route': route,
        'students': students,
    })

class ParentSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=20)
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

class DriverSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=20)
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'rfid', 'parent', 'route']

class ParentEditForm(forms.ModelForm):
    student_rfid = forms.CharField(label='Student RFID', required=False, help_text='Enter the RFID of the student to link')
    class Meta:
        model = Parent
        fields = ['phone_number']

class ParentUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']

class DriverEditForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ['phone_number']

class DriverUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']

class BusForm(forms.ModelForm):
    class Meta:
        model = Bus
        fields = ['number_plate', 'driver', 'current_latitude', 'current_longitude']

class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = ['name', 'start_location', 'end_location', 'bus']

def register_parent(request):
    if request.method == 'POST':
        form = ParentSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            phone_number = form.cleaned_data.get('phone_number')
            Parent.objects.create(user=user, phone_number=phone_number)
            login(request, user)
            messages.success(request, 'Parent account created successfully!')
            return redirect('parent_dashboard')
    else:
        form = ParentSignUpForm()
    return render(request, 'busmonitor/register_parent.html', {'form': form})

def register_driver(request):
    if request.method == 'POST':
        form = DriverSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            phone_number = form.cleaned_data.get('phone_number')
            Driver.objects.create(user=user, phone_number=phone_number)
            login(request, user)
            messages.success(request, 'Driver account created successfully!')
            return redirect('driver_dashboard')
    else:
        form = DriverSignUpForm()
    return render(request, 'busmonitor/register_driver.html', {'form': form})

@login_required
def register_student(request):
    if not request.user.is_superuser:
        return redirect('dashboard')
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student registered successfully!')
            return redirect('admin_dashboard')
    else:
        form = StudentForm()
    return render(request, 'busmonitor/register_student.html', {'form': form})

import json
# from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
# from .models import Student, Bus, BoardingHistory # Assuming your models are in the same app

@csrf_exempt
def rfid_scan(request):
    """
    Handles RFID scan data for student boarding/unboarding on a bus.
    Expects POST requests with JSON data.
    """
    if request.method == 'POST':
        # --- 1. Parse Request Body ---
        try:
            # Attempt to parse JSON body
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                # Fallback to form-data if content-type is not JSON
                # This might be useful for testing via browser forms, but ESP8266 sends JSON
                data = request.POST
        except json.JSONDecodeError:
            # Return error if JSON is invalid
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format.'}, status=400)
        except Exception as e:
            # Catch any other parsing errors
            return JsonResponse({'status': 'error', 'message': f'Error parsing request body: {str(e)}'}, status=400)

        # --- 2. Extract and Validate Required Data ---
        rfid = data.get('rfid')
        bus_id_str = data.get('bus_id') # Get as string first for validation
        gps_location = data.get('gps_location', '') # Optional, default to empty string
        action = data.get('action', 'board') # Default action is 'board'

        # Basic validation for essential fields
        if not rfid:
            return JsonResponse({'status': 'error', 'message': 'RFID is required.'}, status=400)
        if not bus_id_str:
            return JsonResponse({'status': 'error', 'message': 'Bus ID is required.'}, status=400)

        # Validate and convert bus_id to integer
        try:
            bus_id = int(bus_id_str)
        except (ValueError, TypeError):
            return JsonResponse({'status': 'error', 'message': 'Bus ID must be a valid number.'}, status=400)

        # --- 3. Process RFID Scan ---
        try:
            # Retrieve student and bus objects from the database
            student = Student.objects.get(rfid=rfid)
            bus = Bus.objects.get(id=bus_id)

            # Create a new boarding history record
            BoardingHistory.objects.create(
                student=student,
                bus=bus,
                timestamp=timezone.now(),
                action=action,
                gps_location=gps_location
            )

            # Get parent phone number, defaulting to an empty string if not available
            # This ensures the 'parent_phone_number' key is always present in the response
            parent_phone = student.parent.phone_number if student.parent else ""

            # --- 4. Return Success Response ---
            # Simplified success response, as requested
            return JsonResponse({
                'student_name': student.name,
                'parent_phone_number': parent_phone
            })

        except Student.DoesNotExist:
            # Handle case where RFID does not match any student
            return JsonResponse({'status': 'error', 'message': 'Student not found.'}, status=404)
        except Bus.DoesNotExist:
            # Handle case where bus ID does not match any bus
            return JsonResponse({'status': 'error', 'message': 'Bus not found.'}, status=404)
        except Exception as e:
            # Catch any other unexpected errors during processing
            # Log this error for debugging in a real application
            print(f"An unexpected error occurred: {e}") # For debugging, remove in production
            return JsonResponse({'status': 'error', 'message': f'An unexpected server error occurred: {str(e)}'}, status=500)

    # --- 5. Handle Invalid Request Method ---
    # Return error for any method other than POST
    return JsonResponse({'status': 'error', 'message': 'Invalid request method. Only POST is allowed.'}, status=405) # 405 Method Not Allowed

@login_required
def export_boarding_history(request):
    if not request.user.is_superuser:
        return redirect('dashboard')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="boarding_history.csv"'
    writer = csv.writer(response)
    writer.writerow(['Student', 'Bus', 'Timestamp', 'Action', 'GPS Location'])
    for record in BoardingHistory.objects.select_related('student', 'bus').all():
        writer.writerow([
            record.student.name,
            record.bus.number_plate,
            record.timestamp,
            record.action,
            record.gps_location
        ])
    return response

@login_required
def route_map(request, route_id):
    route = get_object_or_404(Route, id=route_id)

    origin = route.start_location
    destination = route.end_location

    map_url = f"https://schoolroute.silicon4forge.org/?origin={origin}&destination={destination}"
    return redirect(map_url)

@csrf_exempt
def update_bus_location(request):
    if request.method == 'POST':
        bus_id = request.POST.get('bus_id')
        lat = request.POST.get('lat')
        lng = request.POST.get('lng')
        try:
            bus = Bus.objects.get(id=bus_id)
            bus.current_latitude = lat
            bus.current_longitude = lng
            bus.save()
            return JsonResponse({'status': 'success'})
        except Bus.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Bus not found.'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request.'}, status=400)

@login_required
def parent_bus_map(request):
    parent = getattr(request.user, 'parent', None)
    if not parent:
        return redirect('dashboard')
    children = parent.children.select_related('route').all()
    buses = []
    for child in children:
        if child.route and child.route.bus:
            buses.append({
                'student': child,
                'bus': child.route.bus
            })
    return render(request, 'busmonitor/parent_bus_map.html', {'buses': buses})

@login_required
def driver_bus_map(request):
    driver = getattr(request.user, 'driver', None)
    if not driver:
        return redirect('dashboard')
    bus = Bus.objects.filter(driver=driver).first()
    return render(request, 'busmonitor/driver_bus_map.html', {'bus': bus})

def choose_role(request):
    return render(request, 'busmonitor/choose_role.html')

@login_required
def admin_register_all(request):
    if not request.user.is_superuser:
        return redirect('dashboard')
    parent_form = ParentSignUpForm(prefix='parent')
    driver_form = DriverSignUpForm(prefix='driver')
    student_form = StudentForm(prefix='student')
    if request.method == 'POST':
        parent_form = ParentSignUpForm(request.POST, prefix='parent')
        driver_form = DriverSignUpForm(request.POST, prefix='driver')
        student_form = StudentForm(request.POST, prefix='student')
        if parent_form.is_valid() and driver_form.is_valid() and student_form.is_valid():
            # Create parent
            parent_user = parent_form.save()
            parent = Parent.objects.create(user=parent_user, phone_number=parent_form.cleaned_data['phone_number'])
            # Create driver
            driver_user = driver_form.save()
            driver = Driver.objects.create(user=driver_user, phone_number=driver_form.cleaned_data['phone_number'])
            # Create route and bus if not exist
            route_name = student_form.cleaned_data['route'].name
            route, created = Route.objects.get_or_create(name=route_name)
            if created or not route.bus:
                bus = Bus.objects.create(number_plate=f"BUS-{route_name.upper()}", driver=driver)
                route.bus = bus
                route.save()
            else:
                bus = route.bus
                bus.driver = driver
                bus.save()
            # Create student
            student = student_form.save(commit=False)
            student.parent = parent
            student.route = route
            student.save()
            messages.success(request, 'Parent, driver, and student registered and mapped successfully!')
            return redirect('admin_dashboard')
    return render(request, 'busmonitor/admin_register_all.html', {
        'parent_form': parent_form,
        'driver_form': driver_form,
        'student_form': student_form,
    })

def custom_admin_login(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            error = 'Invalid credentials or not an admin.'
    return render(request, 'busmonitor/admin_login.html', {'error': error})

@login_required
def student_create(request):
    if not request.user.is_superuser:
        return redirect('dashboard')
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student added successfully!')
            return redirect('admin_dashboard')
    else:
        form = StudentForm()
    return render(request, 'busmonitor/student_form.html', {'form': form, 'student': None})

@login_required
def student_update(request, pk):
    if not request.user.is_superuser:
        return redirect('dashboard')
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student updated successfully!')
            return redirect('admin_dashboard')
    else:
        form = StudentForm(instance=student)
    return render(request, 'busmonitor/student_form.html', {'form': form, 'student': student})

@login_required
def student_delete(request, pk):
    if not request.user.is_superuser:
        return redirect('dashboard')
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.delete()
        messages.success(request, 'Student deleted successfully!')
        return redirect('admin_dashboard')
    return render(request, 'busmonitor/student_confirm_delete.html', {'student': student})

@login_required
def parent_create(request):
    if not request.user.is_superuser:
        return redirect('dashboard')
    user_form = ParentUserForm(request.POST or None)
    parent_form = ParentEditForm(request.POST or None)
    if request.method == 'POST':
        if user_form.is_valid() and parent_form.is_valid():
            user = user_form.save()
            parent = parent_form.save(commit=False)
            parent.user = user
            parent.save()
            # Link student by RFID if provided
            student_rfid = parent_form.cleaned_data.get('student_rfid')
            if student_rfid:
                try:
                    student = Student.objects.get(rfid=student_rfid)
                    student.parent = parent
                    student.save()
                    messages.success(request, f'Parent added and linked to student {student.name}.')
                except Student.DoesNotExist:
                    messages.warning(request, 'Parent added, but no student found with that RFID.')
            else:
                messages.success(request, 'Parent added successfully!')
            return redirect('admin_dashboard')
    return render(request, 'busmonitor/parent_form.html', {'form': parent_form, 'user_form': user_form, 'parent': None})

@login_required
def parent_update(request, pk):
    if not request.user.is_superuser:
        return redirect('dashboard')
    parent = get_object_or_404(Parent, pk=pk)
    user_form = ParentUserForm(request.POST or None, instance=parent.user)
    parent_form = ParentEditForm(request.POST or None, instance=parent)
    if request.method == 'POST':
        if user_form.is_valid() and parent_form.is_valid():
            user_form.save()
            parent_form.save()
            # Link student by RFID if provided
            student_rfid = parent_form.cleaned_data.get('student_rfid')
            if student_rfid:
                try:
                    student = Student.objects.get(rfid=student_rfid)
                    student.parent = parent
                    student.save()
                    messages.success(request, f'Parent updated and linked to student {student.name}.')
                except Student.DoesNotExist:
                    messages.warning(request, 'Parent updated, but no student found with that RFID.')
            else:
                messages.success(request, 'Parent updated successfully!')
            return redirect('admin_dashboard')
    return render(request, 'busmonitor/parent_form.html', {'form': parent_form, 'user_form': user_form, 'parent': parent})

@login_required
def parent_delete(request, pk):
    if not request.user.is_superuser:
        return redirect('dashboard')
    parent = get_object_or_404(Parent, pk=pk)
    if request.method == 'POST':
        parent.user.delete()
        parent.delete()
        messages.success(request, 'Parent deleted successfully!')
        return redirect('admin_dashboard')
    return render(request, 'busmonitor/parent_confirm_delete.html', {'parent': parent})

@login_required
def driver_create(request):
    if not request.user.is_superuser:
        return redirect('dashboard')
    user_form = DriverUserForm(request.POST or None)
    driver_form = DriverEditForm(request.POST or None)
    if request.method == 'POST':
        if user_form.is_valid() and driver_form.is_valid():
            user = user_form.save()
            driver = driver_form.save(commit=False)
            driver.user = user
            driver.save()
            messages.success(request, 'Driver added successfully!')
            return redirect('admin_dashboard')
    return render(request, 'busmonitor/driver_form.html', {'form': driver_form, 'user_form': user_form, 'driver': None})

@login_required
def driver_update(request, pk):
    if not request.user.is_superuser:
        return redirect('dashboard')
    driver = get_object_or_404(Driver, pk=pk)
    user_form = DriverUserForm(request.POST or None, instance=driver.user)
    driver_form = DriverEditForm(request.POST or None, instance=driver)
    if request.method == 'POST':
        if user_form.is_valid() and driver_form.is_valid():
            user_form.save()
            driver_form.save()
            messages.success(request, 'Driver updated successfully!')
            return redirect('admin_dashboard')
    return render(request, 'busmonitor/driver_form.html', {'form': driver_form, 'user_form': user_form, 'driver': driver})

@login_required
def driver_delete(request, pk):
    if not request.user.is_superuser:
        return redirect('dashboard')
    driver = get_object_or_404(Driver, pk=pk)
    if request.method == 'POST':
        driver.user.delete()
        driver.delete()
        messages.success(request, 'Driver deleted successfully!')
        return redirect('admin_dashboard')
    return render(request, 'busmonitor/driver_confirm_delete.html', {'driver': driver})

@login_required
def bus_create(request):
    if not request.user.is_superuser:
        return redirect('dashboard')
    if request.method == 'POST':
        form = BusForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bus added successfully!')
            return redirect('admin_dashboard')
    else:
        form = BusForm()
    return render(request, 'busmonitor/bus_form.html', {'form': form, 'bus': None})

@login_required
def bus_update(request, pk):
    if not request.user.is_superuser:
        return redirect('dashboard')
    bus = get_object_or_404(Bus, pk=pk)
    if request.method == 'POST':
        form = BusForm(request.POST, instance=bus)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bus updated successfully!')
            return redirect('admin_dashboard')
    else:
        form = BusForm(instance=bus)
    return render(request, 'busmonitor/bus_form.html', {'form': form, 'bus': bus})

@login_required
def bus_delete(request, pk):
    if not request.user.is_superuser:
        return redirect('dashboard')
    bus = get_object_or_404(Bus, pk=pk)
    if request.method == 'POST':
        bus.delete()
        messages.success(request, 'Bus deleted successfully!')
        return redirect('admin_dashboard')
    return render(request, 'busmonitor/bus_confirm_delete.html', {'bus': bus})

@login_required
def route_create(request):
    if not request.user.is_superuser:
        return redirect('dashboard')
    form = RouteForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Route added successfully!')
        return redirect('admin_dashboard')
    return render(request, 'busmonitor/route_form.html', {'form': form, 'route': None})

@login_required
def route_update(request, pk):
    if not request.user.is_superuser:
        return redirect('dashboard')
    route = get_object_or_404(Route, pk=pk)
    form = RouteForm(request.POST or None, instance=route)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Route updated successfully!')
        return redirect('admin_dashboard')
    return render(request, 'busmonitor/route_form.html', {'form': form, 'route': route})

@login_required
def route_delete(request, pk):
    if not request.user.is_superuser:
        return redirect('dashboard')
    route = get_object_or_404(Route, pk=pk)
    if request.method == 'POST':
        route.delete()
        messages.success(request, 'Route deleted successfully!')
        return redirect('admin_dashboard')
    return render(request, 'busmonitor/route_confirm_delete.html', {'route': route})

@login_required
def student_map_redirect(request, student_id):
    student = get_object_or_404(Student, id=student_id, parent=request.user.parent)
    # Get latest boarding record with action 'board'
    boarding = BoardingHistory.objects.filter(student=student, action='board').order_by('-timestamp').first()
    if not boarding or not student.route:
        messages.warning(request, 'No boarding record or route found for this student.')
        return redirect('parent_dashboard')
    origin = boarding.gps_location
    destination = student.route.end_location
    map_url = f"https://schoolroute.silicon4forge.org/?origin={origin}&destination={destination}"
    return redirect(map_url)

@login_required
def driver_map_redirect(request):
    driver = getattr(request.user, 'driver', None)
    bus = getattr(driver, 'bus', None) if driver else None
    route = getattr(bus, 'route', None) if bus else None
    if not route:
        return redirect('driver_dashboard')
    origin = route.start_location
    destination = route.end_location
    map_url = f"https://schoolroute.silicon4forge.org/?origin={origin}&destination={destination}"
    return redirect(map_url)

@login_required
def admin_driver_map_redirect(request, driver_id):
    driver = get_object_or_404(Driver, id=driver_id)
    bus = getattr(driver, 'bus', None)
    route = getattr(bus, 'route', None) if bus else None
    if not route:
        return redirect('admin_dashboard')
    origin = route.start_location
    destination = route.end_location
    map_url = f"https://schoolroute.silicon4forge.org/?origin={origin}&destination={destination}"
    return redirect(map_url)
