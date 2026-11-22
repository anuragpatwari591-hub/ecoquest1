"""Educational demo content for EcoQuest (topics, lessons, quizzes, challenges, badges).

Content is general, textbook-level environmental knowledge. No statistics are quoted.
"""

TOPICS = [
    ("Climate Change", "🌡️", "Understand the greenhouse effect, global warming and how people can reduce and adapt to climate change."),
    ("Pollution", "🏭", "Learn about air, water, soil and noise pollution: their causes, effects and solutions."),
    ("Waste Management", "♻️", "Reduce, reuse and recycle: how waste is produced and how to manage it responsibly."),
    ("Water Conservation", "💧", "Why fresh water is limited and how rainwater harvesting and everyday habits protect it."),
    ("Renewable Energy", "☀️", "Explore energy from the sun, wind, water and organic matter that nature replenishes."),
    ("Biodiversity", "🦋", "Discover ecosystems, endangered species and how forests and wildlife can be protected."),
]

# (topic, title, difficulty, introduction, explanation, key_points(list), eco_tip)
LESSONS = [
    ("Climate Change", "The Greenhouse Effect", "Beginner",
     "The Earth stays warm enough for life because some gases in the atmosphere trap heat.",
     "Sunlight warms the Earth's surface. The surface gives off heat as infrared radiation. Greenhouse gases such as carbon dioxide, methane and water vapour absorb part of this heat and send some of it back towards the surface. This natural greenhouse effect keeps the planet livable. Human activities such as burning fossil fuels and clearing forests add extra greenhouse gases, which strengthens the effect.",
     ["Greenhouse gases trap heat in the atmosphere", "Carbon dioxide and methane are important greenhouse gases", "The natural effect is useful; extra human emissions strengthen it"],
     "Switch off lights and fans when you leave a room to save electricity."),
    ("Climate Change", "Global Warming and Carbon Emissions", "Intermediate",
     "Global warming is the long-term rise in the average temperature of the Earth's climate system.",
     "Burning coal, oil and natural gas for electricity, transport and industry releases carbon dioxide. Deforestation reduces the number of trees that absorb carbon dioxide. Scientists describe the result as global warming, which is linked to melting ice, rising sea levels and changing weather patterns. Reducing emissions (mitigation) and preparing for changes (adaptation) are both needed.",
     ["Fossil fuels release carbon dioxide when burned", "Forests absorb carbon dioxide", "Mitigation reduces emissions; adaptation prepares for impacts"],
     "Walk, cycle or use public transport for short trips instead of a private car."),
    ("Pollution", "Air and Noise Pollution", "Beginner",
     "Pollution is the release of harmful substances or energy into the environment.",
     "Air pollution comes from vehicle exhaust, industries, burning of waste and dust. It can cause breathing problems and harms plants and buildings. Noise pollution is unwanted loud sound from traffic, construction and loudspeakers; it can cause stress and sleep problems. Cleaner fuels, public transport, tree planting and noise limits help reduce both.",
     ["Vehicles, factories and waste burning pollute air", "Loud noise can harm health and sleep", "Trees and cleaner transport help reduce pollution"],
     "Avoid burning leaves or garbage; compost garden waste instead."),
    ("Pollution", "Water and Soil Pollution", "Intermediate",
     "Water and soil can be contaminated by waste, chemicals and sewage.",
     "Water pollution happens when untreated sewage, industrial waste, plastic and excess fertilizers enter rivers, lakes and the sea. It harms aquatic life and makes water unsafe. Soil pollution occurs when chemicals, plastics and heavy metals build up in soil, reducing fertility and entering the food chain. Proper waste treatment, reduced chemical use and responsible disposal are key solutions.",
     ["Untreated waste harms rivers and lakes", "Chemicals and plastics reduce soil fertility", "Treatment and responsible disposal reduce contamination"],
     "Never pour oil, paint or chemicals down the drain or onto soil."),
    ("Waste Management", "Reduce, Reuse, Recycle", "Beginner",
     "The 3Rs are a simple order of priority for handling waste.",
     "Reduce means using fewer resources and creating less waste in the first place. Reuse means using an item again, for example refilling a bottle. Recycle means turning used materials such as paper, metal and glass into new products. Reduction is the most effective step because the least waste and energy is used. Segregating dry and wet waste makes recycling easier.",
     ["Reduce first, then reuse, then recycle", "Segregate dry waste and wet waste", "Recycling saves raw materials"],
     "Keep separate bins at home for dry waste and wet waste."),
    ("Waste Management", "Composting, Plastic and E-Waste", "Intermediate",
     "Different kinds of waste need different treatment.",
     "Composting turns kitchen and garden waste into nutrient-rich soil conditioner through natural decomposition. Plastic waste breaks down very slowly and can harm animals and water bodies, so single-use plastic should be avoided. E-waste means discarded electronic devices; it contains useful materials and hazardous substances, so it should go to authorised collection and recycling centres, not ordinary dustbins.",
     ["Composting recycles organic waste into soil conditioner", "Single-use plastics should be avoided", "E-waste must be handed to authorised recyclers"],
     "Carry a cloth bag and a reusable bottle to avoid single-use plastic."),
    ("Water Conservation", "Water Scarcity", "Beginner",
     "Only a small part of the Earth's water is fresh water available for people.",
     "Most of the Earth's water is salty ocean water, and a lot of fresh water is frozen or underground. Growing population, wasteful use, pollution and changing rainfall make water scarce in many regions. Using water carefully at home, in farming and in industry helps protect this limited resource.",
     ["Usable fresh water is limited", "Pollution and wastage increase scarcity", "Every household can help save water"],
     "Turn off the tap while brushing your teeth."),
    ("Water Conservation", "Rainwater Harvesting", "Intermediate",
     "Rainwater harvesting means collecting and storing rain for later use.",
     "Rain falling on roofs can be guided through pipes into storage tanks or into the ground to recharge groundwater. Collected water can be used for gardening, cleaning and, after proper filtering and treatment, for other needs. Harvesting reduces dependence on piped or groundwater supply and reduces water-logging in cities.",
     ["Roof water is collected in tanks or recharge pits", "It helps recharge groundwater", "Collected water needs filtering before drinking"],
     "Place a bucket or barrel under a rain pipe and use the water for plants."),
    ("Renewable Energy", "Solar and Wind Energy", "Beginner",
     "Renewable energy comes from sources that nature replenishes.",
     "Solar panels convert sunlight into electricity, and solar heaters use sunlight to heat water. Wind turbines use moving air to turn a generator. Both produce electricity without burning fuel, so they release no carbon dioxide while operating. Their output depends on weather, so energy storage and a mix of sources are used.",
     ["Solar panels turn sunlight into electricity", "Wind turbines turn wind motion into electricity", "Output varies with weather"],
     "Dry clothes in sunlight instead of using a dryer when possible."),
    ("Renewable Energy", "Hydropower and Biomass", "Intermediate",
     "Water and organic matter can also provide energy.",
     "Hydropower uses flowing or falling water to turn turbines. Large dams can affect rivers and communities, so planning is important. Biomass energy comes from organic matter such as crop residue and animal dung, which can be burned or converted into biogas. Biomass is renewable when the material is replaced, but burning it still releases smoke and carbon dioxide.",
     ["Hydropower uses flowing water to spin turbines", "Biogas can be made from organic waste", "Every energy source has trade-offs to manage"],
     "Choose energy-efficient appliances and switch off devices at the plug when not in use."),
    ("Biodiversity", "Ecosystems and Biodiversity", "Beginner",
     "Biodiversity is the variety of living things on Earth.",
     "An ecosystem is a community of living things interacting with each other and with their non-living surroundings, such as water, soil and air. Forests, wetlands, grasslands and oceans are ecosystems. Each species has a role, for example pollinating plants or recycling nutrients. When many species are lost, ecosystems become less stable.",
     ["An ecosystem includes living and non-living parts", "Each species plays a role", "Loss of species weakens ecosystems"],
     "Plant native trees or flowering plants that attract bees and butterflies."),
    ("Biodiversity", "Endangered Species and Forest Conservation", "Intermediate",
     "Some species are at risk of disappearing forever.",
     "A species is endangered when it faces a very high risk of becoming extinct. Main threats include habitat loss, hunting, pollution and climate change. Forests are home to a large variety of species and help store carbon and protect soil and water. Protected areas, afforestation, responsible consumption and wildlife laws support conservation.",
     ["Habitat loss is a major threat to species", "Forests protect soil, water and wildlife", "Protected areas and laws help conservation"],
     "Use paper carefully and choose recycled paper to reduce pressure on forests."),
]

# topic -> (quiz title, description, [ (question, [4 options], correct index, explanation) ])
QUIZZES = [
    ("Climate Change", "Climate Basics Quiz", "Test your knowledge of the greenhouse effect and global warming.", [
        ("Which gas contributes significantly to the greenhouse effect?", ["Oxygen", "Carbon dioxide", "Nitrogen", "Hydrogen"], 1, "Carbon dioxide absorbs heat in the atmosphere."),
        ("Which activity releases large amounts of carbon dioxide?", ["Planting trees", "Burning fossil fuels", "Using solar panels", "Composting"], 1, "Burning coal, oil and gas releases CO2."),
        ("What is 'mitigation' in climate action?", ["Preparing for floods", "Reducing greenhouse gas emissions", "Moving to a new city", "Ignoring the problem"], 1, "Mitigation reduces emissions; adaptation prepares for impacts."),
        ("Which of these helps absorb carbon dioxide from the air?", ["Forests", "Coal plants", "Diesel engines", "Landfills"], 0, "Trees take in CO2 during photosynthesis."),
        ("The natural greenhouse effect is useful because it...", ["Makes the Earth colder", "Keeps the Earth warm enough for life", "Stops sunlight", "Creates oxygen"], 1, "Without it the Earth would be far too cold."),
        ("Which is an example of climate adaptation?", ["Building flood defences", "Burning more coal", "Cutting forests", "Using more plastic"], 0, "Adaptation means preparing for changes already happening."),
    ]),
    ("Pollution", "Pollution Awareness Quiz", "Check what you know about air, water, soil and noise pollution.", [
        ("Which is a major source of air pollution in cities?", ["Vehicle exhaust", "Rainfall", "Wind", "Moonlight"], 0, "Exhaust from vehicles releases pollutants."),
        ("Noise pollution is best described as...", ["Unwanted loud sound", "Dirty water", "Plastic in soil", "Smoke in air"], 0, "Excess noise can harm health."),
        ("Untreated sewage entering a river causes...", ["Water pollution", "Noise pollution", "Light improvement", "Nothing"], 0, "It contaminates water and harms aquatic life."),
        ("Which practice reduces soil pollution?", ["Dumping chemicals", "Proper waste disposal", "Burning plastic", "Using more pesticides"], 1, "Safe disposal keeps harmful materials out of soil."),
        ("Planting trees along roads helps because trees...", ["Increase traffic", "Can reduce dust and some noise", "Create smoke", "Use plastic"], 1, "Trees trap dust and can soften noise."),
        ("Which is a cleaner way to travel?", ["Public transport", "Many private cars", "Idling engines", "Burning waste"], 0, "Sharing transport reduces emissions per person."),
    ]),
    ("Waste Management", "Waste Warriors Quiz", "Reduce, reuse, recycle: test your waste knowledge.", [
        ("In the 3Rs, which step is the most effective?", ["Recycle", "Reduce", "Dispose", "Burn"], 1, "Using less creates the least waste."),
        ("Kitchen vegetable peels are best handled by...", ["Composting", "Burning", "Throwing in a river", "Mixing with e-waste"], 0, "Composting turns organic waste into soil conditioner."),
        ("Where should old mobile phones and chargers go?", ["Ordinary dustbin", "Authorised e-waste collection", "A river", "Open burning"], 1, "E-waste contains hazardous and valuable materials."),
        ("Which item can usually be reused many times?", ["Plastic carry bag used once", "Cloth shopping bag", "Disposable cup", "Tissue"], 1, "Reusable bags reduce single-use waste."),
        ("Why should dry and wet waste be separated?", ["It makes recycling and composting easier", "It looks nice", "It is a game", "No reason"], 0, "Clean segregated waste is easier to process."),
    ]),
    ("Water Conservation", "Water Guardians Quiz", "How well do you know water scarcity and conservation?", [
        ("What is rainwater harvesting?", ["Collecting and storing rain for use", "Wasting rain", "Making rain", "Polluting rivers"], 0, "Rain is collected from roofs and stored or recharged."),
        ("Which habit saves water?", ["Leaving the tap running", "Turning off the tap while brushing", "Washing the car daily", "Long showers"], 1, "Small habits add up."),
        ("Most of the Earth's water is...", ["Fresh and easy to use", "Salty ocean water", "In clouds", "In rivers"], 1, "Usable fresh water is only a small part."),
        ("Fixing a dripping tap...", ["Wastes more water", "Prevents wastage", "Pollutes water", "Has no effect"], 1, "Drips waste water over time."),
        ("Which can recharge groundwater?", ["Recharge pits for rainwater", "Paving all land", "Burning waste", "Cutting trees"], 0, "Pits let rain soak into the ground."),
    ]),
    ("Renewable Energy", "Clean Energy Quiz", "Test your understanding of solar, wind, hydro and biomass energy.", [
        ("Solar panels convert...", ["Sunlight into electricity", "Wind into water", "Coal into gas", "Sound into heat"], 0, "Photovoltaic cells produce electricity from light."),
        ("Which is a renewable energy source?", ["Coal", "Wind", "Petrol", "Diesel"], 1, "Wind is naturally replenished."),
        ("Hydropower uses...", ["Flowing water", "Burning coal", "Nuclear fuel", "Sunlight"], 0, "Moving water turns turbines."),
        ("Biogas can be produced from...", ["Organic waste", "Glass", "Metal", "Stone"], 0, "Microbes break down organic waste to make biogas."),
        ("A challenge for solar and wind power is that...", ["Output depends on weather", "They burn coal", "They need no equipment", "They produce smoke"], 0, "Storage and mixed sources help."),
    ]),
    ("Biodiversity", "Biodiversity Explorer Quiz", "Explore ecosystems, species and conservation.", [
        ("Biodiversity means...", ["Variety of life", "Only trees", "Only animals", "Only humans"], 0, "It covers all living things and their variety."),
        ("A major threat to wildlife is...", ["Habitat loss", "Clean air", "Rain", "Sunlight"], 0, "Losing habitat leaves species with nowhere to live."),
        ("An ecosystem includes...", ["Only animals", "Living and non-living parts", "Only plants", "Only soil"], 1, "Organisms interact with their surroundings."),
        ("Which action helps forest conservation?", ["Afforestation", "Illegal logging", "Forest fires", "Dumping waste"], 0, "Planting and protecting forests helps."),
        ("An endangered species is one that...", ["Faces a high risk of extinction", "Is very common", "Lives only in zoos", "Is a pet"], 0, "Conservation efforts try to prevent extinction."),
    ]),
]

# (topic, title, description, difficulty, xp)
CHALLENGES = [
    ("Waste Management", "Carry a Reusable Water Bottle", "Use your own refillable bottle all day instead of buying bottled water.", "Easy", 20),
    ("Waste Management", "Plastic-Free Day", "Avoid single-use plastic (bags, straws, cups, wrappers) for one full day.", "Medium", 30),
    ("Waste Management", "Separate Recyclable Waste", "Sort your household waste into dry and wet waste for one day.", "Easy", 20),
    ("Waste Management", "Avoid Unnecessary Printing", "Read or share documents digitally and print only when needed today.", "Easy", 15),
    ("Waste Management", "Start a Compost Pot", "Collect vegetable peels in a pot or bin for composting.", "Medium", 30),
    ("Renewable Energy", "Switch Off Unused Lights", "Switch off lights and fans in empty rooms all day.", "Easy", 15),
    ("Renewable Energy", "Unplug Idle Chargers", "Unplug phone chargers and devices that are not in use.", "Easy", 15),
    ("Climate Change", "Use Public Transport or Carpool", "Travel by bus, train, cycle or share a ride instead of a private car.", "Medium", 30),
    ("Water Conservation", "Save Water While Brushing", "Turn off the tap while brushing your teeth.", "Easy", 15),
    ("Water Conservation", "Fix or Report a Leaking Tap", "Find a dripping tap at home or school and get it repaired.", "Medium", 25),
    ("Biodiversity", "Care for a Plant", "Water and look after a plant or tree today.", "Easy", 20),
    ("Pollution", "Quiet Hour", "Spend one hour without loud music or unnecessary noise and observe the difference.", "Easy", 10),
]

# (name, description, icon, rule_type, rule_value, topic)
BADGES = [
    ("Green Beginner", "Complete your first lesson.", "🌱", "lessons", 1, None),
    ("Eco Learner", "Complete 5 quizzes.", "📘", "quizzes", 5, None),
    ("Recycling Hero", "Complete 5 waste-management challenges.", "♻️", "topic_challenges", 5, "Waste Management"),
    ("Water Guardian", "Complete 3 water-conservation lessons or challenges.", "💧", "topic_activity", 3, "Water Conservation"),
    ("7-Day Streak", "Stay active for seven days in a row.", "🔥", "streak", 7, None),
    ("Eco Champion", "Reach 1000 XP.", "🏆", "xp", 1000, None),
    ("Energy Explorer", "Complete 3 renewable-energy lessons or challenges.", "⚡", "topic_activity", 3, "Renewable Energy"),
]

DEMO_USERS = [
    # name, email, password, role, institution, class
    ("Admin User", "admin@ecoquest.test", "Admin@123", "admin", None, None),
    ("Teacher Demo", "teacher@ecoquest.test", "Teacher@123", "teacher", "Green Valley College", "Class 10-A"),
    ("Anurag Student", "student@ecoquest.test", "Student@123", "student", "Green Valley College", "Class 10-A"),
    ("Riya Sharma", "riya@ecoquest.test", "Student@123", "student", "Green Valley College", "Class 10-A"),
    ("Kabir Mehta", "kabir@ecoquest.test", "Student@123", "student", "Green Valley College", "Class 10-B"),
    ("Sara Khan", "sara@ecoquest.test", "Student@123", "student", "Sunrise Public School", "Class 9-A"),
]
