from django.urls import path
from .views import submit_data, pass_detail

urlpatterns = [
    # POST/GET /submitData/ - создание нового перевала (POST) / получение перевалов пользователя (GET)
    path('submitData/', submit_data, name='submit_data'),
    
    # GET/PATCH /submitData/<id>/ - получение перевала по ID (GET) / редактирование перевала (PATCH)
    path('submitData/<int:pass_id>/', pass_detail, name='pass_detail'),
] 