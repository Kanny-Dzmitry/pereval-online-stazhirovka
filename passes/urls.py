from django.urls import path
from .views import submit_data

urlpatterns = [
    path('submitData/', submit_data, name='submit_data'),
] 