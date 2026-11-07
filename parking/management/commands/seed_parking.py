"""
=============================================================================
DATABASE SEED SCRIPT (manage.py seed_parking)
=============================================================================
Beginner Guide to Management Commands:
In Django, you can create custom CLI commands that can be run with:
`python manage.py <your_command>`

This command populates the database with realistic sample parking slots,
zones, and test bookings so you can present or test the system immediately
without manually entering data!
=============================================================================
"""

from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from parking.models import ParkingSlot, Booking


class Command(BaseCommand):
    help = 'Seeds the database with realistic parking bays and demo bookings'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Flushing old test data and creating fresh slots..."))

        # Clear existing data
        Booking.objects.all().delete()
        ParkingSlot.objects.all().delete()

        # Slot blueprints to create
        slots_data = [
            # Ground Floor - Zone A (Cars, Prime Spot, ₹60/hr)
            {"slot_number": "A-101", "floor_zone": "Ground Floor - Zone A", "vehicle_type": "CAR", "hourly_rate": 60.00},
            {"slot_number": "A-102", "floor_zone": "Ground Floor - Zone A", "vehicle_type": "CAR", "hourly_rate": 60.00},
            {"slot_number": "A-103", "floor_zone": "Ground Floor - Zone A", "vehicle_type": "CAR", "hourly_rate": 60.00},
            {"slot_number": "A-104", "floor_zone": "Ground Floor - Zone A", "vehicle_type": "HANDICAP", "hourly_rate": 40.00},
            {"slot_number": "A-105", "floor_zone": "Ground Floor - Zone A", "vehicle_type": "CAR", "hourly_rate": 60.00},
            {"slot_number": "A-106", "floor_zone": "Ground Floor - Zone A", "vehicle_type": "CAR", "hourly_rate": 60.00},

            # Ground Floor - Zone B (SUVs / Large Vehicles, ₹75/hr)
            {"slot_number": "B-101", "floor_zone": "Ground Floor - Zone B", "vehicle_type": "SUV", "hourly_rate": 75.00},
            {"slot_number": "B-102", "floor_zone": "Ground Floor - Zone B", "vehicle_type": "SUV", "hourly_rate": 75.00},
            {"slot_number": "B-103", "floor_zone": "Ground Floor - Zone B", "vehicle_type": "SUV", "hourly_rate": 75.00},
            {"slot_number": "B-104", "floor_zone": "Ground Floor - Zone B", "vehicle_type": "SUV", "hourly_rate": 75.00},

            # Level 1 - Zone C (Standard Covered Bays, ₹50/hr)
            {"slot_number": "C-201", "floor_zone": "Level 1 - Zone C", "vehicle_type": "CAR", "hourly_rate": 50.00},
            {"slot_number": "C-202", "floor_zone": "Level 1 - Zone C", "vehicle_type": "CAR", "hourly_rate": 50.00},
            {"slot_number": "C-203", "floor_zone": "Level 1 - Zone C", "vehicle_type": "CAR", "hourly_rate": 50.00},
            {"slot_number": "C-204", "floor_zone": "Level 1 - Zone C", "vehicle_type": "CAR", "hourly_rate": 50.00},

            # Level 1 - Zone D (Bikes & Two Wheelers, ₹25/hr)
            {"slot_number": "D-201", "floor_zone": "Level 1 - Zone D", "vehicle_type": "BIKE", "hourly_rate": 25.00},
            {"slot_number": "D-202", "floor_zone": "Level 1 - Zone D", "vehicle_type": "BIKE", "hourly_rate": 25.00},
            {"slot_number": "D-203", "floor_zone": "Level 1 - Zone D", "vehicle_type": "BIKE", "hourly_rate": 25.00},
            {"slot_number": "D-204", "floor_zone": "Level 1 - Zone D", "vehicle_type": "BIKE", "hourly_rate": 25.00},

            # Basement - Zone E (EV Charging Superhub, ₹70/hr)
            {"slot_number": "EV-301", "floor_zone": "Basement - Zone E", "vehicle_type": "EV", "hourly_rate": 70.00},
            {"slot_number": "EV-302", "floor_zone": "Basement - Zone E", "vehicle_type": "EV", "hourly_rate": 70.00},
            {"slot_number": "EV-303", "floor_zone": "Basement - Zone E", "vehicle_type": "EV", "hourly_rate": 70.00},
            {"slot_number": "EV-304", "floor_zone": "Basement - Zone E", "vehicle_type": "EV", "hourly_rate": 70.00},
        ]

        created_slots = {}
        for s in slots_data:
            slot_obj = ParkingSlot.objects.create(
                slot_number=s["slot_number"],
                floor_zone=s["floor_zone"],
                vehicle_type=s["vehicle_type"],
                status=ParkingSlot.STATUS_AVAILABLE,
                hourly_rate=Decimal(str(s["hourly_rate"])),
            )
            created_slots[s["slot_number"]] = slot_obj

        # Mark 1 slot under maintenance
        slot_maint = created_slots["A-106"]
        slot_maint.status = ParkingSlot.STATUS_MAINTENANCE
        slot_maint.save()

        # Create realistic active demo bookings
        demo_bookings = [
            {
                "slot": created_slots["A-102"],
                "driver_name": "Rajesh Sharma",
                "vehicle_number": "DL-03-CC-8421",
                "phone_number": "+91 9811223344",
                "vehicle_type": "CAR",
                "duration_hours": 3,
            },
            {
                "slot": created_slots["B-101"],
                "driver_name": "Priya Patel",
                "vehicle_number": "MH-12-PQ-9009",
                "phone_number": "+91 9822334455",
                "vehicle_type": "SUV",
                "duration_hours": 4,
            },
            {
                "slot": created_slots["EV-301"],
                "driver_name": "Arjun Nair",
                "vehicle_number": "KA-01-EV-4412",
                "phone_number": "+91 9845012345",
                "vehicle_type": "EV",
                "duration_hours": 2,
            },
            {
                "slot": created_slots["D-201"],
                "driver_name": "Aman Verma",
                "vehicle_number": "HR-26-DK-1188",
                "phone_number": "+91 9998877665",
                "vehicle_type": "BIKE",
                "duration_hours": 1,
            },
        ]

        for b in demo_bookings:
            booking_obj = Booking.objects.create(
                slot=b["slot"],
                driver_name=b["driver_name"],
                vehicle_number=b["vehicle_number"],
                phone_number=b["phone_number"],
                vehicle_type=b["vehicle_type"],
                duration_hours=b["duration_hours"],
                status=Booking.STATUS_ACTIVE,
            )
            # Mark the slot as OCCUPIED
            slot = b["slot"]
            slot.status = ParkingSlot.STATUS_OCCUPIED
            slot.save()

        self.stdout.write(self.style.SUCCESS(
            f"Successfully seeded {len(slots_data)} parking bays and {len(demo_bookings)} active reservations!"
        ))
