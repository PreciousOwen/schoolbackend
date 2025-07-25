# Generated by Django 4.2.23 on 2025-06-27 10:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("orders", "0002_order_corporate_account"),
    ]

    operations = [
        migrations.CreateModel(
            name="KitchenQueue",
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
                ("queue_position", models.PositiveIntegerField(default=0)),
                ("estimated_start_time", models.DateTimeField(blank=True, null=True)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["queue_position", "created_at"],
            },
        ),
        migrations.CreateModel(
            name="OrderNote",
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
                ("note", models.TextField()),
                (
                    "is_internal",
                    models.BooleanField(
                        default=True,
                        help_text="Internal staff note or customer-visible",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="OrderStatusHistory",
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
                    "previous_status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("pending", "Pending"),
                            ("confirmed", "Confirmed"),
                            ("preparing", "Preparing"),
                            ("ready", "Ready"),
                            ("served", "Served"),
                            ("paid", "Paid"),
                            ("cancelled", "Cancelled"),
                            ("refunded", "Refunded"),
                        ],
                        max_length=20,
                        null=True,
                    ),
                ),
                (
                    "new_status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("confirmed", "Confirmed"),
                            ("preparing", "Preparing"),
                            ("ready", "Ready"),
                            ("served", "Served"),
                            ("paid", "Paid"),
                            ("cancelled", "Cancelled"),
                            ("refunded", "Refunded"),
                        ],
                        max_length=20,
                    ),
                ),
                ("notes", models.TextField(blank=True)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name_plural": "Order status histories",
                "ordering": ["-timestamp"],
            },
        ),
        migrations.AlterModelOptions(
            name="order",
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddField(
            model_name="order",
            name="actual_prep_time",
            field=models.PositiveIntegerField(
                blank=True, help_text="Actual preparation time in minutes", null=True
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="assigned_chef",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to={"is_staff": True},
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="assigned_orders",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="confirmed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="order",
            name="estimated_prep_time",
            field=models.PositiveIntegerField(
                blank=True, help_text="Estimated preparation time in minutes", null=True
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="is_delivery",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="order",
            name="is_takeout",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="order",
            name="kitchen_notes",
            field=models.TextField(
                blank=True, help_text="Special instructions for kitchen"
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="kitchen_started_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="order",
            name="priority",
            field=models.CharField(
                choices=[("normal", "Normal"), ("high", "High"), ("urgent", "Urgent")],
                default="normal",
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="ready_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="order",
            name="served_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="order",
            name="server",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to={"is_staff": True},
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="served_orders",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("confirmed", "Confirmed"),
                    ("preparing", "Preparing"),
                    ("ready", "Ready"),
                    ("served", "Served"),
                    ("paid", "Paid"),
                    ("cancelled", "Cancelled"),
                    ("refunded", "Refunded"),
                ],
                default="pending",
                max_length=10,
            ),
        ),
        migrations.AddIndex(
            model_name="order",
            index=models.Index(
                fields=["status", "created_at"], name="orders_orde_status_25e057_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="order",
            index=models.Index(
                fields=["customer", "status"], name="orders_orde_custome_c9b64a_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="order",
            index=models.Index(
                fields=["assigned_chef", "status"],
                name="orders_orde_assigne_6402f1_idx",
            ),
        ),
        migrations.AddField(
            model_name="orderstatushistory",
            name="changed_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="orderstatushistory",
            name="order",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="status_history",
                to="orders.order",
            ),
        ),
        migrations.AddField(
            model_name="ordernote",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="ordernote",
            name="order",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="notes",
                to="orders.order",
            ),
        ),
        migrations.AddField(
            model_name="kitchenqueue",
            name="order",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="kitchen_queue",
                to="orders.order",
            ),
        ),
    ]
