# Generated by Django 2.0 on 2018-09-11 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0017_auto_20180911_1708'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shopitem',
            name='item_id',
            field=models.IntegerField(blank=True, primary_key=True, serialize=False),
        ),
    ]
