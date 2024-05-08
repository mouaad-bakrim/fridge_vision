
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('Process_detail/<int:pk>', views.DetailProcess.as_view(), name='Detail_Process'),
    path('', views.ListProcess.as_view(), name='List_process'),

]
