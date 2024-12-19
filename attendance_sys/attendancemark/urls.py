from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('recognize-face/', views.recognize_face, name='recognize_face'),
    path('get-attendance/', views.get_attendance_details, name='get_attendance'),
    path('start-day/', views.start_day, name='start_day'),
    path('admin-page/', views.admin_page, name='admin_page'),
]

