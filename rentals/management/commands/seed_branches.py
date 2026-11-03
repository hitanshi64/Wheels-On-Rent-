from django.core.management.base import BaseCommand
from rentals.models import Branch

class Command(BaseCommand):
    help = 'Seeds initial branch/shop location data for WheelsOnRent'

    def handle(self, *args, **kwargs):
        branches_data = [
            {
                'name': 'WheelsOnRent - Satellite',
                'city': 'Ahmedabad',
                'address': 'Shop 4, Satellite Road, Ahmedabad, Gujarat 380015',
                'contact_number': '+91 79123 45001',
                'latitude': 23.0225,
                'longitude': 72.5714,
            },
            {
                'name': 'WheelsOnRent - Andheri',
                'city': 'Mumbai',
                'address': 'Ground Floor, Andheri West, Mumbai, Maharashtra 400058',
                'contact_number': '+91 22123 45002',
                'latitude': 19.1197,
                'longitude': 72.8468,
            },
            {
                'name': 'WheelsOnRent - Connaught Place',
                'city': 'Delhi',
                'address': 'Block A, Connaught Place, New Delhi 110001',
                'contact_number': '+91 11123 45003',
                'latitude': 28.6315,
                'longitude': 77.2167,
            },
            {
                'name': 'WheelsOnRent - Koramangala',
                'city': 'Bangalore',
                'address': '5th Block, Koramangala, Bangalore, Karnataka 560095',
                'contact_number': '+91 80123 45004',
                'latitude': 12.9352,
                'longitude': 77.6245,
            },
            {
                'name': 'WheelsOnRent - Kothrud',
                'city': 'Pune',
                'address': 'Kothrud Depot Road, Pune, Maharashtra 411038',
                'contact_number': '+91 20123 45005',
                'latitude': 18.5074,
                'longitude': 73.8077,
            },
            {
                'name': 'WheelsOnRent - Vesu',
                'city': 'Surat',
                'address': 'Vesu Main Road, Surat, Gujarat 395007',
                'contact_number': '+91 26123 45006',
                'latitude': 21.1458,
                'longitude': 72.7709,
            },
            {
                'name': 'WheelsOnRent - Alkapuri',
                'city': 'Vadodara',
                'address': 'Alkapuri, Vadodara, Gujarat 390007',
                'contact_number': '+91 26512 34567',
                'latitude': 22.3072,
                'longitude': 73.1812,
            },
            {
                'name': 'WheelsOnRent - Kalawad Road',
                'city': 'Rajkot',
                'address': 'Kalawad Road, Rajkot, Gujarat 360005',
                'contact_number': '+91 28122 34568',
                'latitude': 22.3039,
                'longitude': 70.8022,
            },
            {
                'name': 'WheelsOnRent - Sector 21',
                'city': 'Gandhinagar',
                'address': 'Sector 21, Gandhinagar, Gujarat 382021',
                'contact_number': '+91 79232 34569',
                'latitude': 23.2156,
                'longitude': 72.6369,
            },
            {
                'name': 'WheelsOnRent - Waghawadi Road',
                'city': 'Bhavnagar',
                'address': 'Waghawadi Road, Bhavnagar, Gujarat 364001',
                'contact_number': '+91 27842 34570',
                'latitude': 21.7645,
                'longitude': 72.1519,
            },
            {
                'name': 'WheelsOnRent - Bedi Bandar Road',
                'city': 'Jamnagar',
                'address': 'Bedi Bandar Road, Jamnagar, Gujarat 361008',
                'contact_number': '+91 28822 34571',
                'latitude': 22.4707,
                'longitude': 70.0577,
            },
        ]

        created_count = 0
        for data in branches_data:
            branch, created = Branch.objects.get_or_create(
                name=data['name'],
                city=data['city'],
                defaults=data
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {created_count} branches into the database.'))
