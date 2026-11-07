"""
=============================================================================
SMART PARKING MANAGEMENT SYSTEM - CONTROLLERS & VIEWS (views.py)
=============================================================================
Beginner Guide to Django Views:
In Django's MVT (Model-View-Template) pattern:
- A "View" is a Python function that takes a Web Request (`HttpRequest`)
  and returns a Web Response (`HttpResponse` or rendered HTML).
- It retrieves data from your Models (Database), applies business logic,
  and packages that data into a Python dictionary called "context" to pass
  to the Template (HTML file).
=============================================================================
"""

import json
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Q, Sum

from .models import ParkingSlot, Booking
from .forms import BookingForm, CancelBookingForm, ParkingSlotForm


# =============================================================================
# USER SIDE: 1. HOME & LIVE PARKING BAY GRID
# =============================================================================
def home_view(request):
    """
    Renders the public dashboard showing all parking slots with their live status.
    Supports filtering by Floor/Zone and Vehicle Type.
    
    Beginner explanation:
    `request.GET.get('param')` grabs query parameters from URL:
    e.g. `/ ?zone=Ground+Floor &status=AVAILABLE`
    """
    # Base QuerySet: All slots ordered by slot number
    slots = ParkingSlot.objects.all().order_by('slot_number')

    # Get optional search/filter values from the URL query string
    zone_filter = request.GET.get('zone', '').strip()
    status_filter = request.GET.get('status', '').strip()
    vehicle_filter = request.GET.get('vehicle', '').strip()

    if zone_filter:
        slots = slots.filter(floor_zone=zone_filter)
    if status_filter:
        slots = slots.filter(status=status_filter)
    if vehicle_filter:
        slots = slots.filter(vehicle_type=vehicle_filter)

    # Compute Live Real-time Statistics
    total_slots = ParkingSlot.objects.count()
    available_slots = ParkingSlot.objects.filter(status=ParkingSlot.STATUS_AVAILABLE).count()
    occupied_slots = ParkingSlot.objects.filter(status=ParkingSlot.STATUS_OCCUPIED).count()
    maintenance_slots = ParkingSlot.objects.filter(status=ParkingSlot.STATUS_MAINTENANCE).count()

    # Calculate occupancy percentage safely
    occupancy_rate = 0
    if total_slots > 0:
        occupancy_rate = round((occupied_slots / total_slots) * 100, 1)

    # Empty booking form for the modal popup
    booking_form = BookingForm()

    # Get distinct floor zones for filter tabs
    all_zones = [choice[0] for choice in ParkingSlot.FLOOR_CHOICES]

    context = {
        'slots': slots,
        'total_slots': total_slots,
        'available_slots': available_slots,
        'occupied_slots': occupied_slots,
        'maintenance_slots': maintenance_slots,
        'occupancy_rate': occupancy_rate,
        'booking_form': booking_form,
        'all_zones': all_zones,
        'selected_zone': zone_filter,
        'selected_status': status_filter,
        'selected_vehicle': vehicle_filter,
    }
    return render(request, 'parking/home.html', context)


# =============================================================================
# USER SIDE: 2. BOOK AN AVAILABLE SLOT
# =============================================================================
def book_slot_view(request, slot_id=None):
    """
    Handles slot booking.
    Can be loaded directly with a pre-selected slot: `/book/<slot_id>/`
    or directly via `/book/`.
    
    Senior Dev Concept: `transaction.atomic()` & `select_for_update()`
    When multiple users try to book the exact same slot at the same second,
    `select_for_update()` places an exclusive row-level lock in SQL. This guarantees
    ZERO race conditions and ZERO double-bookings!
    """
    preselected_slot = None
    if slot_id:
        preselected_slot = get_object_or_404(ParkingSlot, id=slot_id)

    if request.method == 'POST':
        form = BookingForm(request.POST)

        if form.is_valid():
            slot = form.cleaned_data['slot']

            try:
                # Begin Database Transaction with Row Lock
                with transaction.atomic():
                    # Re-fetch slot with lock to ensure it's still available
                    locked_slot = ParkingSlot.objects.select_for_update().get(id=slot.id)

                    if locked_slot.status != ParkingSlot.STATUS_AVAILABLE:
                        messages.error(
                            request,
                            f"Uh oh! Slot {locked_slot.slot_number} was just booked by someone else! Please pick another."
                        )
                        return redirect('parking:home')

                    # Save the new booking
                    booking = form.save(commit=False)
                    booking.slot = locked_slot
                    # Calculate cost: hourly rate * duration
                    booking.estimated_cost = Decimal(booking.duration_hours) * locked_slot.hourly_rate
                    booking.save()

                    # Immediately mark slot as OCCUPIED
                    locked_slot.status = ParkingSlot.STATUS_OCCUPIED
                    locked_slot.save()

                messages.success(
                    request,
                    f"Success! Bay {locked_slot.slot_number} has been reserved. Reference ID: {booking.booking_reference}"
                )
                return redirect('parking:booking_confirmation', reference=booking.booking_reference)

            except Exception as e:
                messages.error(request, f"Booking transaction failed: {str(e)}")
        else:
            messages.error(request, "Please review the form errors below and correct invalid inputs.")
    else:
        # GET request: Initialize form with initial values if slot selected
        initial_data = {}
        if preselected_slot:
            initial_data['slot'] = preselected_slot
            initial_data['vehicle_type'] = preselected_slot.vehicle_type
        form = BookingForm(initial=initial_data)

    context = {
        'form': form,
        'preselected_slot': preselected_slot,
    }
    return render(request, 'parking/book_slot.html', context)


# =============================================================================
# USER SIDE: 3. BOOKING CONFIRMATION & DIGITAL PASS
# =============================================================================
def booking_confirmation_view(request, reference):
    """
    Displays the digital parking ticket / boarding pass upon successful reservation.
    Shows QR visualization, Slot Bay, Vehicle Plate, In-time, and Cancellation option.
    """
    booking = get_object_or_404(Booking, booking_reference=reference)

    context = {
        'booking': booking,
    }
    return render(request, 'parking/confirmation.html', context)


# =============================================================================
# USER SIDE: 4. CANCEL AN EXISTING BOOKING
# =============================================================================
def cancel_booking_view(request):
    """
    Allows a driver to search for their active booking by Reference ID or Vehicle Plate
    and cancel it. Automatically restores slot status to AVAILABLE.
    """
    searched_booking = None
    form = CancelBookingForm()

    if request.method == 'POST':
        # Check if this is the final confirm cancellation button press
        confirm_ref = request.POST.get('confirm_cancel_ref')
        if confirm_ref:
            booking = get_object_or_404(Booking, booking_reference=confirm_ref, status=Booking.STATUS_ACTIVE)
            booking.cancel_booking()
            messages.success(
                request,
                f"Booking {booking.booking_reference} cancelled successfully! Bay {booking.slot.slot_number} is now free."
            )
            return redirect('parking:home')

        # Otherwise, user is searching for a booking to cancel
        form = CancelBookingForm(request.POST)
        if form.is_valid():
            ref_or_plate = form.cleaned_data['booking_reference']

            # Lookup by either booking reference OR vehicle plate
            searched_booking = Booking.objects.filter(
                Q(booking_reference__iexact=ref_or_plate) | Q(vehicle_number__iexact=ref_or_plate),
                status=Booking.STATUS_ACTIVE
            ).first()

            if not searched_booking:
                messages.warning(
                    request,
                    f"No active reservation found matching '{ref_or_plate}'. Please check your reference code or vehicle number."
                )

    context = {
        'form': form,
        'booking': searched_booking,
    }
    return render(request, 'parking/cancel_booking.html', context)


# =============================================================================
# ADMINISTRATOR SIDE: 1. DASHBOARD & MONITORING
# =============================================================================
def admin_dashboard_view(request):
    """
    Dedicated Executive Admin Portal:
    - Add, view and update parking slots.
    - View all parking bookings and their details.
    - Manage parking-slot availability (toggle free/maintenance/occupied).
    """
    slots = ParkingSlot.objects.all().order_by('slot_number')
    bookings = Booking.objects.select_related('slot').order_by('-booking_time')

    # Booking Filter by status
    status_filter = request.GET.get('booking_status', '')
    if status_filter:
        bookings = bookings.filter(status=status_filter)

    # Search filter by vehicle plate, reference or driver
    search_query = request.GET.get('q', '').strip()
    if search_query:
        bookings = bookings.filter(
            Q(vehicle_number__icontains=search_query) |
            Q(driver_name__icontains=search_query) |
            Q(booking_reference__icontains=search_query) |
            Q(slot__slot_number__icontains=search_query)
        )

    # KPI Metrics
    total_slots = slots.count()
    available_slots = slots.filter(status=ParkingSlot.STATUS_AVAILABLE).count()
    occupied_slots = slots.filter(status=ParkingSlot.STATUS_OCCUPIED).count()
    maintenance_slots = slots.filter(status=ParkingSlot.STATUS_MAINTENANCE).count()

    total_bookings_count = Booking.objects.count()
    active_bookings_count = Booking.objects.filter(status=Booking.STATUS_ACTIVE).count()
    total_revenue = Booking.objects.aggregate(total=Sum('estimated_cost'))['total'] or Decimal('0.00')

    occupancy_rate = 0
    if total_slots > 0:
        occupancy_rate = round((occupied_slots / total_slots) * 100, 1)

    slot_form = ParkingSlotForm()

    context = {
        'slots': slots,
        'bookings': bookings[:50], # Latest 50 bookings
        'total_slots': total_slots,
        'available_slots': available_slots,
        'occupied_slots': occupied_slots,
        'maintenance_slots': maintenance_slots,
        'occupancy_rate': occupancy_rate,
        'total_bookings_count': total_bookings_count,
        'active_bookings_count': active_bookings_count,
        'total_revenue': total_revenue,
        'slot_form': slot_form,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'parking/admin_dashboard.html', context)


# =============================================================================
# ADMINISTRATOR SIDE: 2. ADD NEW PARKING SLOT
# =============================================================================
def admin_add_slot_view(request):
    """
    Allows the Administrator to add new parking slots to the facility.
    """
    if request.method == 'POST':
        form = ParkingSlotForm(request.POST)
        if form.is_valid():
            new_slot = form.save()
            messages.success(request, f"Parking Bay '{new_slot.slot_number}' successfully created!")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    return redirect('parking:admin_dashboard')


# =============================================================================
# ADMINISTRATOR SIDE: 3. UPDATE / EDIT PARKING SLOT
# =============================================================================
def admin_edit_slot_view(request, slot_id):
    """
    Allows updating slot status, vehicle type, floor zone, and hourly rate.
    """
    slot = get_object_or_404(ParkingSlot, id=slot_id)

    if request.method == 'POST':
        form = ParkingSlotForm(request.POST, instance=slot)
        if form.is_valid():
            form.save()
            messages.success(request, f"Slot '{slot.slot_number}' updated successfully!")
            return redirect('parking:admin_dashboard')
        else:
            messages.error(request, "Failed to update slot. Please check inputs.")
    else:
        form = ParkingSlotForm(instance=slot)

    context = {
        'form': form,
        'slot': slot,
    }
    return render(request, 'parking/admin_edit_slot.html', context)


# =============================================================================
# ADMINISTRATOR SIDE: 4. QUICK TOGGLE SLOT AVAILABILITY
# =============================================================================
def admin_toggle_slot_status(request, slot_id):
    """
    Instant 1-Click Action for Admin:
    Toggles slot status between AVAILABLE and MAINTENANCE (or frees an OCCUPIED slot).
    """
    slot = get_object_or_404(ParkingSlot, id=slot_id)

    if slot.status == ParkingSlot.STATUS_AVAILABLE:
        slot.status = ParkingSlot.STATUS_MAINTENANCE
        messages.info(request, f"Slot {slot.slot_number} marked as UNDER MAINTENANCE.")
    elif slot.status == ParkingSlot.STATUS_MAINTENANCE:
        slot.status = ParkingSlot.STATUS_AVAILABLE
        messages.success(request, f"Slot {slot.slot_number} marked as AVAILABLE.")
    elif slot.status == ParkingSlot.STATUS_OCCUPIED:
        # If admin manually frees an occupied slot, complete any active booking
        active_b = slot.active_booking
        if active_b:
            active_b.complete_booking()
        else:
            slot.status = ParkingSlot.STATUS_AVAILABLE
            slot.save()
        messages.success(request, f"Slot {slot.slot_number} has been manually released to AVAILABLE.")

    slot.save()
    return redirect('parking:admin_dashboard')


# =============================================================================
# ADMINISTRATOR SIDE: 5. COMPLETE BOOKING (VEHICLE EXIT)
# =============================================================================
def admin_complete_booking_view(request, booking_id):
    """
    Admin checks out a vehicle when the driver leaves the parking bay.
    """
    booking = get_object_or_404(Booking, id=booking_id)
    if booking.complete_booking():
        messages.success(request, f"Booking {booking.booking_reference} marked as Completed. Bay {booking.slot.slot_number} is now Available!")
    else:
        messages.warning(request, f"Booking {booking.booking_reference} is not currently active.")
    return redirect('parking:admin_dashboard')


# =============================================================================
# LIVE API: SLOTS STATUS (JSON ENDPOINT)
# =============================================================================
def api_slots_status(request):
    """
    Returns JSON of all parking slots.
    Allows frontend JavaScript to poll/auto-refresh without full page reload.
    """
    slots = ParkingSlot.objects.all().values(
        'id', 'slot_number', 'floor_zone', 'vehicle_type', 'status', 'hourly_rate'
    )
    return JsonResponse({'slots': list(slots)})
