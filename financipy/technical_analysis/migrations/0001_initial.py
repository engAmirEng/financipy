# Generated by Django 4.2.9 on 2024-01-26 17:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="SymbolModel",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(db_index=True, max_length=63, unique=True)),
            ],
            options={
                "verbose_name": "Symbol",
                "db_table": "symbol",
            },
        ),
        migrations.CreateModel(
            name="OHLCModel",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("csv_file", models.FileField(upload_to="technical_analysis/ohlc")),
                (
                    "symbol",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ohlc_set",
                        to="technical_analysis.symbolmodel",
                    ),
                ),
            ],
            options={
                "verbose_name": "OHLC",
                "db_table": "ohlc",
            },
        ),
    ]
