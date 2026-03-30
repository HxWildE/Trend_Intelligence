class GeoMapper:

    def __init__(self):

        self.city_to_state = {
            "bangalore": "karnataka",
            "bengaluru": "karnataka",
            "mysore": "karnataka",

            "chennai": "tamil nadu",
            "coimbatore": "tamil nadu",
            "madurai": "tamil nadu",

            "mumbai": "maharashtra",
            "pune": "maharashtra",

            "hyderabad": "telangana",

            "delhi": "delhi",
            "new delhi": "delhi",

            "kolkata": "west bengal",

            "ahmedabad": "gujarat",

            "jaipur": "rajasthan",

            "lucknow": "uttar pradesh",

            "kochi": "kerala",

            "visakhapatnam": "andhra pradesh",

            "patna": "bihar",

            "bhubaneswar": "odisha",

            "guwahati": "assam",

            "ranchi": "jharkhand",

            "raipur": "chhattisgarh",

            "dehradun": "uttarakhand",

            "shimla": "himachal pradesh",

            "goa": "goa",
            "panaji": "goa"
        }

        self.alias_map = {
            "blr": "bangalore",
            "bglr": "bangalore",
            "hyd": "hyderabad",
            "mum": "mumbai",
            "del": "delhi",
            "kol": "kolkata",
            "chn": "chennai",
            "pnq": "pune"
        }

    def normalize_location(self, loc):
        loc = loc.lower().strip()

        if loc in self.alias_map:
            loc = self.alias_map[loc]

        return loc

    def map_location(self, locations):
        states = []

        for loc in locations:
            key = self.normalize_location(loc)

            if key in self.city_to_state:
                states.append(self.city_to_state[key])

        return list(set(states))