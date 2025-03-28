# Generated by Django 5.1.7 on 2025-03-27 20:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("demo_app", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="prospect",
            name="password",
            field=models.CharField(default="demo123", max_length=255),
        ),
        migrations.AddField(
            model_name="prospect",
            name="username",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.CreateModel(
            name="Appointment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("customer_name", models.CharField(max_length=255)),
                (
                    "customer_email",
                    models.EmailField(blank=True, max_length=254, null=True),
                ),
                ("customer_phone", models.CharField(max_length=20)),
                ("service_type", models.CharField(max_length=100)),
                ("service_address", models.CharField(blank=True, max_length=255)),
                ("notes", models.TextField(blank=True)),
                ("appointment_date", models.DateField()),
                ("appointment_time_slot", models.CharField(max_length=50)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("confirmed", "Confirmed"),
                            ("completed", "Completed"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_demo", models.BooleanField(default=False)),
                (
                    "prospect",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="appointments",
                        to="demo_app.prospect",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ChatMessage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "sender_type",
                    models.CharField(
                        choices=[
                            ("customer", "Customer"),
                            ("business", "Business"),
                            ("system", "System"),
                        ],
                        max_length=20,
                    ),
                ),
                ("sender_name", models.CharField(blank=True, max_length=255)),
                ("message", models.TextField()),
                ("conversation_id", models.CharField(blank=True, max_length=255)),
                ("is_read", models.BooleanField(default=False)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                ("is_demo", models.BooleanField(default=False)),
                (
                    "prospect",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="chat_messages",
                        to="demo_app.prospect",
                    ),
                ),
            ],
        ),
    ]
