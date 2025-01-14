# Generated by Django 3.2.9 on 2022-09-01 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0048_note_solr_dirty'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='delayed_index',
            field=models.BooleanField(default=False, help_text='Do not index the document in Solr immediately - Wait for it to be batched indexed by the dirty indexer. Useful when uploading in bulk to not overwhelm the Celery queue.', verbose_name='delayed index'),
        ),
    ]
