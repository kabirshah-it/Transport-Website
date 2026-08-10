
from django import forms
from .models import Quote


class QuoteForm(forms.ModelForm):

    class Meta:

        model = Quote

        fields = [
            # Customer Information
            "first_name",
            "last_name",
            "email",
            "phone",

            # Vehicle Information
            "vehicle_year",
            "vehicle_make",
            "vehicle_model",

            # Shipping Information
            "transport_type",
            "vehicle_condition",

            # Location Information
            "pickup_address",
            "delivery_address",

            # Additional Information
            "notes",
        ]


        widgets = {

            # =========================
            # Customer Information
            # =========================

            "first_name": forms.TextInput(attrs={
                "class": "custom-input",
                "placeholder": "First Name",
                "required": True
            }),

            "last_name": forms.TextInput(attrs={
                "class": "custom-input",
                "placeholder": "Last Name",
                "required": True
            }),

            "email": forms.EmailInput(attrs={
                "class": "custom-input",
                "placeholder": "Email Address",
                "required": True
            }),

            "phone": forms.TextInput(attrs={
                "class": "custom-input",
                "placeholder": "Phone Number",
                "required": True
            }),


            # =========================
            # Vehicle Information
            # =========================

            "vehicle_year": forms.TextInput(attrs={
                "class": "custom-input",
                "placeholder": "Vehicle Year",
                "required": True
            }),

            "vehicle_make": forms.TextInput(attrs={
                "class": "custom-input",
                "placeholder": "Vehicle Make",
                "required": True
            }),

            "vehicle_model": forms.TextInput(attrs={
                "class": "custom-input",
                "placeholder": "Vehicle Model",
                "required": True
            }),


            # =========================
            # Shipping Information
            # =========================

            "transport_type": forms.Select(attrs={
                "class": "custom-input",
                "required": True
            }),

            "vehicle_condition": forms.Select(attrs={
                "class": "custom-input",
                "required": True
            }),


            # =========================
            # Location Information
            # =========================

            "pickup_address": forms.TextInput(attrs={
                "class": "custom-input",
                "id": "pickup_address",
                "placeholder": "Pickup Address",
                "required": True
            }),

            "delivery_address": forms.TextInput(attrs={
                "class": "custom-input",
                "id": "delivery_address",
                "placeholder": "Delivery Address",
                "required": True
            }),


            # =========================
            # Additional Information
            # =========================

            "notes": forms.Textarea(attrs={
                "class": "custom-input",
                "placeholder": "Additional Notes",
                "rows": 3
            }),
        }
