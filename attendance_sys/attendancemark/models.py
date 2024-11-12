from django.db import models

# Create your models here.

#Table that contains students information, along with their images that will be used for processing.
class Student(models.Model):
    rollnum = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=100)
    branch = models.CharField(max_length=40)
    year = models.IntegerField()
    image = models.ImageField(blank=False)

#Table to mark the attendance of students.
class Attendance(models.Model):
    slno = models.AutoField(primary_key=True)
    rollnum = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateTimeField()
    status = models.BooleanField()
    