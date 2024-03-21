from django.shortcuts import render
from django.http import JsonResponse
from preprocess.models import Book, Word, WordFrequencies, EdgeList
from preprocess.preprocess import preprocess_text
from collections import defaultdict
from django.db.models import Count, Q, Subquery
from django.db import connection
from itertools import combinations
import re
import math
from django.core.exceptions import ObjectDoesNotExist

from math import log

def book_details(request, book_id):
    try:
        book = Book.objects.get(pk=book_id)
        data = {
            'book_id': book.book_id,
            'type': book.type,
            'issued': book.issued,
            'title': book.title,
            'language': book.language,
            'authors': book.authors,
            'subjects': book.subjects,
            'locc': book.locc,
            'bookshelves': book.bookshelves,
            'cover': f'https://www.gutenberg.org/cache/epub/{book.book_id}/pg{book.book_id}.cover.medium.jpg',
            'text_link': f'https://gutenberg.org/cache/epub/{book.book_id}/pg{book.book_id}.txt'
        }
        return JsonResponse(data)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Book not found'}, status=404)



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

    positions_by_word_id = {word['word_id']: word['positions'] for word in word_positions}

    for (word_id1, positions1), (word_id2, positions2) in combinations(positions_by_word_id.items(), 2):
        min_distance = min(abs(p1 - p2) for p1 in positions1 for p2 in positions2)
        total_distance += min_distance
        if min_distance == 1:
            sequenced_pairs += 1
            
    if total_pairs == 0:
        return -1 # No proximity score if there are no adjacent query words in the text

    average_distance = total_distance / len(query_words)

    score = sequenced_pairs / total_pairs + 1 / average_distance if average_distance > 0 else -1
    return score


def get_suggestions_for_document(book_id):
    # Assuming 'document_id' is the ID of one of the top relevant documents
    # Fetch neighbors based on the Jaccard similarity
    suggestions = EdgeList.objects.filter(source_book=book_id).order_by('-weight')[:3]  # Top 3 suggestions
    
    suggested_documents = [
        {
            'title': edge.target_book.title,
            'authors': edge.target_book.authors,  # Adjust if 'authors' needs special handling
            'cover': f'https://www.gutenberg.org/cache/epub/{edge.target_book.book_id}/{edge.target_book.book_id}-cover.png'
        }
        for edge in suggestions
    ]
    
    return suggested_documents


def preprocess_query(query_phrase, is_regex):

    if is_regex:
        # For advanced regex search
        query_words = query_phrase.split()
    else:
        query_words, _, _ = preprocess_text(query_phrase, 'english')

    if is_regex:
        query_words_list =  '|'.join([f"{word}" for word in query_words])
    else:
        query_words_list = ','.join([f"'{word}'" for word in query_words])
    
    return query_words, query_words_list

def build_sql_query(query_words_list, is_regex=False, is_phrase_query=False):

    if is_regex:
        condition = f"w.word ~* '{query_words_list}'"
    else:
        condition = f"w.word IN ({query_words_list})"

    if is_phrase_query:
        if is_regex:
            phrase_condition = ""
        else:
            phrase_condition = "HAVING COUNT(DISTINCT wf.word_id) = %s"
    else:
        phrase_condition = ""

    sql = f"""
    WITH matching_books AS (
    SELECT book.book_id, book.title, book.authors,
           COUNT(DISTINCT wf.word_id) AS matching_words
    FROM preprocess_book AS book
    INNER JOIN preprocess_wordfrequencies AS wf ON book.book_id = wf.book_id
    INNER JOIN preprocess_word AS w ON wf.word_id = w.id
    WHERE ({condition}) -- Placeholders for query words
    GROUP BY book.book_id
    {phrase_condition} -- Placeholder for length of query_words_list
    ), word_positions AS (
        SELECT wp.book_id, w.word, w.id AS word_id, wp.positions
        FROM preprocess_wordpositions AS wp
        INNER JOIN preprocess_word AS w ON wp.word_id = w.id
        WHERE ({condition}) -- Placeholders for query words
        GROUP BY wp.book_id, w.word, w.id, wp.positions
    ), word_frequencies AS (
        SELECT wf.book_id, w.word, wf.frequency
        FROM preprocess_wordfrequencies AS wf
        INNER JOIN preprocess_word AS w ON wf.word_id = w.id
        WHERE ({condition}) -- Use placeholders appropriately here
        GROUP BY wf.book_id, w.word, wf.frequency
    ), max_frequencies_per_book AS (
        SELECT wf.book_id, MAX(wf.frequency) AS max_raw_freq
        FROM preprocess_wordfrequencies AS wf
        GROUP BY wf.book_id
    )
    SELECT mb.book_id, mb.title, mb.authors, wp.word, wp.word_id, wp.positions, wf.frequency, mf.max_raw_freq, it.pagerank, it.betweenness_centrality, it.closeness_centrality
    FROM matching_books mb
    INNER JOIN word_positions wp ON mb.book_id = wp.book_id
    INNER JOIN word_frequencies wf ON mb.book_id = wf.book_id AND wp.word = wf.word
    INNER JOIN max_frequencies_per_book mf ON mb.book_id = mf.book_id
    INNER JOIN preprocess_indextable it ON mb.book_id = it.book_id
    ORDER BY mb.book_id, wp.word;
    """
    print(sql)
    
    return sql

def execute_sql_query(sql, num_query_words):
    with connection.cursor() as cursor:
        cursor.execute(sql, [num_query_words])
        result = cursor.fetchall()
    return result

def prepare_results(result, query_words, is_phrase_query, is_regex):

    w1, w2, w3, w4 = 0.4, 0.3, 0.15, 0.15  # Weights for final score components
    w_tf_idf, w_prox = 0.7, 0.3  # Weights for relevance components
    relevance_boost = 1

    is_phrase_query = len(query_words) > 1

    books_info = defaultdict(lambda: defaultdict(list))

    for row in result:
        book_id, title, authors, word, word_id, positions_str, frequency, max_frequency, page_rank, betweenness, closeness = row
    
        positions = positions_str  # If positions are directly usable as a list, just assign them

        title_words, _, _ = preprocess_text(title)
        author_words, _, _ = preprocess_text(authors)
       
        if book_id not in books_info:
            books_info[book_id] = {
                'id': book_id,
                'title': title,
                'authors': authors,
                'cover': f'https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.cover.medium.jpg',
                'words': [],
                'proximity_score': 0, 
                'tf_idf_score': 0,
                'relevance': 0,
                'pagerank': page_rank,
                'betweenness_centrality': betweenness,
                'closeness_centrality': closeness,
                'final_score': 0
        }
        
        books_info[book_id]['words'].append({'word': word, 'id':word_id, 'positions': positions, 'tf': 0.5 + (0.5 * frequency / max_frequency), 'frequency': frequency})
        
        if not is_regex:
            if set(query_words) & set(title_words):
                books_info[book_id]['relevance'] += relevance_boost
            if set(query_words) & set(author_words):
                books_info[book_id]['relevance'] += relevance_boost
        else:
            # Compile regex patterns for efficiency if you are checking multiple titles/authors
            regex_patterns = [re.compile(word, re.IGNORECASE) for word in query_words]
            
            # Check if any of the compiled regex patterns match the title
            if any(pattern.search(books_info[book_id]['title']) for pattern in regex_patterns):
                books_info[book_id]['relevance'] += relevance_boost
            
            # Similarly, check for matches in authors if needed
            # This assumes 'authors' is a string; adjust accordingly if it's a list or other structure
            if any(pattern.search(books_info[book_id]['authors']) for pattern in regex_patterns):
                books_info[book_id]['relevance'] += relevance_boost

    idf_scores = {}
    total_books = Book.objects.count()

    if not is_regex:
        words = Word.objects.filter(word__in=query_words)

        for word in words:
            num_books_with_word = WordFrequencies.objects.filter(word=word).values('book').distinct().count()
            idf_scores[word.word] = math.log((1 + total_books) / (1 + num_books_with_word))
    else:
        # Create a Q object to accumulate queries
        query_accumulator = Q()

        # Loop through each regex pattern and build the query
        for regex_pattern in query_words:
            query_accumulator |= Q(word__regex=regex_pattern)

        # Use the accumulated Q object to filter Word objects
        words = Word.objects.filter(query_accumulator).distinct()
        for word in words:
            num_books_with_word = WordFrequencies.objects.filter(word=word).aggregate(books_count=Count('book', distinct=True))['books_count']
            idf_scores[word.word] = math.log((1 + total_books) / (1 + num_books_with_word))

    # Convert defaultdict to a regular dict for easier use outside of this context
    books_info = dict(books_info)

    for book_id, book_info in books_info.items():
        # word_positions = {word['word']: word['positions'] for word in book_info['words']}
        word_positions = [{
            'word_id': word['id'],
            'word': word['word'],  # Assuming you also have the word text here
            'positions': word['positions']
        } for word in book_info['words']]
        books_info[book_id]['proximity_score'] = calculate_proximity_score(word_positions, query_words)
        books_info[book_id]['tf_idf_score'] = sum(word['tf'] * idf_scores[word['word']] for word in book_info['words'])

        if is_phrase_query:
            relevance = w_tf_idf * book_info['tf_idf_score'] + w_prox * book_info['proximity_score']
        else:
            relevance = book_info['tf_idf_score']  # For single word queries, only TF-IDF score is considered
        
        final_score = book_info['relevance'] + (w1 * relevance) + (w2 * books_info[book_id]['pagerank']) + (w3 * books_info[book_id]['betweenness_centrality']) + (w4 * books_info[book_id]['closeness_centrality'])

        # Update the book_info dictionary with the final score
        books_info[book_id]['final_score'] = final_score
        
        
    books_info = sorted(books_info.values(), key=lambda x: x['final_score'], reverse=True)

    return books_info


def search_books(request):
    query_phrase = request.GET.get('query', '').strip()
    regex_query = request.GET.get('regex', '').strip()
    
    is_regex_query = bool(regex_query)
    search_phrase = regex_query if is_regex_query else query_phrase

    if not search_phrase :
        return JsonResponse({'error': 'No query provided'}, status=400)
    
    query_words, query_words_list = preprocess_query(search_phrase, is_regex_query)
    print(f"Searching for: {query_words}")
    num_query_words = len(set(query_words))

    sql = build_sql_query(query_words_list, is_regex_query, len(query_words) > 1)
    result = execute_sql_query(sql, num_query_words)
    books_info = prepare_results(result, query_words, len(query_words) > 1, is_regex_query)

    top_3_books = books_info[:3]
    books_suggestions = []

    for book in top_3_books:
        book_id = book['id']
        suggestions = get_suggestions_for_document(book_id)
        books_suggestions.extend(suggestions)
     
    return JsonResponse({'results': books_info, 'suggestions': books_suggestions})

def search_books_old(request):
    
    query_phrase = request.GET.get('query', '').strip()
    
    query_words, _, _ = preprocess_text(query_phrase, 'english')

    print(f"Searching for: {query_words}")

    w1, w2, w3, w4 = 0.4, 0.3, 0.15, 0.15  # Weights for final score components
    w_tf_idf, w_prox = 0.7, 0.3  # Weights for relevance components
    relevance_boost = 1

    is_phrase_query = len(query_words) > 1

    query_words_list = ','.join([f"'{word}'" for word in query_words])
    num_query_words = len(set(query_words))

    
    sql = f"""
    WITH matching_books AS (
    SELECT book.book_id, book.title, book.authors,
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
    ), max_frequencies_per_book AS (
        SELECT wf.book_id, MAX(wf.frequency) AS max_raw_freq
        FROM preprocess_wordfrequencies AS wf
        GROUP BY wf.book_id
    )
    SELECT mb.book_id, mb.title, mb.authors, wp.word, wp.positions, wf.frequency, mf.max_raw_freq, it.pagerank, it.betweenness_centrality, it.closeness_centrality
    FROM matching_books mb
    INNER JOIN word_positions wp ON mb.book_id = wp.book_id
    INNER JOIN word_frequencies wf ON mb.book_id = wf.book_id AND wp.word = wf.word
    INNER JOIN max_frequencies_per_book mf ON mb.book_id = mf.book_id
    INNER JOIN preprocess_indextable it ON mb.book_id = it.book_id
    ORDER BY mb.book_id, wp.word;
    """


    with connection.cursor() as cursor:
        cursor.execute(sql, [num_query_words])
        result = cursor.fetchall()

    books_info = defaultdict(lambda: defaultdict(list))

    
    for row in result:
        book_id, title, authors, word, positions_str, frequency, max_frequency, page_rank, betweenness, closeness = row
    
        positions = positions_str  # If positions are directly usable as a list, just assign them

        title_words, _, _ = preprocess_text(title)
        author_words, _, _ = preprocess_text(authors)
       
        if book_id not in books_info:
            books_info[book_id] = {
                'id': book_id,
                'title': title,
                'authors': authors,
                'cover': f'https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.cover.medium.jpg',
                'words': [],
                'proximity_score': 0, 
                'tf_idf_score': 0,
                'relevance': 0,
                'pagerank': page_rank,
                'betweenness_centrality': betweenness,
                'closeness_centrality': closeness,
                'final_score': 0
        }
        
        books_info[book_id]['words'].append({'word': word, 'positions': positions, 'tf': 0.5 + (0.5 * frequency / max_frequency), 'frequency': frequency})
        if set(query_words) & set(title_words):
            books_info[book_id]['relevance'] += relevance_boost
        if set(query_words) & set(author_words):
            books_info[book_id]['relevance'] += relevance_boost

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
        books_info[book_id]['tf_idf_score'] = sum(word['tf'] * idf_scores[word['word']] for word in book_info['words'])

        if is_phrase_query:
            relevance = w_tf_idf * book_info['tf_idf_score'] + w_prox * book_info['proximity_score']
        else:
            relevance = book_info['tf_idf_score']  # For single word queries, only TF-IDF score is considered
        
        final_score = book_info['relevance'] + (w1 * relevance) + (w2 * books_info[book_id]['pagerank']) + (w3 * books_info[book_id]['betweenness_centrality']) + (w4 * books_info[book_id]['closeness_centrality'])

        # Update the book_info dictionary with the final score
        books_info[book_id]['final_score'] = final_score
        
        
    books_info = sorted(books_info.values(), key=lambda x: x['final_score'], reverse=True)
    
    top_3_books = books_info[:3]
    books_suggestions = []

    for book in top_3_books:
        book_id = book['id']
        suggestions = get_suggestions_for_document(book_id)
        books_suggestions.extend(suggestions)
     
    return JsonResponse({'results': books_info, 'suggestions': books_suggestions})


def get_random_books(request):
    
    sql = """
    SELECT b.book_id, b.title, b.authors, 'https://www.gutenberg.org/cache/epub/' || b.book_id || '/' || b.book_id || '-cover.png' AS cover
    FROM preprocess_book AS b
    INNER JOIN (
        SELECT DISTINCT wf.book_id
        FROM preprocess_wordfrequencies AS wf
    ) AS distinct_wf ON b.book_id = distinct_wf.book_id
    ORDER BY RANDOM()
    LIMIT 50;
    """

    # Execute the query
    with connection.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()

    books_data = [
        {'id': row[0], 'title': row[1], 'authors': row[2], 'cover': row[3]} for row in rows
    ]

    # Return the data as JSON
    return JsonResponse({'books': books_data})