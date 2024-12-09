from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Route for the main page
    path('recognize-face/', views.recognize_face, name='recognize_face'),  # Route for face recognition
]

# urlpatterns = [
#     path('', views.index, name='index'),
#     path('video_feed/', views.video_feed, name='video_feed'),
#     path('get_recognized_student/', views.get_recognized_student, name='get_recognized_student'),

# ]