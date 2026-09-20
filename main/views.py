from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages

from .forms import QuoteForm
from .models import Quote

import json
import math
import re
from functools import lru_cache


# ============================================================
# LOCATION DATA
# ============================================================

LOCATION_FILE = (
    settings.BASE_DIR
    / "static"
    / "assets"
    / "data"
    / "usa_locations_optimized.json"
)


@lru_cache(maxsize=1)
def load_locations():
    """
    Load the ZIP/location database once and keep it in memory.

    This avoids reading the 2.4 MB JSON file on every request.
    """

    try:
        with open(
            LOCATION_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError(
                "Location database must contain a JSON object."
            )

        return data

    except FileNotFoundError:

        raise RuntimeError(
            f"Location database not found: {LOCATION_FILE}"
        )

    except json.JSONDecodeError as error:

        raise RuntimeError(
            f"Location database contains invalid JSON: {error}"
        )


# ============================================================
# EXTRACT ZIP CODE
# ============================================================

def extract_zip(location_text):
    """
    Extract a 5-digit ZIP code from a location string.

    Example:
        Miami, FL 33101
        Houston, TX 77001

    Returns:
        '33101'
        '77001'

    Returns None if no valid ZIP is found.
    """

    if not location_text:
        return None

    location_text = str(location_text).strip()

    match = re.search(
        r"\b(\d{5})(?:-\d{4})?\b",
        location_text
    )

    if not match:
        return None

    return match.group(1)


# ============================================================
# VALIDATE LOCATION
# ============================================================

def get_valid_location(location_text):
    """
    Validate a submitted location against the official
    server-side ZIP database.

    Returns:
        {
            'zip': '33101',
            'city': 'Miami',
            'state': 'FL',
            'lat': 25.7743,
            'lng': -80.1937
        }

    Returns None if invalid.
    """

    zip_code = extract_zip(location_text)

    if not zip_code:
        return None

    locations = load_locations()

    location = locations.get(zip_code)

    if not location:
        return None

    try:

        city = str(location["city"]).strip()
        state = str(location["state"]).strip()

        lat = float(location["lat"])
        lng = float(location["lng"])

    except (
        KeyError,
        TypeError,
        ValueError
    ):

        return None

    # Reject invalid coordinates in the database.
    if not (
        -90 <= lat <= 90
        and
        -180 <= lng <= 180
    ):
        return None

    return {
        "zip": zip_code,
        "city": city,
        "state": state,
        "lat": lat,
        "lng": lng,
    }


# ============================================================
# CANONICAL LOCATION DISPLAY
# ============================================================

def format_location(location):
    """
    Create the official location string used by the application.
    """

    return (
        f"{location['city']}, "
        f"{location['state']} "
        f"{location['zip']}"
    )


# ============================================================
# DISTANCE CALCULATION
# ============================================================

def calculate_distance(
    pickup_location,
    delivery_location
):
    """
    Calculate great-circle distance in miles.

    This follows the same type of calculation used by
    Turf's distance(..., units='miles') on the frontend.
    """

    lat1 = math.radians(
        pickup_location["lat"]
    )

    lon1 = math.radians(
        pickup_location["lng"]
    )

    lat2 = math.radians(
        delivery_location["lat"]
    )

    lon2 = math.radians(
        delivery_location["lng"]
    )

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        +
        math.cos(lat1)
        *
        math.cos(lat2)
        *
        math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    # Earth's mean radius in miles.
    earth_radius_miles = 3958.7613

    distance = (
        earth_radius_miles * c
    )

    return round(distance)


# ============================================================
# QUOTE CALCULATION
# ============================================================

def calculate_quote(
    distance,
    vehicle_type
):

    # ========================================================
    # PER-MILE RATES FOR TRIPS OVER 200 MILES
    # ========================================================

    rates = {
        "sedan": 0.55,
        "suv": 0.65,
        "pickup": 0.75,
        "van": 0.60,
        "motorcycle": 0.50,
        "convertible": 0.65,
        "coupe": 0.60,
        "wagon": 0.60,
        "minivan": 0.70,
        "commercial-truck": 1.00,
        "rv": 1.10,
        "classic": 0.85,
    }

    # ========================================================
    # FIXED PRICES FOR 0–200 MILES
    # ========================================================

    fixed_prices = {

        "sedan": {
            "0-50": 80,
            "51-100": 120,
            "101-150": 150,
            "151-200": 250,
        },

        "suv": {
            "0-50": 80,
            "51-100": 120,
            "101-150": 180,
            "151-200": 250,
        },

        "pickup": {
            "0-50": 80,
            "51-100": 120,
            "101-150": 180,
            "151-200": 250,
        },

        "van": {
            "0-50": 80,
            "51-100": 120,
            "101-150": 180,
            "151-200": 250,
        },

        "motorcycle": {
            "0-50": 50,
            "51-100": 100,
            "101-150": 150,
            "151-200": 180,
        },

        "convertible": {
            "0-50": 80,
            "51-100": 100,
            "101-150": 150,
            "151-200": 250,
        },

        "coupe": {
            "0-50": 80,
            "51-100": 100,
            "101-150": 150,
            "151-200": 180,
        },

        "wagon": {
            "0-50": 80,
            "51-100": 100,
            "101-150": 150,
            "151-200": 200,
        },

        "minivan": {
            "0-50": 80,
            "51-100": 100,
            "101-150": 180,
            "151-200": 250,
        },

        "commercial-truck": {
            "0-50": 80,
            "51-100": 100,
            "101-150": 150,
            "151-200": 250,
        },

        "rv": {
            "0-50": 80,
            "51-100": 100,
            "101-150": 150,
            "151-200": 200,
        },

        "classic": {
            "0-50": 80,
            "51-100": 100,
            "101-150": 150,
            "151-200": 200,
        },
    }

    # ========================================================
    # VALIDATE VEHICLE
    # ========================================================

    if not vehicle_type:
        return None

    vehicle_type = (
        str(vehicle_type)
        .strip()
        .lower()
    )

    if vehicle_type not in rates:
        return None

    # ========================================================
    # CONVERT DISTANCE
    # ========================================================

    try:
        distance = float(distance)
    except (
        TypeError,
        ValueError
    ):
        return None

    if distance < 0:
        return None

    # ========================================================
    # FIXED PRICE: 0–50
    # ========================================================

    if distance <= 50:

        return fixed_prices[
            vehicle_type
        ]["0-50"]

    # ========================================================
    # FIXED PRICE: 51–100
    # ========================================================

    elif distance <= 100:

        return fixed_prices[
            vehicle_type
        ]["51-100"]

    # ========================================================
    # FIXED PRICE: 101–150
    # ========================================================

    elif distance <= 150:

        return fixed_prices[
            vehicle_type
        ]["101-150"]

    # ========================================================
    # FIXED PRICE: 151–200
    # ========================================================

    elif distance <= 200:

        return fixed_prices[
            vehicle_type
        ]["151-200"]

    # ========================================================
    # OVER 200 MILES
    # ========================================================

    else:

        rate = rates[vehicle_type]

        calculated_price = (
            distance * rate
        )

        return round(
            calculated_price,
            2
        )


# ============================================================
# HOME
# ============================================================

def home(request):

    if request.method == "POST":

        pickup_city = (
            request.POST.get(
                "pickup_city",
                ""
            ).strip()
        )

        delivery_city = (
            request.POST.get(
                "delivery_city",
                ""
            ).strip()
        )

        vehicle_type = (
            request.POST.get(
                "vehicle_type",
                ""
            ).strip().lower()
        )

        pickup_date = (
            request.POST.get(
                "pickup_date",
                ""
            ).strip()
        )

        # ====================================================
        # VALIDATE PICKUP
        # ====================================================

        pickup_location = get_valid_location(
            pickup_city
        )

        if not pickup_location:

            messages.error(
                request,
                "Please select a valid pickup ZIP code."
            )

            return redirect("home")

        # ====================================================
        # VALIDATE DELIVERY
        # ====================================================

        delivery_location = get_valid_location(
            delivery_city
        )

        if not delivery_location:

            messages.error(
                request,
                "Please select a valid delivery ZIP code."
            )

            return redirect("home")

        # ====================================================
        # PREVENT SAME ZIP
        # ====================================================

        if (
            pickup_location["zip"]
            ==
            delivery_location["zip"]
        ):

            messages.error(
                request,
                "Pickup and delivery locations must be different."
            )

            return redirect("home")

        # ====================================================
        # VALIDATE VEHICLE
        # ====================================================

        valid_vehicle_types = {
            "sedan",
            "suv",
            "pickup",
            "van",
            "motorcycle",
            "convertible",
            "coupe",
            "wagon",
            "minivan",
            "commercial-truck",
            "rv",
            "classic",
        }

        if vehicle_type not in valid_vehicle_types:

            messages.error(
                request,
                "Please select a valid vehicle type."
            )

            return redirect("home")

        # ====================================================
        # CALCULATE DISTANCE SERVER-SIDE
        # ====================================================

        distance = calculate_distance(
            pickup_location,
            delivery_location
        )

        # ====================================================
        # CALCULATE PRICE SERVER-SIDE
        # ====================================================

        quote_price = calculate_quote(
            distance,
            vehicle_type
        )

        if quote_price is None:

            messages.error(
                request,
                "Unable to calculate the shipping quote."
            )

            return redirect("home")

        # ====================================================
        # STORE ONLY TRUSTED DATA
        # ====================================================

        request.session["quote"] = {

            "pickup_city":
                format_location(
                    pickup_location
                ),

            "delivery_city":
                format_location(
                    delivery_location
                ),

            "pickup_zip":
                pickup_location["zip"],

            "delivery_zip":
                delivery_location["zip"],

            "vehicle_type":
                vehicle_type,

            "pickup_date":
                pickup_date,

            "distance":
                distance,

            "quote_price":
                quote_price,
        }

        return redirect(
            "quote_details"
        )

    return render(
        request,
        "index.html"
    )


# ============================================================
# QUOTE DETAILS
# ============================================================

def quote_details(request):

    quote_data = request.session.get(
        "quote"
    )

    if not quote_data:
        return redirect("home")

    # ========================================================
    # RE-VALIDATE SESSION DATA
    # ========================================================

    pickup_location = get_valid_location(
        quote_data.get("pickup_city")
    )

    delivery_location = get_valid_location(
        quote_data.get("delivery_city")
    )

    if (
        not pickup_location
        or not delivery_location
    ):

        request.session.pop(
            "quote",
            None
        )

        messages.error(
            request,
            "The shipping locations are no longer valid."
        )

        return redirect("home")

    # ========================================================
    # PREVENT SAME ZIP
    # ========================================================

    if (
        pickup_location["zip"]
        ==
        delivery_location["zip"]
    ):

        request.session.pop(
            "quote",
            None
        )

        messages.error(
            request,
            "Pickup and delivery locations must be different."
        )

        return redirect("home")

    # ========================================================
    # RECALCULATE DISTANCE
    # ========================================================

    distance = calculate_distance(
        pickup_location,
        delivery_location
    )

    # ========================================================
    # RECALCULATE PRICE
    # ========================================================

    vehicle_type = quote_data.get(
        "vehicle_type"
    )

    quote_price = calculate_quote(
        distance,
        vehicle_type
    )

    if quote_price is None:

        request.session.pop(
            "quote",
            None
        )

        messages.error(
            request,
            "Unable to calculate the shipping quote."
        )

        return redirect("home")

    # ========================================================
    # UPDATE SESSION WITH TRUSTED VALUES
    # ========================================================

    quote_data["distance"] = distance

    quote_data["quote_price"] = quote_price

    quote_data["pickup_city"] = format_location(
        pickup_location
    )

    quote_data["delivery_city"] = format_location(
        delivery_location
    )

    request.session["quote"] = quote_data

    # ========================================================
    # FINAL FORM SUBMISSION
    # ========================================================

    if request.method == "POST":

        form = QuoteForm(
            request.POST
        )

        if form.is_valid():

            quote = form.save(
                commit=False
            )

            # ================================================
            # NEVER TRUST BROWSER PRICE/DISTANCE
            # ================================================

            quote.pickup_city = (
                quote_data["pickup_city"]
            )

            quote.delivery_city = (
                quote_data["delivery_city"]
            )

            quote.vehicle_type = (
                quote_data["vehicle_type"]
            )

            quote.pickup_date = (
                quote_data["pickup_date"]
            )

            quote.distance = distance

            quote.quote_price = quote_price

            quote.save()

            return redirect(
                "quoteSuccess",
                quote_id=quote.id
            )

    else:

        form = QuoteForm()

    return render(
        request,
        "details.html",
        {
            "quote": quote_data,
            "form": form,
        }
    )


# ============================================================
# QUOTE SUCCESS
# ============================================================
def quote_success(
    request,
    quote_id
):

    quote = get_object_or_404(
        Quote,
        id=quote_id
    )

    return render(
        request,
        "quote-success.html",
        {
            "quote": quote
        }
    )


# ============================================================
# ABOUT
# ============================================================

def about(request):

    return render(
        request,
        "about.html"
    )


# ============================================================
# SERVICES
# ============================================================

def services(request):

    return render(
        request,
        "services.html"
    )