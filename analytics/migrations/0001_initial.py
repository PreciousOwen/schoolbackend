# Generated by Django 4.2.23 on 2025-06-27 10:42

from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("menu", "0002_alter_category_options_menuitem_low_stock_threshold_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="DailySummary",
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
                ("date", models.DateField(unique=True)),
                ("total_orders", models.PositiveIntegerField(default=0)),
                ("completed_orders", models.PositiveIntegerField(default=0)),
                ("cancelled_orders", models.PositiveIntegerField(default=0)),
                (
                    "total_revenue",
                    models.DecimalField(
                        decimal_places=2, default=Decimal("0.00"), max_digits=12
                    ),
                ),
                (
                    "avg_order_value",
                    models.DecimalField(
                        decimal_places=2, default=Decimal("0.00"), max_digits=10
                    ),
                ),
                ("total_reservations", models.PositiveIntegerField(default=0)),
                ("completed_reservations", models.PositiveIntegerField(default=0)),
                ("cancelled_reservations", models.PositiveIntegerField(default=0)),
                ("total_covers", models.PositiveIntegerField(default=0)),
                ("new_customers", models.PositiveIntegerField(default=0)),
                ("returning_customers", models.PositiveIntegerField(default=0)),
                (
                    "avg_prep_time",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=6, null=True
                    ),
                ),
                (
                    "table_turnover_rate",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=5, null=True
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["-date"],
            },
        ),
        migrations.CreateModel(
            name="RevenueReport",
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
                    "period_type",
                    models.CharField(
                        choices=[
                            ("daily", "Daily"),
                            ("weekly", "Weekly"),
                            ("monthly", "Monthly"),
                            ("quarterly", "Quarterly"),
                            ("yearly", "Yearly"),
                        ],
                        max_length=20,
                    ),
                ),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                (
                    "food_revenue",
                    models.DecimalField(
                        decimal_places=2, default=Decimal("0.00"), max_digits=12
                    ),
                ),
                (
                    "beverage_revenue",
                    models.DecimalField(
                        decimal_places=2, default=Decimal("0.00"), max_digits=12
                    ),
                ),
                (
                    "total_revenue",
                    models.DecimalField(
                        decimal_places=2, default=Decimal("0.00"), max_digits=12
                    ),
                ),
                (
                    "cost_of_goods",
                    models.DecimalField(
                        decimal_places=2, default=Decimal("0.00"), max_digits=12
                    ),
                ),
                (
                    "gross_profit",
                    models.DecimalField(
                        decimal_places=2, default=Decimal("0.00"), max_digits=12
                    ),
                ),
                (
                    "gross_margin",
                    models.DecimalField(
                        decimal_places=2, default=Decimal("0.00"), max_digits=5
                    ),
                ),
                ("total_orders", models.PositiveIntegerField(default=0)),
                ("total_covers", models.PositiveIntegerField(default=0)),
                (
                    "avg_check_size",
                    models.DecimalField(
                        decimal_places=2, default=Decimal("0.00"), max_digits=10
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-start_date"],
                "unique_together": {("period_type", "start_date", "end_date")},
            },
        ),
        migrations.CreateModel(
            name="CustomerAnalytics",
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
                ("total_orders", models.PositiveIntegerField(default=0)),
                (
                    "total_spent",
                    models.DecimalField(
                        decimal_places=2, default=Decimal("0.00"), max_digits=12
                    ),
                ),
                (
                    "avg_order_value",
                    models.DecimalField(
                        decimal_places=2, default=Decimal("0.00"), max_digits=10
                    ),
                ),
                ("last_order_date", models.DateTimeField(blank=True, null=True)),
                ("total_reservations", models.PositiveIntegerField(default=0)),
                ("last_reservation_date", models.DateTimeField(blank=True, null=True)),
                (
                    "preferred_table_size",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                (
                    "days_since_last_visit",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                (
                    "visit_frequency",
                    models.CharField(
                        choices=[
                            ("daily", "Daily"),
                            ("weekly", "Weekly"),
                            ("monthly", "Monthly"),
                            ("occasional", "Occasional"),
                            ("new", "New Customer"),
                        ],
                        default="new",
                        max_length=20,
                    ),
                ),
                ("favorite_menu_items", models.JSONField(blank=True, default=list)),
                ("preferred_order_times", models.JSONField(blank=True, default=list)),
                (
                    "ltv_score",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                (
                    "churn_risk_score",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=5, null=True
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "customer",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="analytics",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-total_spent"],
            },
        ),
        migrations.CreateModel(
            name="MenuItemAnalytics",
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
                ("date", models.DateField()),
                ("times_ordered", models.PositiveIntegerField(default=0)),
                ("total_quantity", models.PositiveIntegerField(default=0)),
                (
                    "total_revenue",
                    models.DecimalField(
                        decimal_places=2, default=Decimal("0.00"), max_digits=10
                    ),
                ),
                (
                    "avg_rating",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=3, null=True
                    ),
                ),
                ("times_viewed", models.PositiveIntegerField(default=0)),
                (
                    "conversion_rate",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=5, null=True
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "menu_item",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="analytics",
                        to="menu.menuitem",
                    ),
                ),
            ],
            options={
                "ordering": ["-date", "-times_ordered"],
                "unique_together": {("menu_item", "date")},
            },
        ),
        migrations.CreateModel(
            name="AnalyticsEvent",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "event_type",
                    models.CharField(
                        choices=[
                            ("order_created", "Order Created"),
                            ("order_completed", "Order Completed"),
                            ("order_cancelled", "Order Cancelled"),
                            ("payment_completed", "Payment Completed"),
                            ("payment_failed", "Payment Failed"),
                            ("reservation_created", "Reservation Created"),
                            ("reservation_completed", "Reservation Completed"),
                            ("reservation_cancelled", "Reservation Cancelled"),
                            ("user_registered", "User Registered"),
                            ("user_login", "User Login"),
                            ("menu_item_viewed", "Menu Item Viewed"),
                        ],
                        max_length=50,
                    ),
                ),
                ("object_id", models.PositiveIntegerField(blank=True, null=True)),
                ("properties", models.JSONField(blank=True, default=dict)),
                ("session_id", models.CharField(blank=True, max_length=255)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.TextField(blank=True)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "content_type",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="analytics_events",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-timestamp"],
                "indexes": [
                    models.Index(
                        fields=["event_type", "timestamp"],
                        name="analytics_a_event_t_64745b_idx",
                    ),
                    models.Index(
                        fields=["user", "timestamp"],
                        name="analytics_a_user_id_5c8c13_idx",
                    ),
                    models.Index(
                        fields=["timestamp"], name="analytics_a_timesta_aef2a5_idx"
                    ),
                ],
            },
        ),
    ]
