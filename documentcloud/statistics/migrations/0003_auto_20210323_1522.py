# Generated by Django 2.2.5 on 2021-03-23 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('statistics', '0002_auto_20200807_1430'),
    ]

    operations = [
        migrations.AddField(
            model_name='statistics',
            name='total_documents_deleted',
            field=models.IntegerField(default=0, help_text='The total number of deleted documents'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='statistics',
            name='total_documents_error',
            field=models.IntegerField(default=0, help_text='The total number of errored documents'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='statistics',
            name='total_documents_nofile',
            field=models.IntegerField(default=0, help_text='The total number of documents with no file'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='statistics',
            name='total_documents_pending',
            field=models.IntegerField(default=0, help_text='The total number of pending documents'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='statistics',
            name='total_documents_readable',
            field=models.IntegerField(default=0, help_text='The total number of readable documents'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='statistics',
            name='total_documents_success',
            field=models.IntegerField(default=0, help_text='The total number of successful documents'),
            preserve_default=False,
        ),
    ]