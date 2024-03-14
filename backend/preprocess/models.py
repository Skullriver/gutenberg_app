from django.db import models
from django.contrib.postgres.fields import ArrayField

class Book(models.Model):
    book_id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=255)
    issued = models.DateField()
    title = models.TextField()
    language = models.CharField(max_length=255)
    authors = models.TextField()
    subjects = models.TextField()
    locc = models.CharField(max_length=255, verbose_name="LoCC")
    bookshelves = models.TextField()

class IndexTable(models.Model):
    book = models.ForeignKey('Book', on_delete=models.CASCADE, related_name='index_metrics')
    word = models.ForeignKey('Word', on_delete=models.CASCADE, related_name='metrics')
    betweenness_centrality = models.FloatField(default=0.0)
    closeness_centrality = models.FloatField(default=0.0)
    pagerank = models.FloatField(default=0.0)

    class Meta:
        unique_together = ('book', 'word')

    def __str__(self):
        return f"{self.word.word} in {self.book.title}"


class Word(models.Model):
    word = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.word

class WordFrequencies(models.Model):
    book = models.ForeignKey('Book', on_delete=models.CASCADE, related_name='word_frequencies')
    word = models.ForeignKey('Word', on_delete=models.CASCADE, related_name='frequencies')
    frequency = models.IntegerField()

    class Meta:
        unique_together = ('book', 'word')

class WordPositions(models.Model):
    book = models.ForeignKey('Book', on_delete=models.CASCADE, related_name='word_positions')
    word = models.ForeignKey('Word', on_delete=models.CASCADE, related_name='positions')
    positions = ArrayField(models.IntegerField(), default=list)

    class Meta:
        unique_together = ('book', 'word')

class AdjacencyList(models.Model):
    book = models.OneToOneField(Book, on_delete=models.CASCADE, primary_key=True)
    adjacent_book_ids = ArrayField(models.IntegerField())

class EdgeList(models.Model):
    source_book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='source_edges')
    target_book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='target_edges')
    weight = models.FloatField(default=1.0)