from django.urls import path
from . import views

urlpatterns = [
    path('', views.map_view, {'page_name': 'default'}, name='map_view'),
    path('<str:page_name>/', views.map_view, name='map_view_with_page'),
]
