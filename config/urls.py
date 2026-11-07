"""
=============================================================================
MAIN URL ROUTING CONFIGURATION (config/urls.py)
=============================================================================
Beginner Guide:
This is the root router for the entire project. When a user requests a URL:
1. Django checks patterns in this list from top to bottom.
2. `include('parking.urls')` forwards all parking-related URLs to the parking app.
3. `path('admin/', admin.site.urls)` provides Django's powerful out-of-the-box
   Superuser Administration Portal!
=============================================================================
"""

from django.contrib import admin
from django.urls import path, include

# Customize Django Admin Portal Branding
admin.site.site_header = "Smart Parking Management | Central Admin"
admin.site.site_title = "SmartPark Admin Portal"
admin.site.index_title = "Facility & Bay Management Control Room"

urlpatterns = [
    # Built-in Django Admin Interface
    path('admin/', admin.site.urls),

    # Main Application URLs (Home, Booking, Cancel, Custom Admin Portal)
    path('', include('parking.urls')),
]
