from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('get_recognized_student/', views.get_recognized_student, name='get_recognized_student'),

]