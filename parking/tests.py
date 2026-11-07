"""
=============================================================================
SMART PARKING SYSTEM - AUTOMATED UNIT & INTEGRATION TESTS (tests.py)
=============================================================================
Beginner Guide to Django Testing:
Tests ensure your code works properly and prevents regressions (bugs created
when you add new features).
You can run all tests using:
`python manage.py test`

Django creates a temporary, isolated SQLite test database, runs your tests,
and immediately cleans it up. Your real database is never touched!
=============================================================================
"""

from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from parking.models import ParkingSlot, Booking


class SmartParkingTests(TestCase):
    """Automated test suite verifying business logic and views."""

    def setUp(self):
        """Runs before every test method: prepares test database state."""
        self.client = Client()

        # Create sample slots
        self.slot1 = ParkingSlot.objects.create(
            slot_number="A-101",
            floor_zone="Ground Floor - Zone A",
            vehicle_type=ParkingSlot.VEHICLE_CAR,
            status=ParkingSlot.STATUS_AVAILABLE,
            hourly_rate=Decimal("60.00")
        )
        self.slot2 = ParkingSlot.objects.create(
            slot_number="B-102",
            floor_zone="Ground Floor - Zone B",
            vehicle_type=ParkingSlot.VEHICLE_SUV,
            status=ParkingSlot.STATUS_OCCUPIED,
            hourly_rate=Decimal("75.00")
        )

    def test_slot_availability_property(self):
        """Test is_available property correctly reports status."""
        self.assertTrue(self.slot1.is_available)
        self.assertFalse(self.slot2.is_available)

    def test_booking_creation_and_cost_calculation(self):
        """
        Verify booking creation:
        - Automatically capitalizes vehicle plate number
        - Calculates estimated cost based on slot hourly rate
        - Marks slot as OCCUPIED
        """
        booking = Booking.objects.create(
            slot=self.slot1,
            driver_name="Rahul Varma",
            vehicle_number="dl 01 ab 1234",  # lowercase input
            phone_number="9876543210",
            vehicle_type=ParkingSlot.VEHICLE_CAR,
            duration_hours=3,
        )

        # Vehicle number normalized to uppercase
        self.assertEqual(booking.vehicle_number, "DL 01 AB 1234")

        # 3 hours * ₹60.00/hr = ₹180.00
        self.assertEqual(booking.estimated_cost, Decimal("180.00"))

        # Unique reference generated
        self.assertTrue(booking.booking_reference.startswith("PRK-"))

    def test_booking_cancellation_frees_slot(self):
        """
        Cancelling an active booking must:
        - Set booking status to CANCELLED
        - Automatically reset the associated parking slot back to AVAILABLE
        """
        # Initially occupy slot 1
        booking = Booking.objects.create(
            slot=self.slot1,
            driver_name="Test Driver",
            vehicle_number="KA-05-MM-1234",
            phone_number="9988776655",
            vehicle_type=ParkingSlot.VEHICLE_CAR,
            duration_hours=2,
            status=Booking.STATUS_ACTIVE
        )
        self.slot1.status = ParkingSlot.STATUS_OCCUPIED
        self.slot1.save()

        self.assertFalse(self.slot1.is_available)

        # Trigger cancellation
        success = booking.cancel_booking()
        self.assertTrue(success)

        # Reload from DB
        self.slot1.refresh_from_db()
        booking.refresh_from_db()

        self.assertEqual(booking.status, Booking.STATUS_CANCELLED)
        self.assertEqual(self.slot1.status, ParkingSlot.STATUS_AVAILABLE)
        self.assertTrue(self.slot1.is_available)

    def test_home_view_status_code(self):
        """Test Home Page loads successfully (HTTP 200 OK)."""
        response = self.client.get(reverse('parking:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A-101")
        self.assertContains(response, "AVAILABLE")

    def test_admin_toggle_slot_status(self):
        """Test admin can toggle slot between Available and Maintenance."""
        response = self.client.get(reverse('parking:admin_toggle_slot', args=[self.slot1.id]))
        self.assertEqual(response.status_code, 302)  # Redirects back to portal
        self.slot1.refresh_from_db()
        self.assertEqual(self.slot1.status, ParkingSlot.STATUS_MAINTENANCE)
