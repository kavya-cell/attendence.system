from django.test import TestCase
import face_recognition
from .models import Student
# Create your tests here

for student in Student.objects.all():
    print(student.image)