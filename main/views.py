# from django.shortcuts import render

# Create your views here.
# def main(request):
#     return render(request, 'templates/index.html')

from django.shortcuts import render, redirect
from .models import    Quote
from .forms import QuoteForm


def home(request):

    if request.method == "POST":

        request.session["quote"] = {
            "pickup_city": request.POST.get("pickup_city"),
            "delivery_city": request.POST.get("delivery_city"),
            "vehicle_type": request.POST.get("vehicle_type"),
            "pickup_date": request.POST.get("pickup_date"),
            "distance": request.POST.get("distance"),
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

            # Data from index page
            quote.pickup_city = quote_data.get("pickup_city")
            quote.delivery_city = quote_data.get("delivery_city")
            quote.vehicle_type = quote_data.get("vehicle_type")
            quote.pickup_date = quote_data.get("pickup_date")

            # Distance
            distance = quote_data.get("distance")

            if distance:
                quote.distance = float(distance)

            # Save everything
            quote.save()

            # Remove temporary index data
            request.session.pop("quote", None)

            # Go to success page
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

def quote(request):

    if request.method == "POST":

        form = QuoteForm(request.POST)

        if form.is_valid():

            quote = form.save()

            return redirect(
                "quote-success",
                quote_id=quote.id
            )

    else:

        form = QuoteForm()


    return render(
        request,
        "details.html",
        {
            "form":form
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