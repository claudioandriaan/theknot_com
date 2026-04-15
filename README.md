# The Knot Wedding Venues Scraper

A professional web scraper built with Python Playwright to extract wedding reception venue data from TheKnot.com.

## Features

✅ **Comprehensive Data Extraction**
- Venue name
- Location
- Price range
- Guest capacity
- Rating (float)
- Review count
- Description

✅ **Robust Scraping**
- Automatic pagination process
- Multiple selector fallbacks for reliability
- Proper error handling
- Debug HTML output for troubleshooting

✅ **Export Options**
- JSON format
- CSV format

## Installation

### 1. Install Python Dependencies

```bash
pip install playwright
```

### 2. Install Browser

```bash
playwright install chromium
```

## Usage

### Basic Usage

```bash
python theknot_scraper.py
```

### In Your Code

```python
import asyncio
from theknot_scraper import TheKnotScraper

async def main():
    # Initialize scraper
    scraper = TheKnotScraper(headless=True)
    
    # Scrape venues
    venues = await scraper.scrape()
    
    # Save to JSON
    scraper.save_to_json(venues, "my_venues.json")
    
    # Save to CSV
    scraper.save_to_csv(venues, "my_venues.csv")
    
    # Work with venue data
    for venue in venues:
        print(f"{venue.name} - {venue.rating}⭐ ({venue.reviews} reviews)")

asyncio.run(main())
```

## Configuration

### Headless Mode

```python
# Run with visible browser (useful for debugging)
scraper = TheKnotScraper(headless=False)

# Run in headless mode (faster, no GUI)
scraper = TheKnotScraper(headless=True)
```

## Output Format

### JSON Example

```json
[
  {
    "name": "The Biltmore Ballrooms",
    "location": "Atlanta, GA",
    "price": "$$$",
    "capacity": "300-500 guests",
    "rating": 4.8,
    "reviews": 342,
    "description": "Historic ballroom with elegant architecture..."
  }
]
```

### CSV Example

```csv
name,location,price,capacity,rating,reviews,description
The Biltmore Ballrooms,Atlanta GA,$$$,300-500 guests,4.8,342,Historic ballroom...
```

## Data Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | str | Venue name |
| `location` | str | Venue location/address |
| `price` | str | Price range (e.g., "$$$") |
| `capacity` | str | Guest capacity (e.g., "200-400 guests") |
| `rating` | float | Average rating (0.0-5.0) |
| `reviews` | int | Number of reviews |
| `description` | str | Venue description |

## Troubleshooting

### No venues found?

1. **Check network access**: Ensure theknot.com is accessible
2. **Website structure changed**: The site may have updated their HTML structure
3. **Anti-bot protection**: The site may be detecting automated access
4. **Review debug output**: Check `debug_page.html` for the actual page content

### Common Issues

**Issue**: "Host not in allowlist"
- **Solution**: Update network settings to allow theknot.com or run on a machine with unrestricted internet access

**Issue**: Empty data fields
- **Solution**: The website structure may have changed. Update the CSS selectors in `scrape_venue_card()` method

**Issue**: Timeout errors
- **Solution**: Increase timeout values or check your internet connection

## Advanced Customization

### Adding More Fields

To scrape additional data:

1. Add the field to the `Venue` dataclass:
```python
@dataclass
class Venue:
    # ... existing fields ...
    website: str
    phone: str
```

2. Extract the data in `scrape_venue_card()`:
```python
website_elem = await card.query_selector('.website-selector')
website = await website_elem.inner_text() if website_elem else "N/A"
```

### Scraping Multiple Cities

Modify the base URL:

```python
scraper = TheKnotScraper()
scraper.base_url = "https://www.theknot.com/marketplace/wedding-reception-venues-NEW-YORK-NY"
venues = await scraper.scrape()
```

## Requirements

- Python 3.7+
- playwright 1.48.0+
- Internet connection

## License

This project is provided as-is for educational purposes.

## Version

**Version**: 1.0.0  
**Last Updated**: 2026-04-15
