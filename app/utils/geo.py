"""
app/utils/geo.py - Provides utility functions and constants related to geographical data, such as countries, currencies, and timezones
"""

# app/utils/geo.py
from zoneinfo import available_timezones
import pycountry

# Countries: (alpha_2, name) sorted A–Z
COUNTRIES = sorted(
    ((c.alpha_2, c.name) for c in pycountry.countries),
    key=lambda x: x[1]
)

# Currencies: (alpha_3, "Code — Name") sorted A–Z
CURRENCIES = sorted(
    ((cur.alpha_3, f"{cur.alpha_3} — {cur.name}") for cur in pycountry.currencies),
    key=lambda x: x[1]
)

# Timezones: (iana_key, iana_key) sorted A–Z  <-- the fixed part
TIMEZONES = sorted((tz, tz) for tz in available_timezones())

# End of file
