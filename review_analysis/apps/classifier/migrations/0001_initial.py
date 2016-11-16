# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-11-06 13:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LabeledData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asin', models.TextField()),
                ('review_text', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Sentiment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sentiment_id', models.PositiveIntegerField()),
                ('sentiment', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='labeleddata',
            name='sentiment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='classifier.Sentiment'),
        ),
    ]
