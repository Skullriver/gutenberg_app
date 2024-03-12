from django.shortcuts import render
from django.http import JsonResponse
import requests
import csv
from .models import Book, IndexTable, Word, WordFrequencies, WordPositions
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


def calculate_proximity_score(word_positions, query_words):
    # Assuming word_positions is a dictionary where the key is a word
    # and the value is a list of positions that word appears in the document.
    # Initialize min_distance to infinity to find the minimum distance scenario.
    min_distance = float('inf')
    best_sequence_score = 0

    if len(query_words) > 1:
        for start_pos in word_positions[query_words[0]]:
            # Check if subsequent words follow in sequence
            sequence_match = True
            current_pos = start_pos
            for i in range(1, len(query_words)):
                next_word_positions = word_positions[query_words[i]]
                # Check if next word is exactly after the current one
                if current_pos + 1 in next_word_positions:
                    current_pos += 1
                else:
                    sequence_match = False
                    break

            if sequence_match:
                # If a perfect sequence is found, assign the highest score and break
                best_sequence_score = 1
                break
            else:
                # If not a perfect sequence, optionally calculate distance for proximity
                # This part can be adapted based on how you want to handle near matches.
                for i in range(len(query_words) - 1):
                    for pos1 in word_positions[query_words[i]]:
                        for pos2 in word_positions[query_words[i+1]]:
                            distance = abs(pos1 - pos2)
                            if distance < min_distance:
                                min_distance = distance

    # Update proximity score based on findings
    if best_sequence_score == 1:
        proximity_score = 2  # Highest score for perfect sequence match
    else:
        proximity_score = 0 if min_distance == float('inf') else 1 / min_distance

    return proximity_score




    