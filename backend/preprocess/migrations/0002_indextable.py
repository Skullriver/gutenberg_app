# Generated by Django 5.0.3 on 2024-03-10 21:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('preprocess', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='IndexTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.CharField(max_length=255)),
                ('position', models.IntegerField()),
                ('frequency', models.IntegerField()),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='indexed_words', to='preprocess.book')),
            ],
        ),
    ]
