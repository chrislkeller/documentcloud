# Generated by Django 2.2.5 on 2020-02-05 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0011_auto_20200128_1418'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='content',
            field=models.TextField(blank=True, help_text='The contents of the note', verbose_name='content'),
        ),
    ]