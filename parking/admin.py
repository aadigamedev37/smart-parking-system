"""
=============================================================================
SMART PARKING MANAGEMENT SYSTEM - DJANGO ADMIN CONFIG (admin.py)
=============================================================================
Beginner Guide to Django Admin:
Django comes with an automatic, production-ready backend administration site.
By registering our models with custom `ModelAdmin` classes, we get:
- Search bars, date filters, and multi-field dropdown filters.
- Bulk actions (e.g. mark 10 slots as under maintenance at once).
- Custom colored badges and formatted displays.
=============================================================================
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import ParkingSlot, Booking


@admin.register(ParkingSlot)
class ParkingSlotAdmin(admin.ModelAdmin):
    """
    Customizes how Parking Slots appear in the built-in Django Admin (`/admin/`).
    """
    list_display = (
        'slot_number',
        'floor_zone',
        'vehicle_type',
        'colored_status',
        'hourly_rate',
        'created_at',
    )
    list_filter = ('status', 'vehicle_type', 'floor_zone')
    search_fields = ('slot_number', 'floor_zone')
    list_editable = ('hourly_rate',)
    ordering = ('slot_number',)

    # Custom Admin Actions
    actions = ['make_available', 'make_maintenance']

    @admin.display(description='Live Status')
    def colored_status(self, obj):
        """Displays status as a modern colored pill badge."""
        colors = {
            ParkingSlot.STATUS_AVAILABLE: 'background:#10b981; color:#ffffff;',
            ParkingSlot.STATUS_OCCUPIED: 'background:#ef4444; color:#ffffff;',
            ParkingSlot.STATUS_MAINTENANCE: 'background:#64748b; color:#ffffff;',
        }
        style = colors.get(obj.status, 'background:#334155; color:#ffffff;')
        return format_html(
            '<span style="padding:4px 10px; border-radius:9999px; font-weight:600; font-size:11px; {}">{}</span>',
            style,
            obj.get_status_display()
        )

    @admin.action(description='Mark selected slots as AVAILABLE')
    def make_available(self, request, queryset):
        rows_updated = queryset.update(status=ParkingSlot.STATUS_AVAILABLE)
        self.message_user(request, f"{rows_updated} slot(s) successfully marked as Available.")

    @admin.action(description='Mark selected slots as UNDER MAINTENANCE')
    def make_maintenance(self, request, queryset):
        rows_updated = queryset.update(status=ParkingSlot.STATUS_MAINTENANCE)
        self.message_user(request, f"{rows_updated} slot(s) marked as Under Maintenance.")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """
    Customizes how Bookings appear in the built-in Django Admin.
    """
    list_display = (
        'booking_reference',
        'driver_name',
        'vehicle_number',
        'slot_link',
        'duration_hours',
        'estimated_cost',
        'colored_booking_status',
        'booking_time',
    )
    list_filter = ('status', 'vehicle_type', 'booking_time')
    search_fields = ('booking_reference', 'driver_name', 'vehicle_number', 'phone_number')
    readonly_fields = ('booking_reference', 'booking_time', 'cancelled_at', 'completed_at')
    ordering = ('-booking_time',)

    @admin.display(description='Slot')
    def slot_link(self, obj):
        return f"Bay {obj.slot.slot_number}"

    @admin.display(description='Status')
    def colored_booking_status(self, obj):
        colors = {
            Booking.STATUS_ACTIVE: 'background:#0ea5e9; color:#ffffff;',
            Booking.STATUS_CANCELLED: 'background:#f43f5e; color:#ffffff;',
            Booking.STATUS_COMPLETED: 'background:#10b981; color:#ffffff;',
        }
        style = colors.get(obj.status, 'background:#475569; color:#ffffff;')
        return format_html(
            '<span style="padding:4px 10px; border-radius:9999px; font-weight:600; font-size:11px; {}">{}</span>',
            style,
            obj.get_status_display()
        )
