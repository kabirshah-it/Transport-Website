from django.shortcuts import render, redirect
from .forms import QuoteForm
from .models import Quote

from django.core.mail import send_mail
from django.conf import settings
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
            # Email customer
            send_mail(
                subject="Your Vehicle Shipping Quote",
                message=f"""
                Hello {quote.first_name},

                Thank you for choosing us for your vehicle transportation needs.

                Your quote has been successfully submitted.

                Pickup: {quote.pickup_city}
                Delivery: {quote.delivery_city}
                Vehicle: {quote.vehicle_type}
                Distance: {quote.distance} miles
                Quote Price: ${quote.quote_price}

                We will contact you shortly.

                Thank you,
                Your Transport Company
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[quote.email],
                fail_silently=False,
            )


            # Email you
            send_mail(
                subject=f"New Vehicle Shipping Quote - {quote.first_name} {quote.last_name}",
                message=f"""
                A new vehicle shipping quote has been submitted.

                Customer:
                Name: {quote.first_name} {quote.last_name}
                Email: {quote.email}
                Phone: {quote.phone}

                Shipping Information:
                Pickup: {quote.pickup_city}
                Delivery: {quote.delivery_city}
                Vehicle: {quote.vehicle_type}
                Distance: {quote.distance} miles
                Pickup Date: {quote.pickup_date}

                Quote Price: ${quote.quote_price}
                """,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=["ksmafg1@gmail.com"],
                    fail_silently=False,
            )

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