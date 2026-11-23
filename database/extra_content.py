"""Extra levels of content: intermediate/advanced lessons, harder quizzes and more challenges.

Loaded by init_db.ensure_extra_content() — items are matched by title, so it is safe to run repeatedly.
General, textbook-level knowledge only; no statistics are quoted.
"""

# (topic, title, difficulty, introduction, explanation, [key points], eco_tip)
LESSONS = [
    ("Climate Change", "Carbon Footprint and Climate Action", "Advanced",
     "A carbon footprint is the total greenhouse gas emissions caused by a person, product or activity.",
     "Everyday choices such as travel, electricity use, food and shopping all add to a carbon footprint. Reducing energy use, choosing public transport, "
     "avoiding waste and supporting renewable energy lower it. 'Carbon neutral' means balancing the emissions released with an equal amount removed or offset. "
     "Individual action matters most when it is combined with community and government action.",
     ["A carbon footprint counts greenhouse gas emissions", "Energy, transport and waste are major parts of it", "Carbon neutral means emissions are balanced by removals"],
     "List three things you did today that used energy, and one way to cut each."),
    ("Pollution", "Understanding the Air Quality Index", "Intermediate",
     "The Air Quality Index (AQI) turns complex pollution measurements into one easy number and colour.",
     "On the US AQI scale used in EcoQuest's Eco Pulse, 0–50 is Good, 51–100 is Moderate, 101–150 is Unhealthy for Sensitive Groups, 151–200 is Unhealthy, "
     "201–300 is Very Unhealthy and above 300 is Hazardous. The higher the number, the greater the health concern. Children, older adults and people with heart "
     "or lung conditions are usually affected first. Checking the AQI helps people decide when to limit outdoor activity.",
     ["Higher AQI means more pollution and more health risk", "0–50 is Good; above 150 is Unhealthy for everyone", "Sensitive groups should take care earlier"],
     "Check the Eco Pulse page each day and plan outdoor exercise for cleaner-air hours."),
    ("Pollution", "PM2.5, PM10 and Your Health", "Intermediate",
     "Particulate matter (PM) is a mix of tiny solid and liquid particles floating in the air.",
     "PM10 particles are 10 micrometres across or smaller; PM2.5 particles are 2.5 micrometres or smaller — small enough to reach deep into the lungs. "
     "Sources include vehicle exhaust, construction dust, burning of waste and fuels, and industry. Breathing high levels can irritate the airways and worsen "
     "asthma and heart or lung disease. Reducing burning, controlling dust and using cleaner transport lower particle levels.",
     ["PM2.5 particles are 2.5 micrometres or smaller", "Exhaust, dust and burning are major sources", "Fine particles can reach deep into the lungs"],
     "On high-pollution days keep windows closed during peak traffic hours and avoid burning anything."),
    ("Pollution", "Controlling Pollution at the Source", "Advanced",
     "Preventing pollution is usually cheaper and more effective than cleaning it up later.",
     "Source control means stopping pollutants before they are released: cleaner fuels, catalytic converters in vehicles, filters in factory chimneys, treating "
     "sewage before it reaches rivers, and reducing the use of harmful chemicals. Laws and standards set limits, and monitoring (such as AQI stations) shows whether "
     "they are working. Acid rain, for example, is reduced by cutting sulphur dioxide and nitrogen oxide emissions.",
     ["Prevention beats clean-up", "Catalytic converters and filters reduce emissions", "Monitoring checks whether controls work"],
     "Report open garbage burning or sewage leaks to local authorities."),
    ("Waste Management", "Circular Economy and the Waste Hierarchy", "Advanced",
     "A circular economy keeps materials in use for as long as possible instead of 'take, make, throw away'.",
     "The waste hierarchy ranks options from best to worst: prevent, reuse, recycle, recover energy and, last, dispose. Designing products to be repaired and "
     "recycled, buying less and sharing items all support a circular economy. Extended Producer Responsibility makes manufacturers responsible for their products "
     "at the end of life, for example collecting e-waste.",
     ["Prevention is at the top of the waste hierarchy", "Repair and reuse keep materials in use", "Producers share responsibility for end-of-life products"],
     "Before buying something new, ask: can I repair, borrow or reuse instead?"),
    ("Water Conservation", "Watersheds and Groundwater", "Advanced",
     "A watershed is the area of land that drains rain water into a common river, lake or sea.",
     "What happens anywhere in a watershed — farming, building, waste dumping — affects the water downstream. Groundwater is stored in underground layers called "
     "aquifers and is refilled (recharged) slowly by rain soaking into the ground. Paving land reduces recharge, while rainwater pits, ponds and trees increase it. "
     "Excess fertiliser washing into water can cause eutrophication: algae grow rapidly and oxygen in the water falls.",
     ["A watershed drains to a common water body", "Aquifers are recharged slowly by rainfall", "Excess nutrients cause harmful algal growth"],
     "Use kitchen water from washing vegetables to water plants."),
    ("Renewable Energy", "Energy Efficiency and the Energy Mix", "Advanced",
     "Energy efficiency means using less energy to do the same job.",
     "Efficient appliances, LED lights, good insulation and switching devices off reduce energy demand. The energy mix is the combination of sources a country uses, "
     "such as coal, gas, hydro, solar and wind. Renewable sources are replenished naturally, while fossil fuels are finite and release carbon dioxide when burned. "
     "Because solar and wind vary with the weather, grids use storage and a mix of sources.",
     ["Efficiency cuts energy demand", "The energy mix combines several sources", "Storage helps balance variable renewables"],
     "Look for energy-efficiency star labels when choosing appliances."),
    ("Biodiversity", "Conservation Strategies and Protected Areas", "Advanced",
     "Conservation protects species and the habitats they depend on.",
     "In-situ conservation protects species in their natural home, for example national parks, wildlife sanctuaries and biosphere reserves. Ex-situ conservation "
     "protects them outside their habitat, such as seed banks and zoos. Invasive species, habitat loss and pollution are major threats. Community participation and "
     "laws against poaching and illegal logging make conservation work.",
     ["In-situ conservation protects natural habitats", "Ex-situ conservation includes seed banks and zoos", "Invasive species can outcompete native ones"],
     "Avoid releasing aquarium fish or exotic plants into the wild."),
    ("Biodiversity", "Mangroves, Wetlands and Kolkata's Natural Shields", "Intermediate",
     "Kolkata lies close to two remarkable ecosystems: the Sundarbans mangroves and the East Kolkata Wetlands.",
     "The Sundarbans, in the delta of the Ganga, Brahmaputra and Meghna rivers, is one of the largest mangrove forests in the world and home to the Bengal tiger. "
     "Mangrove roots slow waves and storm surges and protect coastal communities. The East Kolkata Wetlands are a Ramsar-listed wetland where the city's "
     "wastewater is naturally treated and used for fish farming and agriculture. Protecting these ecosystems protects people too.",
     ["The Sundarbans is a vast mangrove forest and tiger habitat", "Mangroves reduce the force of storms and waves", "The East Kolkata Wetlands naturally treat wastewater"],
     "Learn about a wetland or green space near your home and how it helps the city."),
]

# (topic, title, description, difficulty, [(question, [4 options], correct index, explanation)])
QUIZZES = [
    ("Climate Change", "Climate Action Expert", "Advanced questions on carbon footprints and climate action.", "Advanced", [
        ("Which of these is a greenhouse gas?", ["Methane", "Argon", "Helium", "Neon"], 0, "Methane traps heat strongly in the atmosphere."),
        ("A carbon footprint measures...", ["The land a person owns", "The number of trees in a city", "The greenhouse gas emissions caused by a person or activity", "The speed of wind"], 2, "It totals emissions from activities."),
        ("What does 'carbon neutral' mean?", ["Emitting no gases at all", "Balancing emissions with an equal amount removed or offset", "Using only coal", "Planting one tree"], 1, "Emissions and removals balance out."),
        ("Which choice directly reduces electricity-related emissions at home?", ["Using more air conditioning", "Leaving lights on", "Charging devices all night", "Using energy-efficient appliances"], 3, "Efficient appliances use less electricity."),
        ("Rising sea levels are linked to warming because...", ["Ice melts and warmer water expands", "The Moon is closer", "Rivers flow faster", "Clouds become heavier"], 0, "Melting ice and thermal expansion raise sea level."),
    ]),
    ("Pollution", "Air Quality Index Challenge", "Read the AQI like a pro.", "Intermediate", [
        ("AQI stands for...", ["Air Quality Index", "Air Quantity Indicator", "Atmospheric Quality Info", "Air Quick Index"], 0, "It summarises air pollution in one number."),
        ("On the US AQI scale, which range is 'Good'?", ["51–100", "101–150", "0–50", "201–300"], 2, "0–50 is Good."),
        ("PM2.5 refers to particles that are...", ["Larger than 25 mm", "2.5 micrometres or smaller", "Only pollen", "Only water drops"], 1, "Fine particles that reach deep into the lungs."),
        ("Who is usually affected first when air quality worsens?", ["Nobody", "Only athletes", "Only adults", "Children, older adults and people with heart or lung conditions"], 3, "These are sensitive groups."),
        ("When the AQI is 160 (Unhealthy), a sensible step is to...", ["Limit long or heavy outdoor exercise", "Burn leaves outside", "Open all windows at rush hour", "Ignore it"], 0, "Reduce outdoor exertion on unhealthy days."),
    ]),
    ("Pollution", "Pollution Control Expert", "Advanced pollution prevention and control.", "Advanced", [
        ("Which approach is usually most effective?", ["Preventing pollution at the source", "Diluting it with more water", "Moving it elsewhere", "Ignoring it"], 0, "Prevention is better than clean-up."),
        ("Catalytic converters in vehicles reduce...", ["Tyre wear", "Harmful exhaust gases", "Fuel price", "Road noise only"], 1, "They convert gases like carbon monoxide."),
        ("The main purpose of a sewage treatment plant is to...", ["Heat water", "Add colour to water", "Remove contaminants before water is released", "Store rainwater"], 2, "Treated water harms rivers less."),
        ("Acid rain is mainly caused by...", ["Carbon monoxide", "Oxygen", "Water vapour", "Sulphur dioxide and nitrogen oxides"], 3, "They form acids in the atmosphere."),
        ("Which helps reduce traffic noise near homes?", ["Noise barriers and limiting horn use", "Louder horns", "More honking", "Removing all trees"], 0, "Barriers and fewer horns cut noise."),
    ]),
    ("Waste Management", "Circular Economy Challenge", "Advanced questions on the waste hierarchy.", "Advanced", [
        ("A circular economy aims to...", ["Throw items away quickly", "Keep materials in use by reusing, repairing and recycling", "Burn all waste", "Buy more new items"], 1, "Materials stay in use for longer."),
        ("Which option is at the top of the waste hierarchy?", ["Prevention (reduce)", "Disposal", "Energy recovery", "Landfill"], 0, "Avoiding waste is best."),
        ("Biodegradable waste is waste that...", ["Never breaks down", "Is always plastic", "Can be broken down by microorganisms", "Is radioactive"], 2, "Food and garden waste are examples."),
        ("Which of these is hazardous household waste?", ["Vegetable peels", "Newspaper", "Glass jar", "Used batteries"], 3, "Batteries contain harmful chemicals."),
        ("Extended Producer Responsibility makes...", ["Shops close early", "Producers responsible for products at the end of their life", "Consumers pay double", "Recycling illegal"], 1, "Producers help collect and recycle."),
    ]),
    ("Water Conservation", "Water Wise Expert", "Advanced water management.", "Advanced", [
        ("Which helps recharge groundwater?", ["Rainwater recharge pits", "Paving all open ground", "Cutting trees", "Dumping waste in ponds"], 0, "Pits let rain soak into the ground."),
        ("A watershed is...", ["A shed for storing water", "A water tank", "The land area that drains to a common river or lake", "A type of dam"], 2, "All rain in it flows to one outlet."),
        ("Drip irrigation saves water because it...", ["Floods the whole field", "Delivers water slowly to plant roots", "Uses sea water", "Works only at noon"], 1, "Less water is lost to evaporation and runoff."),
        ("Excess fertiliser in lakes can cause...", ["Clearer water", "More fish always", "Lower temperature", "Eutrophication and algal blooms"], 3, "Algae grow fast and oxygen falls."),
        ("Greywater is...", ["Used water from sinks, showers and laundry", "Sea water", "Rainwater only", "Toilet water"], 0, "After treatment it can be reused for gardens."),
    ]),
    ("Renewable Energy", "Energy Mix Expert", "Advanced energy questions.", "Advanced", [
        ("Energy efficiency means...", ["Using more energy", "Using less energy to do the same task", "Only using coal", "Turning off the grid"], 1, "Same result with less energy."),
        ("Which is a non-renewable source?", ["Solar", "Wind", "Natural gas", "Hydropower"], 2, "Fossil fuels are finite."),
        ("A solar water heater uses sunlight to...", ["Heat water directly", "Produce coal", "Pump oil", "Create wind"], 0, "Collectors absorb the Sun's heat."),
        ("A challenge of wind power is that...", ["It burns fuel", "It releases smoke", "It needs coal", "Its output varies with the wind"], 3, "Storage and mixed sources help."),
        ("Biogas mainly contains...", ["Oxygen", "Methane", "Helium", "Neon"], 1, "Microbes produce methane from organic waste."),
    ]),
    ("Biodiversity", "Conservation Expert", "Advanced conservation and Kolkata's ecosystems.", "Advanced", [
        ("Protected areas such as national parks aim to...", ["Build factories", "Increase hunting", "Conserve habitats and wildlife", "Remove all trees"], 2, "They protect species in their natural home."),
        ("Mangrove forests protect coasts by...", ["Reducing the force of waves and storm surges", "Raising sea level", "Blocking rivers", "Producing oil"], 0, "Dense roots slow the water."),
        ("Which is an example of in-situ conservation?", ["A seed bank", "A wildlife sanctuary", "A zoo", "A botanical garden greenhouse"], 1, "Species are protected in their natural habitat."),
        ("Invasive species can harm ecosystems because they...", ["Are always small", "Never reproduce", "Only live in zoos", "Can outcompete native species"], 3, "They spread without natural controls."),
        ("The Sundarbans near Kolkata is famous for...", ["Its mangrove forest and Bengal tigers", "Its deserts", "Its glaciers", "Its coral atolls"], 0, "It is a vast mangrove delta forest."),
    ]),
]

# (topic, title, description, difficulty, xp)
CHALLENGES = [
    ("Climate Change", "Walk or Cycle a Short Trip", "Replace one short vehicle trip with walking or cycling today.", "Easy", 20),
    ("Biodiversity", "Plant a Sapling", "Plant a sapling or seeds of a native plant and water it.", "Medium", 30),
    ("Waste Management", "Shop with a Cloth Bag", "Carry your own cloth bag for shopping and refuse plastic bags.", "Easy", 15),
    ("Water Conservation", "Five-Minute Shower", "Keep your shower to five minutes or use a bucket bath today.", "Easy", 15),
    ("Pollution", "Check Today's Air Quality", "Open Eco Pulse, check Kolkata's AQI and share one safety tip with your family.", "Easy", 10),
    ("Renewable Energy", "Use Natural Light", "Use daylight instead of electric lights in the daytime.", "Easy", 10),
]
