"""
=============================================================================
SMART PARKING MANAGEMENT SYSTEM - DJANGO FORMS (forms.py)
=============================================================================
Beginner Guide to Django Forms:
Django Forms are one of Django's most powerful features. They handle 3 jobs:
1. Rendering HTML input fields (`<input>`, `<select>`) with customizable styling.
2. Validating incoming user submissions (checking required fields, regex, types).
3. Sanitizing data to prevent Cross-Site Scripting (XSS) and SQL injection.

A `ModelForm` automatically creates form fields based on your database Model!
=============================================================================
"""

import re
from decimal import Decimal
from django import forms
from django.core.exceptions import ValidationError
from .models import ParkingSlot, Booking


class BookingForm(forms.ModelForm):
    """
    Form used by users/drivers to book an available parking slot.
    Automatically ties to the Booking model.
    """

    class Meta:
        model = Booking
        fields = [
            'slot',
            'driver_name',
            'vehicle_number',
            'phone_number',
            'vehicle_type',
            'duration_hours',
        ]
        widgets = {
            'slot': forms.Select(attrs={
                'class': 'w-full px-4 py-3 bg-slate-900/80 border border-slate-700 rounded-xl text-white focus:ring-2 focus:ring-emerald-500 focus:outline-none transition-all',
                'id': 'id_slot_selector'
            }),
            'driver_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-900/80 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:ring-2 focus:ring-emerald-500 focus:outline-none transition-all',
                'placeholder': 'e.g. John Doe / Rajesh Kumar'
            }),
            'vehicle_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-900/80 border border-slate-700 rounded-xl text-white font-mono uppercase tracking-wider placeholder-slate-400 focus:ring-2 focus:ring-emerald-500 focus:outline-none transition-all',
                'placeholder': 'e.g. DL-01-AB-1234 or KA-05-MM-9999'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-900/80 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:ring-2 focus:ring-emerald-500 focus:outline-none transition-all',
                'placeholder': 'e.g. +91 9876543210'
            }),
            'vehicle_type': forms.Select(attrs={
                'class': 'w-full px-4 py-3 bg-slate-900/80 border border-slate-700 rounded-xl text-white focus:ring-2 focus:ring-emerald-500 focus:outline-none transition-all',
                'id': 'id_vehicle_type'
            }),
            'duration_hours': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-900/80 border border-slate-700 rounded-xl text-white focus:ring-2 focus:ring-emerald-500 focus:outline-none transition-all',
                'min': '1',
                'max': '48',
                'value': '2',
                'id': 'id_duration_hours'
            }),
        }

    def __init__(self, *args, **kwargs):
        """
        Custom form initialization:
        Only display slots that are currently AVAILABLE in the dropdown choice list!
        Occupied or maintenance bays must not be bookable.
        """
        super().__init__(*args, **kwargs)
        # Filter dropdown queryset to show only available slots
        self.fields['slot'].queryset = ParkingSlot.objects.filter(status=ParkingSlot.STATUS_AVAILABLE)
        self.fields['slot'].empty_label = "-- Choose an Available Bay --"

    def clean_vehicle_number(self):
        """
        Data Cleaning Method (Senior Dev Pattern):
        Normalizes the vehicle license plate to uppercase and strips whitespace.
        Ensures plate is at least 4 characters long.
        """
        plate = self.cleaned_data.get('vehicle_number', '').strip().upper()
        if len(plate) < 4:
            raise ValidationError("Please enter a valid vehicle license plate number.")
        return plate

    def clean_phone_number(self):
        """Validates phone number contains at least 7 digits."""
        phone = self.cleaned_data.get('phone_number', '').strip()
        digits = re.sub(r'\D', '', phone)
        if len(digits) < 7:
            raise ValidationError("Please provide a valid contact number (at least 7 digits).")
        return phone

    def clean(self):
        """
        Cross-Field Validation:
        Crucial check to prevent race-condition double bookings.
        Verifies the chosen slot hasn't been booked by someone else while this form was open.
        """
        cleaned_data = super().clean()
        slot = cleaned_data.get('slot')

        if slot and slot.status != ParkingSlot.STATUS_AVAILABLE:
            raise ValidationError(
                f"Bay {slot.slot_number} was just booked or is undergoing maintenance! Please pick another slot."
            )
        return cleaned_data


class CancelBookingForm(forms.Form):
    """
    Form to lookup and cancel an active reservation using either:
    1. Booking Reference (e.g. PRK-ABC123)
    OR
    2. Vehicle License Plate (e.g. DL-01-AB-1234)
    """

    booking_reference = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-5 py-4 bg-slate-900/80 border border-slate-700 rounded-xl text-white font-mono uppercase tracking-wider placeholder-slate-500 focus:ring-2 focus:ring-rose-500 focus:outline-none transition-all text-lg',
            'placeholder': 'e.g. PRK-7F2A9C or KA-05-MM-9999'
        }),
        help_text="Enter your Booking Reference ID (PRK-XXXXXX) or Vehicle Number"
    )

    def clean_booking_reference(self):
        return self.cleaned_data.get('booking_reference', '').strip().upper()


class ParkingSlotForm(forms.ModelForm):
    """
    Administrator Form:
    Used in the Admin Dashboard to Add, Edit, or Update parking slot configurations.
    """

    class Meta:
        model = ParkingSlot
        fields = ['slot_number', 'floor_zone', 'vehicle_type', 'status', 'hourly_rate']
        widgets = {
            'slot_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-white focus:ring-2 focus:ring-cyan-500 focus:outline-none uppercase font-mono',
                'placeholder': 'e.g. A-101, EV-05'
            }),
            'floor_zone': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-white focus:ring-2 focus:ring-cyan-500 focus:outline-none'
            }),
            'vehicle_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-white focus:ring-2 focus:ring-cyan-500 focus:outline-none'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-white focus:ring-2 focus:ring-cyan-500 focus:outline-none'
            }),
            'hourly_rate': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-white focus:ring-2 focus:ring-cyan-500 focus:outline-none',
                'step': '5.00'
            }),
        }
