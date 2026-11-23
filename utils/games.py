"""Mini-game data and grading (no database needed).

Each game is a sorting game: the player drops items into the correct bin.
The server picks which items are played, re-grades the submitted answers and awards XP,
so XP is never trusted from the browser. (The browser receives the correct bins so it can
show instant feedback; this is a casual game and XP is capped once per day per game.)
"""
import random

import config

ITEMS_PER_ROUND = 8

GAMES = {
    "waste-sort": {
        "title": "Waste Sorting Rush",
        "icon": "♻️",
        "description": "Sort each item into the right bin before the timer runs out.",
        "bins": [("recycle", "Recycle", "♻️"), ("compost", "Compost", "🌱"),
                 ("ewaste", "E-waste", "🔌"), ("general", "General waste", "🗑️")],
        "items": [
            ("bottle", "🧴", "Plastic bottle", "recycle", "Clean plastic bottles can be recycled."),
            ("paper", "📰", "Old newspaper", "recycle", "Paper is recycled into new paper."),
            ("jar", "🫙", "Glass jar", "recycle", "Glass can be recycled many times."),
            ("can", "🥫", "Metal can", "recycle", "Metals are widely recycled."),
            ("peel", "🍌", "Banana peel", "compost", "Fruit and vegetable waste can be composted."),
            ("veg", "🥬", "Vegetable scraps", "compost", "Kitchen scraps turn into compost."),
            ("tea", "🍵", "Used tea leaves", "compost", "Tea leaves are organic and compostable."),
            ("leaves", "🍂", "Dry garden leaves", "compost", "Leaves decompose into soil conditioner."),
            ("phone", "📱", "Old mobile phone", "ewaste", "Electronics must go to authorised e-waste collection."),
            ("battery", "🔋", "Dead batteries", "ewaste", "Batteries contain hazardous materials."),
            ("charger", "🔌", "Broken charger", "ewaste", "Cables and chargers are e-waste."),
            ("tissue", "🧻", "Used tissue", "general", "Soiled tissue cannot be recycled."),
            ("wrapper", "🍟", "Chip packet wrapper", "general", "Multi-layer wrappers are hard to recycle."),
            ("cup", "☕", "Broken ceramic cup", "general", "Ceramics are not recycled with glass."),
        ],
    },
    "pollution-detective": {
        "title": "Pollution Detective",
        "icon": "🕵️",
        "description": "Spot which type of pollution each cause creates: air, water, soil or noise.",
        "bins": [("air", "Air", "💨"), ("water", "Water", "💧"), ("soil", "Soil", "🌍"), ("noise", "Noise", "🔊")],
        "items": [
            ("exhaust", "🚗", "Vehicle exhaust smoke", "air", "Exhaust releases gases and particles into the air."),
            ("chimney", "🏭", "Factory chimney smoke", "air", "Industrial smoke pollutes the air."),
            ("burning", "🔥", "Burning garbage", "air", "Open burning releases smoke and toxic gases."),
            ("sewage", "🚰", "Untreated sewage in a river", "water", "Sewage contaminates rivers and lakes."),
            ("oil", "🛢️", "Oil spill in the sea", "water", "Oil spreads on water and harms sea life."),
            ("chemicals", "🧪", "Factory chemicals in a lake", "water", "Chemical waste poisons water bodies."),
            ("plastic", "🛍️", "Plastic dumped on farmland", "soil", "Plastic stays in soil for a very long time."),
            ("pesticide", "🌾", "Too much pesticide on fields", "soil", "Excess chemicals reduce soil health."),
            ("mining", "⛏️", "Mining waste heaps", "soil", "Waste rock and chemicals contaminate soil."),
            ("drill", "🚧", "Loud construction drilling", "noise", "Loud machinery causes noise pollution."),
            ("horn", "📯", "Constant traffic honking", "noise", "Horns add to city noise."),
            ("speaker", "📢", "Loudspeakers late at night", "noise", "Loud sound disturbs sleep and health."),
        ],
    },
    "myth-buster": {
        "title": "Eco Myth Buster",
        "icon": "🧐",
        "description": "Fact or myth? Bust common environmental myths against the clock.",
        "bins": [("fact", "Fact", "✅"), ("myth", "Myth", "❌")],
        "items": [
            ("paper", "📄", "Recycling paper reduces the need for new raw material.", "fact", "Recycled fibre replaces some new wood pulp."),
            ("onetree", "🌳", "Planting one tree instantly cancels a whole city's pollution.", "myth", "Trees help, but pollution must be cut at the source."),
            ("bags", "🛍️", "Plastic bags disappear within a few days.", "myth", "They break down very slowly and persist for years."),
            ("lights", "💡", "Switching off unused lights saves electricity.", "fact", "No light, no power used."),
            ("solar", "☀️", "Solar panels only work in summer.", "myth", "They work all year; output depends on sunlight."),
            ("compost", "🍂", "Composting food waste reduces landfill waste.", "fact", "Organic waste becomes useful compost."),
            ("airall", "😷", "Air pollution only affects people who already have lung disease.", "myth", "It can affect everyone; sensitive groups first."),
            ("tap", "🚰", "Fixing a dripping tap saves water.", "fact", "Small drips add up to a lot of water."),
            ("burn", "🔥", "Burning garbage is a safe way to get rid of waste.", "myth", "It releases smoke and toxic gases."),
            ("wetland", "🦆", "Wetlands can help clean water naturally.", "fact", "Plants and microbes filter and treat water."),
            ("cycle", "🚲", "Cycling short distances instead of driving cuts exhaust.", "fact", "No fuel burned, no exhaust."),
            ("ewaste", "📱", "Old phones can go in the normal dustbin.", "myth", "E-waste must go to authorised recyclers."),
        ],
    },
    "renewable-sort": {
        "title": "Renewable or Not?",
        "icon": "⚡",
        "description": "Sort each energy source: renewable or non-renewable?",
        "bins": [("renewable", "Renewable", "♻️"), ("nonrenewable", "Non-renewable", "⛽")],
        "items": [
            ("solar", "☀️", "Solar energy", "renewable", "Sunlight is replenished every day."),
            ("wind", "🌬️", "Wind energy", "renewable", "Wind is driven by the Sun's heating of the air."),
            ("hydro", "💧", "Hydropower", "renewable", "Flowing water is renewed by the water cycle."),
            ("biomass", "🌾", "Biomass (crop residue)", "renewable", "Renewable when the plants are regrown."),
            ("tidal", "🌊", "Tidal energy", "renewable", "Tides repeat every day."),
            ("geo", "🌋", "Geothermal energy", "renewable", "Heat from inside the Earth."),
            ("coal", "⚫", "Coal", "nonrenewable", "A fossil fuel formed over millions of years."),
            ("petrol", "⛽", "Petroleum (petrol, diesel)", "nonrenewable", "A finite fossil fuel."),
            ("gas", "🔥", "Natural gas", "nonrenewable", "A finite fossil fuel."),
            ("kerosene", "🪔", "Kerosene", "nonrenewable", "Made from petroleum."),
        ],
    },
    "water-wise": {
        "title": "Water Wise",
        "icon": "💧",
        "description": "Does this habit save water or waste it?",
        "bins": [("save", "Saves water", "💚"), ("waste", "Wastes water", "💸")],
        "items": [
            ("brush", "🪥", "Turning off the tap while brushing", "save", "The tap runs only when needed."),
            ("leak", "🔧", "Fixing a leaking tap", "save", "Stops constant loss."),
            ("bucket", "🪣", "Taking a bucket bath", "save", "Usually uses less than a long shower."),
            ("rain", "🌧️", "Harvesting rainwater from the roof", "save", "Collects water that would run off."),
            ("fullload", "🧺", "Running the washing machine with a full load", "save", "Fewer washes for the same clothes."),
            ("dishes", "🍽️", "Washing dishes under a running tap", "waste", "Use a filled basin instead."),
            ("hose", "🚗", "Washing the car with a hose every day", "waste", "A bucket uses far less."),
            ("shower", "🚿", "Taking very long showers", "waste", "Shorter showers save water."),
            ("noon", "🌞", "Watering plants at hot noon", "waste", "Much evaporates; water in the morning or evening."),
            ("pavement", "🧹", "Washing the pavement with a hose", "waste", "Sweep instead."),
        ],
    },
}


def pick_items(game_key, rng=random):
    """Choose this round's items (ids only) at random."""
    ids = [i[0] for i in GAMES[game_key]["items"]]
    return rng.sample(ids, min(ITEMS_PER_ROUND, len(ids)))


def items_for_client(game_key, item_ids):
    lookup = {i[0]: i for i in GAMES[game_key]["items"]}
    return [{"id": lookup[i][0], "emoji": lookup[i][1], "name": lookup[i][2], "bin": lookup[i][3], "why": lookup[i][4]}
            for i in item_ids]


def grade_game(game_key, item_ids, answers):
    """Score the round. `item_ids` are the items the server picked; `answers` maps item id -> bin key.

    Items that were not answered count as wrong. Returns (score, total, review list).
    """
    lookup = {i[0]: i for i in GAMES[game_key]["items"]}
    valid_bins = {b[0] for b in GAMES[game_key]["bins"]}
    review, score = [], 0
    for item_id in item_ids:
        chosen = answers.get(item_id)
        chosen = chosen if chosen in valid_bins else None
        correct = lookup[item_id][3]
        ok = chosen == correct
        score += ok
        review.append({"emoji": lookup[item_id][1], "name": lookup[item_id][2], "chosen": chosen,
                       "correct": correct, "ok": ok, "why": lookup[item_id][4]})
    return score, len(item_ids), review


def game_xp(score, total):
    xp = score * config.XP_GAME_PER_CORRECT
    if total and score == total:
        xp += config.XP_GAME_PERFECT_BONUS
    return xp
