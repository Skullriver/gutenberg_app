from django.shortcuts import render
from django.http import JsonResponse
import requests
import csv
from .models import Book, IndexTable, Word, WordFrequencies, WordPositions, EdgeList, AdjacencyList
from .preprocess import preprocess_text
from django.utils.dateparse import parse_date
from django.db.models import Count, Sum
from collections import defaultdict, Counter
from django.db import connection
import math
from django.db import models


from math import log


def insert_into_index_table(book, tokens, frequency, positions):

    word_objects = {}

    # Step 1: Ensure all tokens are in the Word table and cache their instances
    for token in tokens:
        word_obj, created = Word.objects.get_or_create(word=token)
        word_objects[token] = word_obj

    # Step 2: Update WordFrequencies table
    for token, freq in frequency.items():
        WordFrequencies.objects.update_or_create(
            book=book,
            word=word_objects[token],
            defaults={'frequency': freq}
        )

    # Step 3: Update WordPositions table
    for token, pos_list in positions.items():
        WordPositions.objects.update_or_create(
            book=book,
            word=word_objects[token],
            defaults={'positions': pos_list}
        )
        

def simple_json(request):

    # preprocessor = Preprocess()
    
    # tokens = preprocessor.preprocess("Mère Lapin prend son panier et son parapluie. Elle traverse le bois et s'en va chez le boulanger, acheter une miche de pain bis et cinq brioches.")
    
    # if tokens is not None:
    #     return JsonResponse({"status": "success", "tokens": tokens})
    # else:
    #     return JsonResponse({"status": "error", "message": "Could not process the file"})
    # Get a queryset of book_ids that have been preprocessed

    processed_book_ids = WordFrequencies.objects.all().values_list('book_id', flat=True)

    books = Book.objects.filter(language='en', type='Text')

    for book in books:
            if book.book_id in processed_book_ids or book.book_id == 673:
                print(f"Skipping {book.title} as it has already been processed")
                continue
            url = f'https://www.gutenberg.org/cache/epub/{book.book_id}/pg{book.book_id}.txt.utf8'
            response = requests.get(url)
            if response.status_code == 200:
                text = response.text
                tokens, frequency, positions = preprocess_text(text, 'english')  # Assuming English preprocessing
                insert_into_index_table(book, tokens, frequency, positions)
                # Here, you'd insert the tokens, frequencies, and positions into the preprocess_indextable
                # This is an example and needs to be adapted to your specific model fields and requirements
                print(f"Processed {book.title}: {len(tokens)} tokens")
            else:
                print(f"Failed to fetch {book.title} from Gutenberg")
    
    
    return JsonResponse({"status": "success", "message": "Books metadata inserted/updated successfully."})

def fetch_books_keywords():
    books_keywords = {}
    sql = """
    SELECT wf.book_id, array_agg(w.word) AS keywords
    FROM preprocess_wordfrequencies AS wf
    JOIN preprocess_word AS w ON wf.word_id = w.id
    GROUP BY wf.book_id;
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)
        for row in cursor.fetchall():
            book_id, keywords = row
            books_keywords[book_id] = set(keywords)  # Convert the list to a set for unique keywords

    return books_keywords

def calculate_jaccard_and_populate_graph(request):
    # Step 1: Extract keywords for each book
    books_keywords = fetch_books_keywords()
    processed_pairs = set()
    
    # Step 2: Calculate Jaccard similarity between each pair of books
    for book_id, keywords in books_keywords.items():
        adjacency_book_ids = []
        for other_book_id, other_keywords in books_keywords.items():
            if book_id == other_book_id:
                continue  # Skip comparing the book with itself
            print(f"Calculating Jaccard similarity between {book_id} and {other_book_id}")
            
            # Calculate Jaccard similarity
            intersection = len(keywords.intersection(other_keywords))
            union = len(keywords.union(other_keywords))
            jaccard_similarity = intersection / union if union != 0 else 0

            print(f"Jaccard similarity: {jaccard_similarity}")
            
            # Populate EdgeList - consider a similarity threshold if necessary
            if jaccard_similarity > 0.3:
                if (book_id, other_book_id) not in processed_pairs and (other_book_id, book_id) not in processed_pairs:
                    EdgeList.objects.update_or_create(
                        source_book_id=book_id,
                        target_book_id=other_book_id,
                        defaults={'weight': jaccard_similarity}
                    )
                adjacency_book_ids.append(other_book_id)
                processed_pairs.add((book_id, other_book_id))
        
        # Populate AdjacencyList
        AdjacencyList.objects.update_or_create(
            book_id=book_id,
            defaults={'adjacent_book_ids': adjacency_book_ids}
        )
    return JsonResponse({"status": "success", "message": "Graph populated successfully."})
    