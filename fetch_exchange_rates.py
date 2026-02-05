"""
Fetch exchange rates from Treasury API and combine with currency codes from ISO data.
"""

import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json
import ssl
import gzip
import base64
import re


def fetch_url(url, skip_ssl=False):
    """Fetch a URL and return the response content."""
    if skip_ssl:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
    else:
        context = ssl.create_default_context()
    
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=context) as response:
        return response.read()


def fetch_eurozone_countries():
    """Fetch the list of Eurozone member countries from Wikipedia."""
    url = "https://en.wikipedia.org/wiki/Eurozone"
    try:
        content = fetch_url(url, skip_ssl=True).decode('utf-8')
        
        # The Eurozone countries are listed in a table. We'll parse the HTML to find them.
        # Look for country names in the member table - they appear in patterns like:
        # |  Austria | AT | 1999
        # |  Germany | DE | 1999
        
        eurozone_countries = set()
        
        # Match patterns like "| Austria |" or "|  Germany |" from the table
        # The table has countries with their ISO codes
        pattern = r'\|\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*\|\s*[A-Z]{2}\s*\|'
        matches = re.findall(pattern, content)
        
        for match in matches:
            country = match.strip()
            if country and len(country) > 2:
                eurozone_countries.add(country.upper())
        
        # Also add known Eurozone countries in case parsing misses any
        known_eurozone = {
            "AUSTRIA", "BELGIUM", "BULGARIA", "CROATIA", "CYPRUS", "ESTONIA",
            "FINLAND", "FRANCE", "GERMANY", "GREECE", "IRELAND", "ITALY",
            "LATVIA", "LITHUANIA", "LUXEMBOURG", "MALTA", "NETHERLANDS",
            "PORTUGAL", "SLOVAKIA", "SLOVENIA", "SPAIN"
        }
        eurozone_countries.update(known_eurozone)
        
        return eurozone_countries
    except Exception as e:
        # Fall back to known list if Wikipedia fetch fails
        return {
            "AUSTRIA", "BELGIUM", "BULGARIA", "CROATIA", "CYPRUS", "ESTONIA",
            "FINLAND", "FRANCE", "GERMANY", "GREECE", "IRELAND", "ITALY",
            "LATVIA", "LITHUANIA", "LUXEMBOURG", "MALTA", "NETHERLANDS",
            "PORTUGAL", "SLOVAKIA", "SLOVENIA", "SPAIN"
        }


def fetch_currency_codes():
    """Fetch currency codes from the ISO currency XML document."""
    url = "https://www.six-group.com/dam/download/financial-information/data-center/iso-currrency/lists/list-one.xml"
    content = fetch_url(url, skip_ssl=True)
    
    # Parse XML
    root = ET.fromstring(content)
    
    # Build a mapping from country name to currency code
    # The XML structure has CcyNtry elements with CtryNm and Ccy children
    country_to_currency = {}
    
    # Find all currency entries (namespace may vary)
    for entry in root.iter():
        if entry.tag.endswith('CcyNtry'):
            country_name = None
            currency_code = None
            
            for child in entry:
                if child.tag.endswith('CtryNm'):
                    country_name = child.text
                elif child.tag.endswith('Ccy'):
                    currency_code = child.text
            
            if country_name and currency_code:
                # Store with normalized key (uppercase for matching)
                country_to_currency[country_name.upper()] = currency_code
    
    return country_to_currency


def fetch_exchange_rates():
    """Fetch exchange rates from Treasury API until record_date changes."""
    base_url = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/rates_of_exchange"
    
    all_results = []
    page_number = 1
    first_record_date = None
    
    while True:
        params = {
            "page[size]": "200",
            "sort": "-record_date",
            "page[number]": str(page_number)
        }
        
        query_string = urllib.parse.urlencode(params)
        url = f"{base_url}?{query_string}"
        
        content = fetch_url(url)
        data = json.loads(content)
        
        records = data.get("data", [])
        
        if not records:
            # No more data
            break
        
        for record in records:
            record_date = record.get("record_date")
            
            if first_record_date is None:
                first_record_date = record_date
            
            if record_date != first_record_date:
                # Record date changed, stop processing
                return all_results, first_record_date
            
            all_results.append(record)
        
        # Check if there are more pages
        meta = data.get("meta", {})
        total_pages = meta.get("total-pages", 1)
        
        if page_number >= total_pages:
            # No more pages
            break
        
        page_number += 1
    
    return all_results, first_record_date


def match_country_to_currency(country_name, country_to_currency):
    """Try to match a country name to a currency code."""
    if not country_name:
        return None
    
    # Try exact match first (uppercase)
    country_upper = country_name.upper()
    if country_upper in country_to_currency:
        return country_to_currency[country_upper]
    
    # Handle some common naming differences BEFORE partial matching
    name_mappings = {
        "EURO ZONE": "EUROPEAN UNION",  # Map Euro Zone to EU for EUR
        "UNITED KINGDOM": "UNITED KINGDOM OF GREAT BRITAIN AND NORTHERN IRELAND",
        "RUSSIA": "RUSSIAN FEDERATION",
        "SOUTH KOREA": "KOREA (THE REPUBLIC OF)",
        "KOREA": "KOREA (THE REPUBLIC OF)",
        "VIETNAM": "VIET NAM",
        "TAIWAN": "TAIWAN (PROVINCE OF CHINA)",
        "VENEZUELA": "VENEZUELA (BOLIVARIAN REPUBLIC OF)",
        "BOLIVIA": "BOLIVIA (PLURINATIONAL STATE OF)",
        "IRAN": "IRAN (ISLAMIC REPUBLIC OF)",
        "SYRIA": "SYRIAN ARAB REPUBLIC",
        "LAOS": "LAO PEOPLE'S DEMOCRATIC REPUBLIC",
        "TANZANIA": "TANZANIA, UNITED REPUBLIC OF",
        "CONGO": "CONGO (THE DEMOCRATIC REPUBLIC OF THE)",
        "IVORY COAST": "CÔTE D'IVOIRE",
        "CZECH REPUBLIC": "CZECHIA",
    }
    
    mapped_name = name_mappings.get(country_upper)
    if mapped_name and mapped_name in country_to_currency:
        return country_to_currency[mapped_name]
    
    # Try partial matching for common variations
    # Be strict - require the country name to be a substantial match
    for iso_country, currency_code in country_to_currency.items():
        # Check if one contains the other AND they share significant overlap
        if country_upper in iso_country or iso_country in country_upper:
            # Skip if this is Bulgaria matching to a Eurozone country
            # (Bulgaria uses Lev, not Euro, in Treasury data)
            if country_upper == "BULGARIA" and currency_code == "EUR":
                continue
            return currency_code
    
    return None


def main():
    country_to_currency = fetch_currency_codes()
    exchange_rates, record_date = fetch_exchange_rates()
    eurozone_countries = fetch_eurozone_countries()
    
    # Filter to only the fields we need
    fields = ["country", "currency", "exchange_rate", "currency_code"]
    filtered_records = []
    
    # Track which currency codes we've already seen with their source
    # Prefer "Euro Zone" over individual countries for EUR
    seen_currencies = {}  # currency_code -> country_name
    
    # Track which countries we've already added
    seen_countries = set()
    
    # First pass: process "Euro Zone" and other zone entries first
    zone_entries = [r for r in exchange_rates if 'zone' in r.get("country", "").lower()]
    other_entries = [r for r in exchange_rates if 'zone' not in r.get("country", "").lower()]
    
    euro_rate = None  # Store the Euro rate for Eurozone countries
    
    for record in zone_entries + other_entries:
        country = record.get("country")
        currency_code = match_country_to_currency(country, country_to_currency)
        
        # Capture the Euro rate from Euro Zone
        if country and 'euro zone' in country.lower() and currency_code == 'EUR':
            euro_rate = record.get("exchange_rate")
        
        # Skip if we already have this currency from a zone entry (like Euro Zone)
        if currency_code and currency_code in seen_currencies:
            continue
        
        if currency_code:
            seen_currencies[currency_code] = country
        
        filtered = {field: record.get(field) for field in fields if field != "currency_code"}
        filtered["currency_code"] = currency_code
        filtered_records.append(filtered)
        
        if country:
            seen_countries.add(country.upper())
    
    # Add Eurozone member countries that aren't already in the results
    if euro_rate:
        for eurozone_country in sorted(eurozone_countries):
            if eurozone_country not in seen_countries:
                filtered_records.append({
                    "country": eurozone_country.title(),
                    "currency": "Euro",
                    "exchange_rate": euro_rate,
                    "currency_code": "EUR"
                })
    
    output = {
        "record_date": record_date,
        "total_records": len(filtered_records),
        "data": filtered_records
    }
    
    json_bytes = json.dumps(output, separators=(',', ':')).encode('utf-8')
    gzipped = gzip.compress(json_bytes)
    print(base64.b64encode(gzipped).decode('ascii'))


if __name__ == "__main__":
    main()
