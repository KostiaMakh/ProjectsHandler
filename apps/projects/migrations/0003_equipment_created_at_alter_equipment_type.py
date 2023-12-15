# Generated by Django 4.1.7 on 2023-12-14 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_position_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipment',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='equipment',
            name='type',
            field=models.CharField(choices=[('screen', 'Screen'), ('scraper', 'Scraper'), ('suction_scraper', 'Suction scraper'), ('penstock', 'Penstock'), ('conveyor', 'Conveyor'), ('compactor', 'Compactor'), ('primary_st', 'Primary clarifier'), ('secondary_st', 'secondary clarifier')], max_length=255),
        ),
    ]