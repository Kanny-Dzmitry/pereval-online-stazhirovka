from django.urls import path
from .views import submit_data, pass_detail

urlpatterns = [
    path('submitData/', submit_data, name='submit_data'),  # POST /submitData/ и GET /submitData/?user__email=<email>
    path('submitData/<int:pk>/', pass_detail, name='pass_detail'),  # GET /submitData/<id>/ и PATCH /submitData/<id>/
] 