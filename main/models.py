from django.db import models


TRANSPORT_CHOICES = [
    ("open", "Open Transport"),
    ("enclosed", "Enclosed Transport"),
]


CONDITION_CHOICES = [
    ("running", "Running Vehicle"),
    ("non_running", "Non-Running Vehicle"),
]


class Quote(models.Model):

    # =========================
    # Customer Information
    # =========================

    first_name = models.CharField(
        max_length=100
    )

    last_name = models.CharField(
        max_length=100
    )

    email = models.EmailField()

    phone = models.CharField(
        max_length=30
    )


    # =========================
    # Vehicle Information
    # =========================

    vehicle_type = models.CharField(
        max_length=100
    )

    vehicle_year = models.CharField(
        max_length=10
    )

    vehicle_make = models.CharField(
        max_length=100
    )

    vehicle_model = models.CharField(
        max_length=100
    )


    # =========================
    # Shipping Information
    # =========================

    pickup_date = models.CharField(
        max_length=100
    )

    transport_type = models.CharField(
        max_length=50,
        choices=TRANSPORT_CHOICES
    )

    vehicle_condition = models.CharField(
        max_length=50,
        choices=CONDITION_CHOICES
    )


    # =========================
    # Location Information
    # =========================

    pickup_city = models.CharField(
        max_length=150
    )

    delivery_city = models.CharField(
        max_length=150
    )

    pickup_address = models.CharField(
        max_length=255,
        blank=True
    )

    delivery_address = models.CharField(
        max_length=255,
        blank=True
    )


    # =========================
    # Route Information
    # =========================

    pickup_lat = models.FloatField(
        null=True,
        blank=True
    )

    pickup_lng = models.FloatField(
        null=True,
        blank=True
    )

    delivery_lat = models.FloatField(
        null=True,
        blank=True
    )

    delivery_lng = models.FloatField(
        null=True,
        blank=True
    )

    distance = models.FloatField(
        null=True,
        blank=True
    )


    # =========================
    # Additional Information
    # =========================

    notes = models.TextField(
        blank=True
    )


    # =========================
    # Auto Fields
    # =========================

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    def __str__(self):
        return f"{self.first_name} {self.last_name}"
