"""
=============================================================================
SMART PARKING MANAGEMENT SYSTEM - DATABASE MODELS (models.py)
=============================================================================
Beginner Guide to Django Models:
In Django, a "Model" represents a table in your SQL database (SQLite in our case).
Each Python class below represents a Table, and each attribute inside the class
represents a Column in that table.

Django's Object-Relational Mapper (ORM) automatically translates these Python
classes into SQL commands (`CREATE TABLE`, `INSERT`, `SELECT`, `UPDATE`).
You don't need to write raw SQL by hand!
=============================================================================
"""

import uuid
from decimal import Decimal
from django.db import models
from django.utils import timezone


def generate_booking_reference():
    """
    Helper function to generate a human-readable, unique booking code.
    Example output: 'PRK-7F2A9C'
    
    Why: Instead of exposing raw database numeric IDs (like 1, 2, 3) which are
    guessable and unprofessional, senior developers use unique reference tokens.
    """
    return f"PRK-{uuid.uuid4().hex[:6].upper()}"


class ParkingSlot(models.Model):
    """
    Represents an individual physical parking bay in the parking lot.
    Tracks its identification number, floor level/zone, vehicle suitability,
    hourly pricing, and whether it is currently free or occupied.
    """

    # -------------------------------------------------------------------------
    # Choices: Enum-like tuples that restrict valid values in forms and admin.
    # Format: (DATABASE_STORED_VALUE, HUMAN_READABLE_LABEL)
    # -------------------------------------------------------------------------
    STATUS_AVAILABLE = 'AVAILABLE'
    STATUS_OCCUPIED = 'OCCUPIED'
    STATUS_MAINTENANCE = 'MAINTENANCE'

    SLOT_STATUS_CHOICES = [
        (STATUS_AVAILABLE, 'Available (Green)'),
        (STATUS_OCCUPIED, 'Occupied (Red)'),
        (STATUS_MAINTENANCE, 'Under Maintenance (Gray)'),
    ]

    VEHICLE_CAR = 'CAR'
    VEHICLE_SUV = 'SUV'
    VEHICLE_BIKE = 'BIKE'
    VEHICLE_EV = 'EV'
    VEHICLE_HANDICAP = 'HANDICAP'

    VEHICLE_TYPE_CHOICES = [
        (VEHICLE_CAR, 'Car / Sedan / Hatchback'),
        (VEHICLE_SUV, 'SUV / Large Vehicle'),
        (VEHICLE_BIKE, 'Two Wheeler / Bike'),
        (VEHICLE_EV, 'Electric Vehicle (EV Charger Available)'),
        (VEHICLE_HANDICAP, 'Accessible / Priority Bay'),
    ]

    FLOOR_CHOICES = [
        ('Ground Floor - Zone A', 'Ground Floor - Zone A (Fast Exit)'),
        ('Ground Floor - Zone B', 'Ground Floor - Zone B (Standard)'),
        ('Level 1 - Zone C', 'Level 1 - Zone C (Covered Parking)'),
        ('Level 1 - Zone D', 'Level 1 - Zone D (Long Duration)'),
        ('Basement - Zone E', 'Basement - Zone E (EV Hub)'),
    ]

    # -------------------------------------------------------------------------
    # Model Fields (Database Columns)
    # -------------------------------------------------------------------------
    slot_number = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text="Unique bay identifier, e.g. A-101, B-205, EV-01"
    )

    floor_zone = models.CharField(
        max_length=60,
        choices=FLOOR_CHOICES,
        default='Ground Floor - Zone A',
        help_text="Floor level and zone where this slot is physically located"
    )

    vehicle_type = models.CharField(
        max_length=20,
        choices=VEHICLE_TYPE_CHOICES,
        default=VEHICLE_CAR,
        help_text="Type of vehicle allowed in this bay"
    )

    status = models.CharField(
        max_length=20,
        choices=SLOT_STATUS_CHOICES,
        default=STATUS_AVAILABLE,
        db_index=True,
        help_text="Current state: Available, Occupied, or Under Maintenance"
    )

    hourly_rate = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('50.00'),
        help_text="Parking fee per hour in currency units (e.g. ₹50/hr)"
    )

    # Metadata timestamps for auditing
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['slot_number']
        verbose_name = 'Parking Slot'
        verbose_name_plural = 'Parking Slots'

    def __str__(self):
        """String representation displayed in the Django Admin and debug shells."""
        return f"Slot {self.slot_number} ({self.get_vehicle_type_display()}) - [{self.status}]"

    # -------------------------------------------------------------------------
    # Helper Business-Logic Methods
    # -------------------------------------------------------------------------
    @property
    def is_available(self):
        """Returns True if this slot is ready for immediate booking."""
        return self.status == self.STATUS_AVAILABLE

    @property
    def is_occupied(self):
        """Returns True if a vehicle is parked or actively booked."""
        return self.status == self.STATUS_OCCUPIED

    @property
    def active_booking(self):
        """
        Retrieves the current active booking associated with this slot (if any).
        Uses reverse relation: `self.bookings.filter(...)`.
        """
        return self.bookings.filter(status=Booking.STATUS_ACTIVE).order_by('-booking_time').first()

    def get_icon(self):
        """Returns a FontAwesome icon class corresponding to vehicle type."""
        icons = {
            self.VEHICLE_CAR: 'fa-solid fa-car-side',
            self.VEHICLE_SUV: 'fa-solid fa-truck-pickup',
            self.VEHICLE_BIKE: 'fa-solid fa-motorcycle',
            self.VEHICLE_EV: 'fa-solid fa-bolt-lightning',
            self.VEHICLE_HANDICAP: 'fa-solid fa-wheelchair',
        }
        return icons.get(self.vehicle_type, 'fa-solid fa-square-parking')


class Booking(models.Model):
    """
    Represents a parking reservation created by a driver.
    Links a driver and their vehicle to a specific ParkingSlot.
    """

    STATUS_ACTIVE = 'ACTIVE'
    STATUS_CANCELLED = 'CANCELLED'
    STATUS_COMPLETED = 'COMPLETED'

    BOOKING_STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active / Parked'),
        (STATUS_CANCELLED, 'Cancelled'),
        (STATUS_COMPLETED, 'Completed / Exited'),
    ]

    # Unique human-friendly reference token (e.g. 'PRK-9A1F3B')
    booking_reference = models.CharField(
        max_length=20,
        unique=True,
        default=generate_booking_reference,
        editable=False,
        db_index=True,
        help_text="Unique booking confirmation code"
    )

    # ForeignKey: Establishes a Many-to-One relationship.
    # Many bookings can belong to one parking slot over time.
    slot = models.ForeignKey(
        ParkingSlot,
        on_delete=models.CASCADE,
        related_name='bookings',
        help_text="The physical parking slot allocated to this booking"
    )

    # Driver Details
    driver_name = models.CharField(
        max_length=100,
        help_text="Full name of the vehicle driver"
    )

    vehicle_number = models.CharField(
        max_length=30,
        db_index=True,
        help_text="Registration license plate, e.g. DL-01-AB-1234 or KA-05-MM-9999"
    )

    phone_number = models.CharField(
        max_length=20,
        help_text="Driver contact number for verification and SMS/ticket alerts"
    )

    vehicle_type = models.CharField(
        max_length=20,
        choices=ParkingSlot.VEHICLE_TYPE_CHOICES,
        default=ParkingSlot.VEHICLE_CAR
    )

    # Duration & Financials
    duration_hours = models.PositiveIntegerField(
        default=2,
        help_text="Estimated duration of parking in hours"
    )

    estimated_cost = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Calculated cost (hourly_rate * duration_hours)"
    )

    status = models.CharField(
        max_length=20,
        choices=BOOKING_STATUS_CHOICES,
        default=STATUS_ACTIVE,
        db_index=True
    )

    # Timestamps
    booking_time = models.DateTimeField(
        default=timezone.now,
        help_text="Timestamp when the booking was initiated"
    )

    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when user cancelled the reservation"
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when vehicle exited the parking bay"
    )

    class Meta:
        ordering = ['-booking_time']
        verbose_name = 'Parking Booking'
        verbose_name_plural = 'Parking Bookings'

    def __str__(self):
        return f"[{self.booking_reference}] {self.driver_name} - {self.vehicle_number} (Slot {self.slot.slot_number})"

    def save(self, *args, **kwargs):
        """
        Senior Dev Override:
        1. Always normalize vehicle registration to clean uppercase (e.g., 'dl 01 ab 1234' -> 'DL-01-AB-1234').
        2. Automatically calculate estimated_cost if not already set.
        """
        # Clean license plate
        if self.vehicle_number:
            self.vehicle_number = self.vehicle_number.strip().upper()

        # Calculate estimated cost
        if not self.estimated_cost or self.estimated_cost == Decimal('0.00'):
            rate = self.slot.hourly_rate if self.slot else Decimal('50.00')
            self.estimated_cost = Decimal(self.duration_hours) * rate

        super().save(*args, **kwargs)

    def cancel_booking(self):
        """
        Cancels this booking and automatically marks the associated parking slot
        as AVAILABLE again so other users can immediately book it.
        """
        if self.status == self.STATUS_ACTIVE:
            self.status = self.STATUS_CANCELLED
            self.cancelled_at = timezone.now()
            self.save()

            # Free up the slot
            slot = self.slot
            slot.status = ParkingSlot.STATUS_AVAILABLE
            slot.save()
            return True
        return False

    def complete_booking(self):
        """
        Marks booking as completed when driver exits the facility.
        Frees up the slot for incoming drivers.
        """
        if self.status == self.STATUS_ACTIVE:
            self.status = self.STATUS_COMPLETED
            self.completed_at = timezone.now()
            self.save()

            slot = self.slot
            slot.status = ParkingSlot.STATUS_AVAILABLE
            slot.save()
            return True
        return False
