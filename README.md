# Wheels on Rent — Vehicle Rental Website (Django)

## Real payments + automatic refunds (Razorpay)
1. Create a free account at https://dashboard.razorpay.com and stay in **Test Mode**.
2. Settings -> API Keys -> Generate Test Key. Copy the Key Id (`rzp_test_...`) and Key Secret.
3. Open `wheels_on_rent/settings.py`, find `RAZORPAY_KEY_ID` / `RAZORPAY_KEY_SECRET`, and paste the keys between the quotes
   (or set them as environment variables of the same names).
4. Restart the server. Checkout now opens the real Razorpay popup (use Razorpay's test card/UPI details).
5. When a customer cancels a paid booking, 75% is refunded automatically through Razorpay to the original payment method.
If the keys are empty, the site falls back to the old simulated payment.
Keep Razorpay's default "auto-capture" setting ON, otherwise refunds will fail.

## New: Admin panel redesign + independent admin login
- The `/admin/` panel now has a professional navy + teal corporate theme, larger fonts throughout (body text bumped from Django's default 13px to 15px, headings scaled up too), a custom "WheelsOnRent Admin" brand mark, rounded cards, and a polished login page
- **Admin login is now fully independent from the customer site.** They use two separate session cookies (`sessionid` for the site, `admin_sessionid` for `/admin/`), so:
  - A customer clicking "Logout" on the website does **not** log the admin out of `/admin/`, even in the same browser
  - Both can be logged in at the same time, in the same browser
- **Who can access the admin panel:** only accounts created with `python manage.py createsuperuser` (or manually marked as staff) can log into `/admin/`. Anyone who self-registers on the website is a regular customer account and can never access `/admin/` — so keep the number of superuser accounts to just 1–2 trusted people, and let as many customers register as you like.

## New: Gujarat cities added to branch coverage
Added branches (and therefore dropdown entries) for: **Vadodara, Rajkot, Gandhinagar, Bhavnagar, Jamnagar** (in addition to the existing Ahmedabad and Surat). Run `python manage.py seed_branches` to load them.

## New: Contact page subject dropdown
The "Subject" field on `/contact/` is now a dropdown: **Review / Query / Other** (previously free text).

## Multi-Branch Shop Location System
- **`Branch`** table: name, city, full address, contact number, Google Maps link, latitude/longitude, active/inactive
- On every page, a bar auto-detects the visitor's location (browser Geolocation API) and shows the **nearest active branch** with a live distance and a **"Get Directions"** button (opens Google Maps navigation — no paid API key needed)
- If location access is denied, a **"Select Your City"** popup appears instead; the nearest/matching branch is shown from that city, or the nearest available branch from another city if none exists locally
- The **Contact Us** page additionally shows an **embedded Google Map** of the nearest branch
- **Admin Panel** → "Branches": add/edit/delete branches, update coordinates, toggle Active/Inactive
- Seed sample branches (6 Indian cities) with:
  ```
  python manage.py seed_branches
  ```

⚠️ Because the database structure changed again, delete any old `db.sqlite3` and re-run
`python manage.py migrate` before starting the server.

## Earlier features

- **About Us** page (`/about/`) and **Contact Us** page (`/contact/`, saves messages to the database — view them in Admin under "Contact messages")
- **Registration** now asks for: username, email, phone number, password, confirm password
- **Before booking a vehicle**, the customer must now fill in: name, phone number, address, email, gender, and driving licence number + upload a licence photo/PDF as ID proof. This is saved with the booking (view it in Admin under "Bookings")

⚠️ Because the database structure changed, if you're updating an existing copy of this project,
delete your old `db.sqlite3` file (or run `python manage.py migrate` — a new migration
`0002_...` is included) before running the server again.


## Requirements
- Python 3.10+ (already installed on your laptop)
- VS Code with the "Python" extension (from Extensions marketplace)
- Internet (only needed once, to install Django)

You do NOT need Node.js. You do NOT need XAMPP — this project uses SQLite,
a database that's just a single file, created automatically.

## Setup steps (run in VS Code's terminal: Terminal > New Terminal)

1. Create a virtual environment
   python -m venv .venv

2. Activate it
   Windows:      .venv\Scripts\activate
   Mac/Linux:    source .venv/bin/activate

3. Install Django
   pip install -r requirements.txt

4. Create the database tables
   python manage.py migrate

5. (Optional) Add sample vehicles (bike, cycle, car, activa, etc.)
   python manage.py seed_vehicles

6. (Optional) Create an admin login
   python manage.py createsuperuser

7. Run the website
   python manage.py runserver

8. Open in browser
   http://127.0.0.1:8000/

Admin panel (if you created a superuser): http://127.0.0.1:8000/admin/
