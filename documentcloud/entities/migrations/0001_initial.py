# Generated by Django 3.2.9 on 2023-01-30 15:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Entity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.JSONField()),
                ('wikidata_id', models.CharField(max_length=16)),
                ('wikipedia_url', models.JSONField()),
                ('description', models.JSONField()),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('access', models.CharField(choices=[('Public', 0), ('Private', 1)], default='Public', max_length=20)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entities', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]