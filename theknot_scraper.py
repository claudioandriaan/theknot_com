"""
The Knot Wedding Venues Scraper (AUTO PAGINATION VERSION)
Loops until "Next" button disappears
"""

import asyncio
import json
import csv
import re
import random
from dataclasses import dataclass, asdict
from typing import List, Optional
from playwright.async_api import async_playwright


# =========================
# DATA MODEL
# =========================
@dataclass
class Venue:
    name: str
    location: str
    price: str
    capacity: str
    rating: float
    reviews: int
    description: str


# =========================
# BLOCK ONLY HEAVY FILES
# =========================
async def block_resources(route):
    if route.request.resource_type in ["image", "font"]:
        await route.abort()
    else:
        await route.continue_()


# =========================
# SCRAPER CLASS
# =========================
class TheKnotScraper:

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.base_url = "https://www.theknot.com/marketplace/wedding-reception-venues-atlanta-ga"

    # =========================
    # EXTRACT DATA
    # =========================
    async def scrape_venue_card(self, card) -> Optional[Venue]:
        """Extract data from a single venue card"""
        try:
            # Extract name
            name_elem = await card.query_selector('.vendor-name--mp-FXNIU')
            if not name_elem:
                name_elem = await card.query_selector('a')
            name = await name_elem.inner_text() if name_elem else "N/A"
            name = name.strip()
            
            # Extract location
            location_elem = await card.query_selector('.location-text--mp-OjSGe')            
            location = await location_elem.inner_text() if location_elem else "N/A"
            location = location.replace("\n", ", ").strip()
            
            # Extract price
            price_elem = await card.query_selector('starting-price--mp-zV6P4')
            if not price_elem:
                price_elem = await card.query_selector('.price, [class*="price"], [class*="Price"]')
            price = await price_elem.inner_text() if price_elem else "N/A"
            price = price.replace("Starting at", "").strip() if isinstance(price, str) else "N/A"
            
            # Extract capacity
            capacity_elem = await card.query_selector('.secondary-info-content--mp-ssSzU')
            capacity_text = await capacity_elem.inner_text()
            capacity = capacity_text.split("Guests")[0]
            capacity = capacity.strip() + ' guests' if capacity else "N/A"
            
            # Extract rating
            rating_elem = await card.query_selector('.star-count--mp-YhpiM')           
            rating_text = await rating_elem.inner_text() if rating_elem else "0.0"
            try:
                # Extract numeric rating
                import re
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                rating = float(rating_match.group(1)) if rating_match else 0.0
            except (ValueError, AttributeError):
                rating = 0.0
            
            # Extract review count
            reviews_elem = await card.query_selector('.review-count--mp-WVdDX')            
            reviews_text = await reviews_elem.inner_text() if reviews_elem else "0"
            try:
                # Extract numeric review count
                import re
                reviews_match = re.search(r'(\d+)', reviews_text.replace(',', ''))
                reviews = int(reviews_match.group(1)) if reviews_match else 0
            except (ValueError, AttributeError):
                reviews = 0
            
            # Extract description
            desc_elem = await card.query_selector('.ds-reset--mp-tbmB2.text-body--mp-VDCOi.container--mp-M8lZ8')            
            description = await desc_elem.inner_text() if desc_elem else "N/A"
            description = description.strip()
            
            return Venue(
                name=name,
                location=location,
                price=price,
                capacity=capacity,
                rating=rating,
                reviews=reviews,
                description=description
            )
            
        except Exception as e:
            print(f"Error extracting venue data: {e}")
            return None
    # =========================
    # MAIN SCRAPER (AUTO LOOP)
    # =========================
    async def scrape(self) -> List[Venue]:
        venues = []

        async with async_playwright() as p:
            print("Launching browser...")
            browser = await p.chromium.launch(headless=self.headless)

            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36',
                extra_http_headers={
                    "Accept-Language": "en-US,en;q=0.9",
                    "Referer": "https://www.google.com/"
                }
            )

            await context.route("**/*", block_resources)

            page = await context.new_page()

            try:
                # FIRST PAGE
                await page.goto(self.base_url, wait_until="domcontentloaded")
                await asyncio.sleep(5)

                page_number = 1

                while True:
                    print(f"\nScraping page {page_number}")

                    cards = await page.query_selector_all(
                        '.vendor-search-row--mp-wp8eA section.container--mp-dDjfl'
                    )

                    if not cards:
                        print("No cards found → stopping")
                        break

                    print(f"Found {len(cards)} venues")

                    for card in cards:
                        venue = await self.scrape_venue_card(card)
                        if venue and venue.name != "N/A":
                            venues.append(venue)

                    #  CHECK NEXT BUTTON
                    next_button = await page.query_selector('a[aria-label="Go to next page"]')

                    if not next_button:
                        print("No more pages → finished")
                        break

                    #  CLICK NEXT
                    try:
                        await next_button.click()
                        await page.wait_for_load_state("domcontentloaded")

                        await asyncio.sleep(5 + random.uniform(2, 5))
                        page_number += 1

                    except Exception as e:
                        print(f"Pagination error: {e}")
                        break

            except Exception as e:
                print(f"Global error: {e}")

            finally:
                await browser.close()

        return venues

    # =========================
    # SAVE JSON
    # =========================
    def save_to_json(self, venues: List[Venue], filename="venues.json"):
        data = [asdict(v) for v in venues]
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Saved JSON → {filename}")

    # =========================
    # SAVE CSV
    # =========================
    def save_to_csv(self, venues: List[Venue], filename="venues.csv"):
        if not venues:
            return

        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=asdict(venues[0]).keys())
            writer.writeheader()
            for v in venues:
                writer.writerow(asdict(v))

        print(f"Saved CSV → {filename}")


# =========================
# MAIN
# =========================
async def main():
    print("=" * 50)
    print("THE KNOT SCRAPER")
    print("=" * 50)

    scraper = TheKnotScraper(headless=False)

    venues = await scraper.scrape()

    print(f"\nTotal venues scraped: {len(venues)}")

    if venues:
        scraper.save_to_json(venues)
        scraper.save_to_csv(venues)


if __name__ == "__main__":
    asyncio.run(main())