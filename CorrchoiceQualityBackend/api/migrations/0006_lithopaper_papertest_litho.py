# Generated by Django 4.2.13 on 2025-02-12 19:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_combinedboardtestlayer_unique_code_plant_combined_board_test_layer_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='LithoPaper',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('litho_uuid', models.CharField(max_length=11, unique=True)),
                ('litho', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='api.litho')),
                ('plant', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='api.plant')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='papertest',
            name='litho',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.lithopaper'),
        ),
    ]
