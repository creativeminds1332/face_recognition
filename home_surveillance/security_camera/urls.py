from django.urls import path

from . import views

app_name='security_camera'

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('upload', views.upload, name='upload'),
    path('recognize', views.recognize, name='recognize'),
    path('search', views.search, name='search'),
    path('delete', views.delete, name='delete'),
    path('update', views.update, name='update'),
    path('webcam_feed', views.webcam_feed, name='webcam_feed'),
    path('viewpic', views.viewpic, name='viewpic'),
]