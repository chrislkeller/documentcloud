# Generated by Django 3.2.9 on 2022-04-07 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('addons', '0006_auto_20220404_1747'),
    ]

    operations = [
        migrations.AddField(
            model_name='addon',
            name='removed',
            field=models.BooleanField(default=False, help_text='This add-on was removed', verbose_name='removed'),
        ),
        migrations.AlterField(
            model_name='addon',
            name='github_token',
            field=models.CharField(db_column='github_token', help_text="The token to access the add-on's GitHub repository", max_length=40, verbose_name='github token'),
        ),
        migrations.AlterField(
            model_name='addon',
            name='repository',
            field=models.CharField(help_text="The add-on's GitHub repository", max_length=140, unique=True, verbose_name='repository'),
        ),
    ]