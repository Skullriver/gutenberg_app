from django.urls import path
from .views import search_books, book_details

urlpatterns = [
    path('', search_books, name='search_books'),
    path('books/<int:book_id>/', book_details, name='book_details'),
]

