from app.database import SessionLocal
from app.models import Contact, Organisation

SAMPLES = [
    ("Acme Logistics", "REG-1001", "Logistics", "info@acme-logistics.com", "active",
     "12 Park End Street", "Oxford", "Oxfordshire", "OX1 1HS"),
    ("Northwind Traders", "REG-1002", "Retail", "hello@northwind.co.uk", "pending",
     "5 Piccadilly", "Manchester", "Greater Manchester", "M1 1AE"),
    ("Bluepeak Solutions", "REG-1003", "Software", "contact@bluepeak.io", "active",
     "20 New Street", "Birmingham", "West Midlands", "B2 4RH"),
    ("Greenfield Agro", "REG-1004", "Agriculture", "office@greenfield.co.uk", "inactive",
     "8 The Headrow", "Leeds", "West Yorkshire", "LS1 6PU"),
]


def main():
    db = SessionLocal()
    try:
        added = 0
        for name, reg, industry, email, status, line1, city, county, postcode in SAMPLES:
            if db.query(Organisation).filter_by(registration_number=reg).first():
                continue
            org = Organisation(
                name=name, registration_number=reg, industry=industry, email=email,
                status=status, address_line1=line1, city=city, county=county,
                postcode=postcode, country="United Kingdom",
                address=f"{line1}, {city}, {county}, {postcode}, United Kingdom",
            )
            db.add(org)
            db.flush()
            db.add(Contact(organisation_id=org.id, full_name="Primary Contact",
                           email=email, job_title="Manager",
                           contact_type="general", is_primary=True))
            added += 1
        db.commit()
        print(f"Added {added} sample organisations.")
    finally:
        db.close()


if __name__ == "__main__":
    main()