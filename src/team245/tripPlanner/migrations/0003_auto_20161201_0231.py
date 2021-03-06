# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-01 02:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tripPlanner', '0002_auto_20161201_0210'),
    ]

    operations = [
        migrations.RenameField(
            model_name='attraction',
            old_name='attr_reference',
            new_name='tag',
        ),
        migrations.RemoveField(
            model_name='attraction',
            name='formatted_phone_number',
        ),
        migrations.RemoveField(
            model_name='attraction',
            name='international_phone_number',
        ),
        migrations.RemoveField(
            model_name='attraction',
            name='map_url',
        ),
        migrations.AddField(
            model_name='attraction',
            name='price',
            field=models.CharField(max_length=5, null=True),
        ),
        migrations.AlterField(
            model_name='attraction',
            name='rating',
            field=models.CharField(max_length=5, null=True),
        ),
    ]
