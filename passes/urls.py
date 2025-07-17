from django.urls import path
from .views import submit_data_list, submit_data_detail

urlpatterns = [
    # Основные эндпоинты для работы с перевалами
    path('submitData/', submit_data_list, name='submit_data_list'),
    path('submitData/<int:pk>/', submit_data_detail, name='submit_data_detail'),
] 