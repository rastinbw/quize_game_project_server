# Generated by Django 2.0 on 2018-09-25 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0028_contest_cid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contest',
            name='CID',
            field=models.CharField(blank=True, default=None, max_length=167),
        ),
    ]
