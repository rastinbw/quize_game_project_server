# Generated by Django 2.0 on 2018-08-14 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0002_auto_20180724_1145'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='barzakh',
            name='experience',
        ),
        migrations.AddField(
            model_name='barzakh',
            name='level',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='barzakh',
            name='xp',
            field=models.IntegerField(default=0),
        ),
    ]