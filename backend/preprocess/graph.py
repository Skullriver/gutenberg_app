from django.http import JsonResponse
import networkx as nx
from django.db import connection
from .models import IndexTable, Book

def create_graph(request):
      
    # Create an empty graph
    G = nx.Graph()

    sql = """
    SELECT source_book_id, target_book_id, weight FROM preprocess_edgelist;
    """

    # Execute the SQL query and fetch the results
    with connection.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()

    # Assuming `edges` is a list of tuples (source_book_id, target_book_id, weight)
    # obtained from your database query
    for source, target, weight in result:
        G.add_edge(source, target, weight=weight)
    
    print(f"Graph has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")

    # Calculate Betweenness Centrality
    betweenness = nx.betweenness_centrality(G, weight='weight')

    print("Betweenness Centrality calculated")

    # Calculate Closeness Centrality
    closeness = nx.closeness_centrality(G)

    print("Closeness Centrality calculated")

    # Calculate PageRank
    pagerank = nx.pagerank(G, weight='weight')

    print("PageRank calculated")

    # `betweenness`, `closeness`, and `pagerank` are dictionaries where the key is the node ID and the value is the metric score
    for book_id in G.nodes:
        # Since betweenness, closeness, and pagerank are keyed by node (book_id), 
        # use the book_id to access the metric value for each book.
        book = Book.objects.get(book_id=book_id)  # Assuming 'id' is the primary key for Book

        # Assuming there's one IndexTable entry per book for these metrics (adjust logic as necessary)
        IndexTable.objects.update_or_create(
            book=book,
            defaults={
                'betweenness_centrality': betweenness.get(book_id, 0.0),
                'closeness_centrality': closeness.get(book_id, 0.0),
                'pagerank': pagerank.get(book_id, 0.0),
            }
        )
        print(f"Metrics updated for {book.title}")
    
    return JsonResponse({"status": "success", "message": "Graph metrics calculated and updated successfully."})