"""Eco Pulse: live air quality for Kolkata (Open-Meteo air-quality API, no key) + daily eco brief.

Data source: Open-Meteo air-quality API (modelled CAMS data, US AQI scale). The only thing sent
is Kolkata's latitude/longitude. Results are cached for 30 minutes; the latest reading is stored
in MySQL (air_readings) so the page still shows something when offline.
"""
import json
import time
import urllib.request
from collections import defaultdict
from datetime import date

CITY = {"name": "Kolkata", "lat": 22.5726, "lon": 88.3639}
API = ("https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}"
       "&current=us_aqi,pm10,pm2_5&hourly=us_aqi&past_days=7&forecast_days=1&timezone=Asia%2FKolkata")
SOURCE = "Open-Meteo air-quality API (US AQI, modelled data)"

# (low, high, name, colour, emoji)
CATEGORIES = [
    (0, 50, "Good", "#16a34a", "😊"),
    (51, 100, "Moderate", "#ca8a04", "🙂"),
    (101, 150, "Unhealthy for sensitive groups", "#ea580c", "😷"),
    (151, 200, "Unhealthy", "#dc2626", "🤒"),
    (201, 300, "Very unhealthy", "#7c3aed", "🚨"),
    (301, 100000, "Hazardous", "#7f1d1d", "☠️"),
]
GUESSES = {"good": "Good or Moderate (0–100)", "sensitive": "Unhealthy for sensitive groups (101–150)", "bad": "Unhealthy or worse (151+)"}

TIPS = {
    "Good": ["Great day for outdoor games, walking or cycling.", "Open windows to let fresh air in.", "Keep it clean — avoid burning waste."],
    "Moderate": ["Most people can be active outdoors.", "If you have asthma, keep your inhaler handy.", "Choose walking or public transport to keep the air cleaner."],
    "Unhealthy for sensitive groups": ["Children, older adults and people with asthma should limit long outdoor exercise.", "Avoid busy roads during rush hour.", "Never burn leaves or garbage."],
    "Unhealthy": ["Reduce long or heavy outdoor exercise.", "Keep windows closed during peak traffic hours.", "A well-fitted N95-type mask can reduce exposure to fine particles."],
    "Very unhealthy": ["Avoid outdoor exercise; stay indoors where possible.", "Keep windows and doors closed.", "Follow local health advisories."],
    "Hazardous": ["Stay indoors and keep activity low.", "Follow official health warnings.", "Check on elderly neighbours and family."],
}

FACTS = [
    "PM2.5 particles are 2.5 micrometres or smaller — small enough to reach deep into the lungs.",
    "Trees absorb carbon dioxide and release oxygen during photosynthesis.",
    "Recycling aluminium needs far less energy than making new aluminium from ore.",
    "Plastic bags break down very slowly and can stay in the environment for many years.",
    "A dripping tap can waste a surprising amount of water in a single day.",
    "LED bulbs give the same light as old incandescent bulbs while using less electricity.",
    "Composting kitchen waste returns nutrients to the soil and keeps it out of landfills.",
    "The Sundarbans near Kolkata is one of the world's largest mangrove forests.",
    "The Sundarbans is home to the Bengal tiger.",
    "Sharing rides and using public transport means fewer vehicles and less exhaust.",
    "Burning garbage in the open releases smoke and harmful gases.",
    "E-waste contains valuable metals and harmful substances — give it to authorised recyclers.",
    "The East Kolkata Wetlands naturally treat much of the city's wastewater.",
    "Switching appliances off at the plug avoids standby power use.",
    "Rainwater harvesting refills groundwater and reduces street flooding.",
    "Solar panels make electricity without burning any fuel.",
    "Long exposure to loud noise can disturb sleep and raise stress.",
    "Native plants support local insects, birds and healthy soil.",
    "Single-use plastics are often used for minutes but last for years.",
    "A reusable bottle can replace hundreds of single-use bottles.",
    "Wind turbines turn moving air into electricity.",
    "Biogas can be made from kitchen scraps and animal dung.",
    "Cool winter air can trap pollution near the ground, so smog is often worse in winter.",
    "Using a bucket instead of a hose saves a lot of water.",
    "Carbon dioxide and methane are greenhouse gases that trap heat.",
    "Bees and butterflies pollinate many of the plants that give us food.",
    "Every species in an ecosystem has a role; losing many makes ecosystems unstable.",
    "Printing only when needed saves paper, trees and energy.",
    "Separating wet and dry waste makes recycling and composting easier.",
    "Mangrove roots slow down waves and protect coasts from storms.",
]

_cache = {"t": 0, "data": None}


def category(aqi):
    for lo, hi, name, colour, emoji in CATEGORIES:
        if lo <= aqi <= hi:
            return {"name": name, "colour": colour, "emoji": emoji}
    return {"name": "Unknown", "colour": "#6b7280", "emoji": "❔"}


def guess_group(aqi):
    return "good" if aqi <= 100 else "sensitive" if aqi <= 150 else "bad"


def daily_fact(today=None):
    today = today or date.today()
    return FACTS[today.toordinal() % len(FACTS)]


def _fetch():
    url = API.format(lat=CITY["lat"], lon=CITY["lon"])
    req = urllib.request.Request(url, headers={"User-Agent": "EcoQuest-education-app"})
    with urllib.request.urlopen(req, timeout=8) as r:
        d = json.load(r)
    cur = d["current"]
    by_day = defaultdict(list)
    for t, v in zip(d["hourly"]["time"], d["hourly"]["us_aqi"]):
        if v is not None:
            by_day[t[:10]].append(v)
    history = [{"day": k, "aqi": round(sum(v) / len(v))} for k, v in sorted(by_day.items()) if k <= cur["time"][:10]]
    return {"aqi": int(round(cur["us_aqi"])), "pm25": cur.get("pm2_5"), "pm10": cur.get("pm10"),
            "time": cur["time"].replace("T", " "), "history": history[-8:], "live": True}


def get_air(max_age=1800):
    """Return live data (cached) or None if the internet/API is unavailable."""
    if _cache["data"] and time.time() - _cache["t"] < max_age:
        return _cache["data"]
    try:
        data = _fetch()
    except Exception:
        return None
    _cache.update(t=time.time(), data=data)
    return data
