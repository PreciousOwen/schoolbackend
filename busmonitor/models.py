from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Parent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return self.user.get_full_name()

class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return self.user.get_full_name()

class Bus(models.Model):
    number_plate = models.CharField(max_length=20, unique=True)
    driver = models.OneToOneField(Driver, on_delete=models.SET_NULL, null=True, blank=True)
    current_latitude = models.FloatField(null=True, blank=True)
    current_longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.number_plate

class Route(models.Model):
    name = models.CharField(max_length=100)
    bus = models.OneToOneField(Bus, on_delete=models.SET_NULL, null=True, blank=True)
    start_location = models.CharField(max_length=255)
    end_location = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Student(models.Model):
    name = models.CharField(max_length=100)
    rfid = models.CharField(max_length=50, unique=True)
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name='children')
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

class BoardingHistory(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=10, choices=[('board', 'Board'), ('alight', 'Alight')])
    gps_location = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.student.name} - {self.action} at {self.timestamp}"
