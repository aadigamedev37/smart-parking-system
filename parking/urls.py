"""
=============================================================================
SMART PARKING MANAGEMENT SYSTEM - APP URL ROUTING (urls.py)
=============================================================================
Beginner Guide to Django URL Routing:
This file maps incoming browser URLs to the corresponding Python view functions.

Key Concepts:
- `path('pattern/', views.function_name, name='route_name')`
- `app_name = 'parking'` creates a "namespace", allowing you to generate URLs
  dynamically in templates using `{% url 'parking:home' %}` rather than hardcoding
  links like `<a href="/home/">`. If you ever change the URL pattern, your templates
  never break!
=============================================================================
"""

from django.urls import path
from . import views

app_name = 'parking'

urlpatterns = [
    # -------------------------------------------------------------------------
    # USER-FACING ROUTES
    # -------------------------------------------------------------------------
    # Home Page: Shows interactive parking layout and available slots
    path('', views.home_view, name='home'),

    # Book an available slot (either general booking or pre-selected slot)
    path('book/', views.book_slot_view, name='book_slot_general'),
    path('book/<int:slot_id>/', views.book_slot_view, name='book_slot'),

    # Booking Confirmation Ticket / Digital Pass
    path('confirmation/<str:reference>/', views.booking_confirmation_view, name='booking_confirmation'),

    # Cancel an existing reservation
    path('cancel/', views.cancel_booking_view, name='cancel_booking'),

    # -------------------------------------------------------------------------
    # ADMINISTRATOR-FACING ROUTES
    # -------------------------------------------------------------------------
    # Dedicated Executive Admin Dashboard & Monitoring
    path('portal/', views.admin_dashboard_view, name='admin_dashboard'),

    # Add a new parking slot
    path('portal/slot/add/', views.admin_add_slot_view, name='admin_add_slot'),

    # Edit an existing parking slot
    path('portal/slot/edit/<int:slot_id>/', views.admin_edit_slot_view, name='admin_edit_slot'),

    # Quick toggle slot availability (Available <-> Maintenance)
    path('portal/slot/toggle/<int:slot_id>/', views.admin_toggle_slot_status, name='admin_toggle_slot'),

    # Mark vehicle as exited / complete booking
    path('portal/booking/complete/<int:booking_id>/', views.admin_complete_booking_view, name='admin_complete_booking'),

    # -------------------------------------------------------------------------
    # LIVE JSON API FOR ASYNC CLIENT UPDATES
    # -------------------------------------------------------------------------
    path('api/slots/', views.api_slots_status, name='api_slots_status'),
]
