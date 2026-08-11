from django.shortcuts import render, redirect
from .forms import QuoteForm
from .models import Quote


def calculate_quote(distance, vehicle_type):

    rates = {
        "sedan": 0.55,
        "suv": 0.65,
        "truck": 0.75,
    }

    rate = rates.get(vehicle_type.lower(), 0.60)

    price = float(distance) * rate

    return round(price, 2)


def home(request):

    if request.method == "POST":

        pickup_city = request.POST.get("pickup_city")
        delivery_city = request.POST.get("delivery_city")
        vehicle_type = request.POST.get("vehicle_type")
        pickup_date = request.POST.get("pickup_date")
        distance = request.POST.get("distance")


        print("------------------------------------------------------------------------------------------",pickup_date)
        # Make sure distance exists
        if not distance:
            return redirect("home")

        # Calculate quote
        quote_price = calculate_quote(
            distance,
            vehicle_type
        )

        # Store temporary data in session
        request.session["quote"] = {
            "pickup_city": pickup_city,
            "delivery_city": delivery_city,
            "vehicle_type": vehicle_type,
            "pickup_date": pickup_date,
            "distance": distance,
            "quote_price": quote_price,
        }




        return redirect("quote_details")

    return render(request, "index.html")


def quote_details(request):

    quote_data = request.session.get("quote")

    if not quote_data:
        return redirect("home")

    if request.method == "POST":

        form = QuoteForm(request.POST)

        if form.is_valid():

            quote = form.save(commit=False)

            # =========================
            # DATA FROM SESSION
            # =========================

            quote.pickup_city = quote_data.get("pickup_city")
            quote.delivery_city = quote_data.get("delivery_city")
            quote.vehicle_type = quote_data.get("vehicle_type")
            quote.pickup_date = quote_data.get("pickup_date")
            quote.distance = quote_data.get("distance")
            quote.quote_price = quote_data.get("quote_price")

            # =========================
            # SAVE EVERYTHING
            # =========================

            quote.save()

            # Optional: clear session after saving
            # request.session.pop("quote", None)

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

def quote_success(request, quote_id):

    quote = Quote.objects.get(id=quote_id)

    return render(
        request,
        "quote-success.html",
        {
            "quote": quote
        }
    )