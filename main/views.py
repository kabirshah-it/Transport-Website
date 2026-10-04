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


LOCATION_FILE = (
    settings.BASE_DIR
    / "static"
    / "assets"
    / "data"
    / "usa_locations_optimized.json"
)


@lru_cache(maxsize=1)
def load_locations():
    try:
        with open(LOCATION_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError("Location database must contain a JSON object.")

        return data

    except FileNotFoundError:
        raise RuntimeError(
            f"Location database not found: {LOCATION_FILE}"
        )

    except json.JSONDecodeError as error:
        raise RuntimeError(
            f"Location database contains invalid JSON: {error}"
        )


def extract_zip(location_text):
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


def get_valid_location(location_text):
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

    except (KeyError, TypeError, ValueError):
        return None

    if not (-90 <= lat <= 90 and -180 <= lng <= 180):
        return None

    return {
        "zip": zip_code,
        "city": city,
        "state": state,
        "lat": lat,
        "lng": lng,
    }


def format_location(location):
    return f"{location['city']}, {location['state']} {location['zip']}"


def calculate_distance(pickup_location, delivery_location):
    lat1 = math.radians(pickup_location["lat"])
    lon1 = math.radians(pickup_location["lng"])

    lat2 = math.radians(delivery_location["lat"])
    lon2 = math.radians(delivery_location["lng"])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    earth_radius_miles = 3958.7613

    distance = earth_radius_miles * c

    return round(distance)


def calculate_quote(distance, vehicle_type):
    """
    Calculate the shipping price using the fixed-price system.

    The distance is used ONLY to select the correct distance bracket.

    There is NO active distance × rate calculation.

    The old per-mile pricing system is kept below as comments
    in case we want to use it again later.
    """

    # ============================================================
    # VEHICLE CATEGORIES
    # ============================================================

    vehicle_categories = {

        # STANDARD VEHICLES
        "sedan": "standard",
        "motorcycle": "standard",
        "convertible": "standard",
        "coupe": "standard",
        "wagon": "standard",

        # LARGER VEHICLES
        "suv": "larger",
        "van": "larger",
        "classic": "larger",

        # COMMERCIAL VEHICLES
        "pickup": "commercial",
        "commercial-truck": "commercial",
    }


    # ============================================================
    # FIXED PRICING
    # ============================================================

    fixed_prices = {

        # --------------------------------------------------------
        # STANDARD
        # Sedan
        # Motorcycle
        # Convertible
        # Coupe
        # Wagon
        # --------------------------------------------------------

        "standard": [
            (0, 50, 200),
            (51, 100, 250),
            (101, 150, 300),
            (151, 200, 350),
            (201, 250, 400),
            (251, 300, 400),
            (301, 350, 450),
            (351, 400, 550),
            (401, 500, 700),
            (501, 600, 800),
            (601, 800, 950),
            (801, 1000, 1000),
            (1001, 1200, 1100),
            (1201, 1300, 1200),
            (1301, 1500, 1300),
            (1501, 1800, 1400),
            (1801, 2000, 1600),
            (2001, 2500, 1800),
            (2501, 3000, 2000),
        ],


        # --------------------------------------------------------
        # LARGER
        # SUV
        # Van
        # Classic Car
        # --------------------------------------------------------

        "larger": [
            (0, 50, 200),
            (51, 100, 250),
            (101, 150, 350),
            (151, 200, 400),
            (201, 250, 420),
            (251, 300, 420),
            (301, 350, 450),
            (351, 400, 550),
            (401, 500, 700),
            (501, 600, 800),
            (601, 800, 950),
            (801, 1000, 1000),
            (1001, 1200, 1100),
            (1201, 1300, 1200),
            (1301, 1500, 1300),
            (1501, 1800, 1400),
            (1801, 2000, 1600),
            (2001, 2500, 1800),
            (2501, 3000, 2000),
        ],


        # --------------------------------------------------------
        # COMMERCIAL
        # Pickup
        # Commercial Truck
        # --------------------------------------------------------

        "commercial": [
            (0, 50, 250),
            (51, 100, 300),
            (101, 150, 350),
            (151, 200, 400),
            (201, 250, 420),
            (251, 300, 420),
            (301, 350, 500),
            (351, 400, 600),
            (401, 500, 800),
            (501, 600, 850),
            (601, 800, 1000),
            (801, 1000, 1100),
            (1001, 1200, 1200),
            (1201, 1300, 1400),
            (1301, 1500, 1500),
            (1501, 1800, 1600),
            (1801, 2000, 1800),
            (2001, 2500, 2000),
            (2501, 3000, 2300),
        ],
    }


    # ============================================================
    # VALIDATE VEHICLE TYPE
    # ============================================================

    if not vehicle_type:
        return None

    vehicle_type = str(vehicle_type).strip().lower()

    category = vehicle_categories.get(vehicle_type)

    if not category:
        return None


    # ============================================================
    # VALIDATE DISTANCE
    # ============================================================

    try:
        distance = float(distance)

    except (TypeError, ValueError):
        return None

    if distance < 0:
        return None


    # ============================================================
    # FIND FIXED PRICE
    # ============================================================

    for minimum, maximum, price in fixed_prices[category]:

        if minimum <= distance <= maximum:
            return price


    # ============================================================
    # NO PRICE ABOVE 3000 MILES
    # ============================================================

    return None


    # ============================================================
    # OLD PER-MILE PRICING SYSTEM
    # KEEP COMMENTED FOR FUTURE USE
    # ============================================================

    # rates = {
    #     "sedan": 0.55,
    #     "suv": 0.65,
    #     "pickup": 0.75,
    #     "van": 0.60,
    #     "motorcycle": 0.50,
    #     "convertible": 0.65,
    #     "coupe": 0.60,
    #     "wagon": 0.60,
    #     "minivan": 0.70,
    #     "commercial-truck": 1.00,
    #     "rv": 1.10,
    #     "classic": 0.85,
    # }

    # rate = rates.get(vehicle_type)

    # if rate is None:
    #     return None

    # calculated_price = distance * rate

    # return round(calculated_price, 2)


def home(request):

    if request.method == "POST":

        pickup_city = request.POST.get(
            "pickup_city",
            ""
        ).strip()

        delivery_city = request.POST.get(
            "delivery_city",
            ""
        ).strip()

        vehicle_type = request.POST.get(
            "vehicle_type",
            ""
        ).strip().lower()

        pickup_date = request.POST.get(
            "pickup_date",
            ""
        ).strip()


        # ========================================================
        # VALIDATE PICKUP LOCATION
        # ========================================================

        pickup_location = get_valid_location(pickup_city)

        if not pickup_location:

            messages.error(
                request,
                "Please select a valid pickup ZIP code."
            )

            return redirect("home")


        # ========================================================
        # VALIDATE DELIVERY LOCATION
        # ========================================================

        delivery_location = get_valid_location(delivery_city)

        if not delivery_location:

            messages.error(
                request,
                "Please select a valid delivery ZIP code."
            )

            return redirect("home")


        # ========================================================
        # SAME LOCATION CHECK
        # ========================================================

        if pickup_location["zip"] == delivery_location["zip"]:

            messages.error(
                request,
                "Pickup and delivery locations must be different."
            )

            return redirect("home")


        # ========================================================
        # VALID VEHICLE TYPES
        # ========================================================

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


        # ========================================================
        # CALCULATE DISTANCE
        # ========================================================

        distance = calculate_distance(
            pickup_location,
            delivery_location
        )


        # ========================================================
        # CALCULATE FIXED QUOTE
        # ========================================================

        quote_price = calculate_quote(
            distance,
            vehicle_type
        )


        if quote_price is None:

            messages.error(
                request,
                "Unable to calculate the shipping quote for this vehicle and distance."
            )

            return redirect("home")


        # ========================================================
        # SAVE QUOTE DATA TO SESSION
        # ========================================================

        request.session["quote"] = {

            "pickup_city": format_location(
                pickup_location
            ),

            "delivery_city": format_location(
                delivery_location
            ),

            "pickup_zip": pickup_location["zip"],

            "delivery_zip": delivery_location["zip"],

            "vehicle_type": vehicle_type,

            "pickup_date": pickup_date,

            "distance": distance,

            "quote_price": quote_price,
        }


        return redirect("quote_details")


    return render(
        request,
        "index.html"
    )


def quote_details(request):

    quote_data = request.session.get("quote")


    if not quote_data:

        return redirect("home")


    # ============================================================
    # VALIDATE LOCATIONS AGAIN
    # ============================================================

    pickup_location = get_valid_location(
        quote_data.get("pickup_city")
    )

    delivery_location = get_valid_location(
        quote_data.get("delivery_city")
    )


    if not pickup_location or not delivery_location:

        request.session.pop(
            "quote",
            None
        )

        messages.error(
            request,
            "The shipping locations are no longer valid."
        )

        return redirect("home")


    # ============================================================
    # SAME LOCATION CHECK
    # ============================================================

    if pickup_location["zip"] == delivery_location["zip"]:

        request.session.pop(
            "quote",
            None
        )

        messages.error(
            request,
            "Pickup and delivery locations must be different."
        )

        return redirect("home")


    # ============================================================
    # RECALCULATE DISTANCE
    # ============================================================

    distance = calculate_distance(
        pickup_location,
        delivery_location
    )


    # ============================================================
    # RECALCULATE FIXED QUOTE
    # ============================================================

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


    # ============================================================
    # UPDATE SESSION
    # ============================================================

    quote_data["distance"] = distance

    quote_data["quote_price"] = quote_price

    quote_data["pickup_city"] = format_location(
        pickup_location
    )

    quote_data["delivery_city"] = format_location(
        delivery_location
    )

    request.session["quote"] = quote_data


    # ============================================================
    # SAVE CUSTOMER QUOTE
    # ============================================================

    if request.method == "POST":

        form = QuoteForm(
            request.POST
        )

        if form.is_valid():

            quote = form.save(
                commit=False
            )

            quote.pickup_city = quote_data[
                "pickup_city"
            ]

            quote.delivery_city = quote_data[
                "delivery_city"
            ]

            quote.vehicle_type = quote_data[
                "vehicle_type"
            ]

            quote.pickup_date = quote_data[
                "pickup_date"
            ]

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
        },
    )


def quote_success(request, quote_id):

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


def about(request):

    return render(
        request,
        "about.html"
    )


def services(request):

    return render(
        request,
        "services.html"
    )