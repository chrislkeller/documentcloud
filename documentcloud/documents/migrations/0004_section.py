# Generated by Django 2.2.5 on 2019-09-25 19:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0003_auto_20190925_1848'),
    ]

    operations = [
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('page_number', models.IntegerField(help_text='Which page this section appears on', verbose_name='page number')),
                ('title', models.TextField(help_text='A title for the section', verbose_name='title')),
                ('document', models.ForeignKey(help_text='The document this section belongs to', on_delete=django.db.models.deletion.CASCADE, related_name='sections', to='documents.Document', verbose_name='document')),
            ],
        ),
    ]