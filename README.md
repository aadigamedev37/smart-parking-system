# 🚗 Smart Parking Management System (SmartPark)
### High-Performance Facility Automation & Bay Allocation Engine
**Built with Python 3.14 + Django 6.1 + Tailwind CSS + Glassmorphism UI**

---

## 📌 1. Project Overview & Problem Statement

In busy locations such as colleges, shopping malls, hospitals, and office complexes, drivers waste significant time searching for vacant parking bays. Manual paper-based or guard-dependent parking makes it difficult to track occupied spaces and identify available slots in real time.

This project delivers a full-stack, production-ready **Smart Parking Management System** addressing all required specifications:

### 👤 User Capabilities:
- **Live Parking Bay Grid**: Visual representation of all parking bays across multiple floors/zones with live state indicators (**Available (Green)**, **Occupied (Red)**, or **Under Maintenance (Gray)**).
- **Vehicle Registration & Booking**: Drivers enter their name, vehicle registration plate (e.g. `DL-01-AB-1234`), contact number, vehicle type (Car, SUV, Bike, EV, Handicap priority), and estimated parking duration.
- **Race-Condition Safe Reservation**: Database row-level locking (`select_for_update()` + `transaction.atomic()`) guarantees that two drivers can never book the same bay simultaneously.
- **Digital Boarding Pass / Parking Ticket**: Generates an instant digital ticket with unique reference ID (`PRK-XXXXXX`), entrance QR code illustration, vehicle plate badge, in-time, and printable ticket layout.
- **Self-Service Reservation Cancellation**: Drivers can search by Booking Reference ID or License Plate number to cancel reservations. Cancelling immediately frees the bay back to `AVAILABLE`.

### 🛡️ Administrator Capabilities:
- **Executive Control Center (`/portal/`)**:
  - Live facility telemetry: Total Bays, Vacant Count, Occupied Count, Maintenance Bays, Load Percentage, and Gross Revenue.
- **Bay Management**:
  - Add new parking slots (slot code, floor zone, vehicle suitability, tariff).
  - Update and edit slot specifications.
  - 1-Click Status Toggle: Instantly switch any bay between `AVAILABLE`, `MAINTENANCE`, or manually release occupied bays.
- **Reservation Ledger**:
  - Live searchable list of all bookings with vehicle plate filters, driver lookups, and timestamps.
  - 1-Click "Exit Vehicle / Complete Booking" boom barrier release.
- **Django Core Admin (`/admin/`)**: Fully configured with custom `ModelAdmin` filters, search bars, and colored badges.

---

## 🚀 2. Quick Start Guide (How to Run)

Open PowerShell or Command Prompt in the project folder:
```powershell
cd C:\Users\Aditya\.gemini\antigravity\scratch\smart_parking_system
```

### Step 1: Run Database Migrations
Creates the SQLite database (`db.sqlite3`) and all tables:
```powershell
python manage.py migrate
```

### Step 2: Seed Realistic Test Bays & Demo Data (Optional but Recommended)
Populates 22 realistic parking bays across 5 zones and 4 active demo bookings:
```powershell
python manage.py seed_parking
```

### Step 3: Start the Development Server
```powershell
python manage.py runserver
```

Open your browser at:
- 🌐 **Driver Portal (Home / Live Grid)**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- 🛡️ **Admin Control Room**: [http://127.0.0.1:8000/portal/](http://127.0.0.1:8000/portal/)
- ⚙️ **Django Core Superuser Admin**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
  - **Username**: `admin`
  - **Password**: `adminpassword123`

---

## 🧪 3. Running Automated Tests

To verify that all business logic, pricing formulas, and slot transitions are 100% bug-free:
```powershell
python manage.py test
```
Result:
```text
Ran 5 tests in 0.062s
OK
```

---

## 📂 4. Project Directory Structure Explained

```text
smart_parking_system/
│
├── config/                         # Master Project Settings & Root Router
│   ├── settings.py                 # Installed apps, database config, templates & static dirs
│   ├── urls.py                     # Root URL dispatcher (routes traffic to parking/ & admin/)
│   ├── wsgi.py & asgi.py           # Web server gateway interfaces for deployment
│
├── parking/                        # Main Application Package
│   ├── models.py                   # SQL Database Tables (ParkingSlot & Booking)
│   ├── views.py                    # Controllers: Business logic, booking flows & Admin stats
│   ├── forms.py                    # ModelForm validations, plate normalization & sanitization
│   ├── urls.py                     # App-level URL routes (/book/, /cancel/, /portal/)
│   ├── admin.py                    # Django Admin customization with colored badges
│   ├── tests.py                    # Automated unit & integration test suite
│   ├── management/commands/        # Custom CLI commands
│   │   └── seed_parking.py         # Seed script: 22 slots, zones & demo cars
│   └── templates/parking/          # HTML Templates for the Parking App
│       ├── home.html               # Visual Bay Grid, Live Stats, Quick Booking Modal
│       ├── book_slot.html          # Standalone Booking page with live Plate simulator
│       ├── confirmation.html       # Boarding-pass style digital parking pass
│       ├── cancel_booking.html     # Reservation search & 1-click cancel
│       ├── admin_dashboard.html    # Executive Admin Portal & Telemetry
│       └── admin_edit_slot.html    # Slot configuration update page
│
├── templates/
│   └── base.html                   # Master layout with navbar, footer, Tailwind & glassmorphism
│
├── static/                         # Static CSS & JS assets
├── db.sqlite3                      # SQLite Database file
└── manage.py                       # Django's Swiss-Army CLI tool
```

---

## 🧠 5. Beginner Code Explanation: How It Works Internally

### 1. Model-View-Template (MVT) Architecture
- **Model (`models.py`)**: Tells Django what tables and columns exist in the database.
  - `ParkingSlot`: Stores slot bay number (`A-101`), floor zone, allowed vehicle type, status (`AVAILABLE`, `OCCUPIED`, `MAINTENANCE`), and hourly tariff.
  - `Booking`: Stores driver name, uppercase license plate (`DL-01-AB-1234`), phone number, duration, estimated fee, and reference code (`PRK-XXXXXX`).
  - `slot = models.ForeignKey(ParkingSlot, on_delete=models.CASCADE, related_name='bookings')`: Connects a booking to a slot in a One-to-Many relational link.

### 2. Concurrency & Race-Condition Safety (Senior Dev Move)
When two drivers click "Book Slot A-101" at the exact same millisecond, standard code would cause a collision. In `views.py`:
```python
with transaction.atomic():
    locked_slot = ParkingSlot.objects.select_for_update().get(id=slot.id)
    if locked_slot.status != ParkingSlot.STATUS_AVAILABLE:
        # Rejects second user safely with a friendly warning!
```
`select_for_update()` places an exclusive row-level lock on the slot in SQL until the transaction finishes.

### 3. Slot Status Synchronization on Cancellation
When a driver cancels their booking:
```python
def cancel_booking(self):
    self.status = self.STATUS_CANCELLED
    self.cancelled_at = timezone.now()
    self.save()

    # Free up the physical slot immediately:
    self.slot.status = ParkingSlot.STATUS_AVAILABLE
    self.slot.save()
```
The bay turns green on the live map in real time!

---

## 🎓 6. Viva & Interview Questions & Answers

1. **Q: What is Django's MVT architecture?**
   - **A**: Model (Data/Database), View (Business logic/Controller), Template (Presentation/HTML).

2. **Q: How does the system prevent two users from booking the same slot simultaneously?**
   - **A**: By wrapping the reservation in `transaction.atomic()` and querying the slot with `select_for_update()`, locking the database row during write operations.

3. **Q: Why do we use `get_object_or_404()` in views?**
   - **A**: It queries the database and automatically returns a clean HTTP 404 Page Not Found if an invalid ID is requested, preventing unhandled server crashes (`DoesNotExist` exception).

4. **Q: How are static files and templates separated in Django?**
   - **A**: Templates are HTML files parsed by Django's template engine; static files are client assets (CSS, JS, fonts, images) served directly to the browser.
