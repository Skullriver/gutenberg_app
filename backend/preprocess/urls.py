from django.urls import path
from .views import simple_json, calculate_jaccard_and_populate_graph

urlpatterns = [
    path('hello/', simple_json, name='simple_json'),
    path('graph/', calculate_jaccard_and_populate_graph, name='calculate_jaccard_and_populate_graph'),
]
