
from django.urls import path
from . import views

urlpatterns = [
    path('', views.Dashboard, name='Dashboard'),
    path('Process/Upload', views.Upload_image.as_view(), name='upload_image'),

]
