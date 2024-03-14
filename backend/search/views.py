from django.shortcuts import render
from django.http import JsonResponse
import requests
import csv
from preprocess.models import Book, IndexTable, Word, WordFrequencies, WordPositions
from preprocess.preprocess import preprocess_text
from django.utils.dateparse import parse_date
from django.db.models import Count, Sum
from collections import defaultdict, Counter
from django.db import connection
from itertools import combinations
from django.db import models
import math

from math import log


def simplified_proximity_score(word_positions, query_words):
    # Example simplified scoring
    total_distance = 0
    total_pairs = 0

    for i in range(len(query_words) - 1):
        positions1 = word_positions.get(query_words[i], [])
        positions2 = word_positions.get(query_words[i+1], [])
        
        if positions1 and positions2:
            # Calculate minimum distance between any pair of positions for these two words
            min_distance = min(abs(p1 - p2) for p1 in positions1 for p2 in positions2)
            total_distance += min_distance
            total_pairs += 1

    if total_pairs == 0:
        return 0  # No proximity score if there are no adjacent query words in the text

    average_distance = total_distance / total_pairs
    return 1 / average_distance if average_distance > 0 else 2  # Simplified scoring


def calculate_proximity_score(word_positions, query_words):
    
    total_distance = 0
    total_pairs = sum(1 for _ in combinations(query_words, 2))
    sequenced_pairs = 0

    for word1, word2 in combinations(list(set(query_words)), 2):
        min_distance = min(abs(p1 - p2) for p1 in word_positions[word1] for p2 in word_positions[word2])
        total_distance += min_distance
        if min_distance == 1:
            sequenced_pairs += 1
            
    if total_pairs == 0:
        return -1 # No proximity score if there are no adjacent query words in the text

    average_distance = total_distance / len(query_words)
    score = sequenced_pairs / total_pairs + 1 / average_distance
    return score

def search_books(request):
    query_phrase = request.GET.get('query', '').strip()
    
    query_words, _, _ = preprocess_text(query_phrase, 'english')

    print(f"Searching for: {query_words}")

    query_words_list = ','.join([f"'{word}'" for word in query_words])
    num_query_words = len(set(query_words))

    sql = f"""
    WITH matching_books AS (
    SELECT book.book_id, book.title,
           COUNT(DISTINCT wf.word_id) AS matching_words
    FROM preprocess_book AS book
    INNER JOIN preprocess_wordfrequencies AS wf ON book.book_id = wf.book_id
    INNER JOIN preprocess_word AS w ON wf.word_id = w.id
    WHERE w.word IN ({query_words_list}) -- Placeholders for query words
    GROUP BY book.book_id
    HAVING COUNT(DISTINCT wf.word_id) = %s -- Placeholder for length of query_words_list
    ), word_positions AS (
        SELECT wp.book_id, w.word, wp.positions
        FROM preprocess_wordpositions AS wp
        INNER JOIN preprocess_word AS w ON wp.word_id = w.id
        WHERE w.word IN ({query_words_list}) -- Placeholders for query words
        GROUP BY wp.book_id, w.word, wp.positions
    ), word_frequencies AS (
        SELECT wf.book_id, w.word, wf.frequency
        FROM preprocess_wordfrequencies AS wf
        INNER JOIN preprocess_word AS w ON wf.word_id = w.id
        WHERE w.word IN ({query_words_list}) -- Use placeholders appropriately here
        GROUP BY wf.book_id, w.word, wf.frequency
    )
    SELECT mb.book_id, mb.title, wp.word, wp.positions, wf.frequency
    FROM matching_books mb
    INNER JOIN word_positions wp ON mb.book_id = wp.book_id
    INNER JOIN word_frequencies wf ON mb.book_id = wf.book_id AND wp.word = wf.word
    ORDER BY mb.book_id, wp.word;
    """

    with connection.cursor() as cursor:
        cursor.execute(sql, [num_query_words])
        result = cursor.fetchall()

    books_info = defaultdict(lambda: defaultdict(list))

    
    for row in result:
        book_id, title, word, positions_str, frequency = row
    
        positions = positions_str  # If positions are directly usable as a list, just assign them
       
        if book_id not in books_info:
            books_info[book_id] = {
                'id': book_id,
                'title': title,
                'cover': f'https://www.gutenberg.org/cache/epub/{book_id}/{book_id}-cover.png',
                'words': [],
                'proximity_score': 0, 
                'tf_idf_score': 0
        }
        books_info[book_id]['words'].append({'word': word, 'positions': positions, 'frequency': frequency})
        

    idf_scores = {}
    total_books = Book.objects.count()
    words = Word.objects.filter(word__in=query_words)

    for word in words:
        num_books_with_word = WordFrequencies.objects.filter(word=word).values('book').distinct().count()
        idf_scores[word.word] = math.log((1 + total_books) / (1 + num_books_with_word))

    # Convert defaultdict to a regular dict for easier use outside of this context
    books_info = dict(books_info)

    for book_id, book_info in books_info.items():
        word_positions = {word['word']: word['positions'] for word in book_info['words']}
        books_info[book_id]['proximity_score'] = calculate_proximity_score(word_positions, query_words)
        books_info[book_id]['tf_idf_score'] = sum(word['frequency'] * idf_scores[word['word']] for word in book_info['words'])
        
    books_info = sorted(books_info.values(), key=lambda x: x['tf_idf_score'], reverse=True)
        # proximity_scores[book_id] = simplified_proximity_score(word_positions, query_words)
     
    return JsonResponse({'results': books_info})