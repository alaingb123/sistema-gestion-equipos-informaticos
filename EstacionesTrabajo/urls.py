from django.urls import path
from . import views

app_name = 'estacionestrabajo'

urlpatterns = [
    path('api/numeros-inventario/', views.get_numeros_inventario, name='get_numeros_inventario'),
] 