
from datetime import timedelta

from django.contrib.admin import AdminSite
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.db.models import Avg
from django.utils import timezone

from .models import Quote


class TransportAdminSite(AdminSite):

    site_header = "Kabir's Transport"
    site_title = "Kabir's Transport Admin"
    index_title = "Transport Management"

    def index(self, request, extra_context=None):

        now = timezone.now()

        today_start = now.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        week_start = today_start - timedelta(days=6)

        quotes = Quote.objects.all()

        total_quotes = quotes.count()

        today_quotes = quotes.filter(
            created_at__gte=today_start
        ).count()

        week_quotes = quotes.filter(
            created_at__gte=week_start
        ).count()

        average_quote = quotes.filter(
            quote_price__isnull=False
        ).aggregate(
            average=Avg("quote_price")
        )["average"] or 0

        recent_quotes = quotes.order_by(
            "-created_at"
        )[:10]

        context = {
            "total_quotes": total_quotes,
            "today_quotes": today_quotes,
            "week_quotes": week_quotes,
            "average_quote": average_quote,
            "recent_quotes": recent_quotes,
        }

        if extra_context:
            context.update(extra_context)

        return super().index(
            request,
            extra_context=context,
        )


transport_admin_site = TransportAdminSite(
    name="transport_admin"
)
# Register Django's built-in user and permission management
transport_admin_site.register(User, UserAdmin)
transport_admin_site.register(Group, GroupAdmin)