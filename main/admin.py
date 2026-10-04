from django.contrib import admin

from .models import Quote
from .admin_site import transport_admin_site
@admin.register(Quote, site=transport_admin_site)
class QuoteAdmin(admin.ModelAdmin):

    list_display = (
        "customer_name",
        "phone",
        "vehicle",
        "route",
        "transport_type",
        "vehicle_condition",
        "distance_miles",
        "formatted_price",
        "created_at",
    )

    list_filter = (
        "transport_type",
        "vehicle_condition",
        "vehicle_type",
        "created_at",
    )

    search_fields = (
        "first_name",
        "last_name",
        "email",
        "phone",
        "vehicle_make",
        "vehicle_model",
        "pickup_city",
        "delivery_city",
    )

    ordering = ("-created_at",)

    date_hierarchy = "created_at"

    fieldsets = (
        (
            "Customer Information",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "phone",
                )
            },
        ),
        (
            "Vehicle Information",
            {
                "fields": (
                    "vehicle_type",
                    "vehicle_year",
                    "vehicle_make",
                    "vehicle_model",
                )
            },
        ),
        (
            "Shipping Information",
            {
                "fields": (
                    "pickup_date",
                    "transport_type",
                    "vehicle_condition",
                )
            },
        ),
        (
            "Route Information",
            {
                "fields": (
                    "pickup_city",
                    "delivery_city",
                    "pickup_address",
                    "delivery_address",
                    "distance",
                    "quote_price",
                )
            },
        ),
        (
            "Location Coordinates",
            {
                "classes": ("collapse",),
                "fields": (
                    "pickup_lat",
                    "pickup_lng",
                    "delivery_lat",
                    "delivery_lng",
                )
            },
        ),
        (
            "Additional Information",
            {
                "fields": ("notes",)
            },
        ),
        (
            "Record Information",
            {
                "classes": ("collapse",),
                "fields": ("created_at",)
            },
        ),
    )

    @admin.display(description="Customer", ordering="first_name")
    def customer_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    @admin.display(description="Vehicle")
    def vehicle(self, obj):
        return f"{obj.vehicle_year} {obj.vehicle_make} {obj.vehicle_model}"

    @admin.display(description="Route")
    def route(self, obj):
        return f"{obj.pickup_city} → {obj.delivery_city}"
        
    @admin.display(description="Distance", ordering="distance")
    def distance_miles(self, obj):
        if obj.distance is None:
            return "—"

        return f"{obj.distance:,.0f} mi"


    @admin.display(description="Quote", ordering="quote_price")
    def formatted_price(self, obj):
        if obj.quote_price is None:
            return "—"

        return f"${obj.quote_price:,.2f}"


admin.site.site_header = "Kabir's Transport"
admin.site.site_title = "Kabir's Transport Admin"
admin.site.index_title = "Transport Management"