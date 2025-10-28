from django.urls import path
from . import views

urlpatterns = [
    path('<str:page_name>/', views.map_view, name='map_view'),
]
