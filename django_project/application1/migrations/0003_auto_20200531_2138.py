# Generated by Django 3.0.6 on 2020-05-31 19:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application1', '0002_auto_20200523_2002'),
    ]

    operations = [
        migrations.CreateModel(
            name='KML_File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255)),
                ('file', models.FileField(upload_to='')),
            ],
        ),
        migrations.AddField(
            model_name='line_string',
            name='personel_id',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
