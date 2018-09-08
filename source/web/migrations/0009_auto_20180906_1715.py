# Generated by Django 2.0 on 2018-09-06 12:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0008_auto_20180906_1644'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contest',
            name='xp',
        ),
        migrations.AlterField(
            model_name='contest',
            name='second_user',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='second_user', to='web.Contestant'),
        ),
    ]
