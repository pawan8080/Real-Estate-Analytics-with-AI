"""Generate a realistic sample real estate dataset for AskEstate."""
import csv
import random
from datetime import datetime, timedelta

random.seed(42)

NEIGHBORHOODS = [
    "Downtown", "Westside", "Northpark", "Eastbrook", "Southgate",
    "Midtown", "Riverside", "Hillcrest", "Oakwood", "Lakeside",
]
PROPERTY_TYPES = ["House", "Condo", "Townhouse", "Apartment"]
CITIES = ["Austin", "Denver", "Seattle", "Portland", "Nashville"]

def generate_listings(n=2000):
    rows = []
    for i in range(1, n + 1):
        prop_type = random.choice(PROPERTY_TYPES)
        bedrooms = random.choices([1, 2, 3, 4, 5], weights=[10, 25, 35, 20, 10])[0]
        bathrooms = max(1, bedrooms - random.randint(0, 2))
        sqft = bedrooms * random.randint(400, 700) + random.randint(-200, 400)
        sqft = max(400, sqft)
        year_built = random.randint(1950, 2024)
        neighborhood = random.choice(NEIGHBORHOODS)
        city = random.choice(CITIES)

        # Price model: base + size + bedrooms + newness + neighborhood premium
        base = 150000
        price = (
            base
            + sqft * random.randint(180, 320)
            + bedrooms * 15000
            + max(0, year_built - 1980) * 1200
            + (50000 if neighborhood in ["Downtown", "Midtown", "Riverside"] else 0)
            + random.randint(-40000, 60000)
        )
        price = max(80000, int(price / 1000) * 1000)

        # Listing date within last 2 years
        days_ago = random.randint(0, 730)
        listing_date = (datetime(2026, 4, 19) - timedelta(days=days_ago)).strftime("%Y-%m-%d")

        status = random.choices(["Active", "Sold", "Pending"], weights=[40, 50, 10])[0]
        days_on_market = random.randint(1, 180) if status != "Active" else random.randint(1, 60)

        rows.append({
            "listing_id": i,
            "city": city,
            "neighborhood": neighborhood,
            "property_type": prop_type,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "square_feet": sqft,
            "year_built": year_built,
            "price": price,
            "listing_date": listing_date,
            "status": status,
            "days_on_market": days_on_market,
        })
    return rows

if __name__ == "__main__":
    rows = generate_listings(2000)
    with open("data/real_estate.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Generated {len(rows)} listings -> data/real_estate.csv")
