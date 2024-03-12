from django.urls import path
from .views import simple_json

urlpatterns = [
    path('hello/', simple_json, name='simple_json'),
]
