from django.contrib import admin
from .models import Parent, Driver, Bus, Route, Student, BoardingHistory

@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone_number')

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone_number')

@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = ('number_plate', 'driver')
    search_fields = ('number_plate',)
    list_filter = ('driver',)

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('name', 'bus', 'start_location', 'end_location')
    search_fields = ('name', 'start_location', 'end_location')
    list_filter = ('bus',)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'rfid', 'parent', 'route')
    search_fields = ('name', 'rfid', 'parent__user__username')
    list_filter = ('route',)

@admin.register(BoardingHistory)
class BoardingHistoryAdmin(admin.ModelAdmin):
    list_display = ('student', 'bus', 'timestamp', 'action', 'gps_location')
    search_fields = ('student__name', 'bus__number_plate', 'gps_location')
    list_filter = ('action', 'bus')
