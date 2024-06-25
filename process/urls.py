
from django.urls import path
from . import views

urlpatterns = [
    path('', views.Dashboard, name='Dashboard'),
    path('comparaison', views.Comparaison, name='Dashboard'),
    # path('Process/list', views.ListProcess.as_view(), name='List_process'),
    path('Process/Upload', views.Upload_image.as_view(), name='upload_image'),

]
