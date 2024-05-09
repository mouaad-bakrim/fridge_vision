
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.Dashboard, name='Dashboard'),
    path('Process_detail/<int:pk>', views.DetailProcess.as_view(), name='Detail_Process'),
    path('Process/list', views.ListProcess.as_view(), name='List_process'),
    path('Process/Upload', views.Upload_image.as_view(), name='upload_image'),

]
