import datetime

from util import hook, urlnorm, timesince, http

UNIFIED_URL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/"

CAN_URL = "https://api.covidactnow.org/v2/state/"

STATE_LIST = [
    "AK", "AL", "AR", "AS", "AZ", "CA", "CO", "CT", "DC", "DE", "FL", "GA", "GU", "HI", "IA", "ID", "IL",
    "IN", "KS", "KY", "LA", "MA", "MD", "ME", "MI", "MN", "MO", "MP", "MS", "MT", "NC", "ND", "NE", "NH",
    "NJ", "NM", "NV", "NY", "OH", "OK", "OR", "PA", "PR", "RI", "SC", "SD", "TN", "TX", "UM", "UT", "VA",
    "VI", "VT", "WA", "WI", "WV", "WY"
]

STATES = {
    "AK": "ALASKA", "AL": "ALABAMA", "AR": "ARKANSAS", "AS": "AMERICAN SAMOA", "AZ": "ARIZONA", "CA": "CALIFORNIA",
    "CO": "COLORADO", "CT": "CONNECTICUT", "DC": "DISTRICT OF COLUMBIA", "DE": "DELAWARE", "FL": "FLORIDA", "GA": "GEORGIA",
    "GU": "GUAM", "HI": "HAWAII", "IA": "IOWA", "ID": "IDAHO", "IL": "ILLINOIS", "IN": "INDIANA", "KS": "KANSAS",
    "KY": "KENTUCKY", "LA": "LOUISIANA", "MA": "MASSACHUSETTS", "MD": "MARYLAND", "ME": "MAINE", "MI": "MICHIGAN",
    "MN": "MINNESOTA", "MO": "MISSOURI", "MP": "NORTHERN MARIANA ISLANDS", "MS": "MISSISSIPPI", "MT": "MONTANA",
    "NA": "NATIONAL", "NC": "NORTH CAROLINA", "ND": "NORTH DAKOTA", "NE": "NEBRASKA", "NH": "NEW HAMPSHIRE",
    "NJ": "NEW JERSEY", "NM": "NEW MEXICO", "NV": "NEVADA", "NY": "NEW YORK", "OH": "OHIO", "OK": "OKLAHOMA",
    "OR": "OREGON", "PA": "PENNSYLVANIA", "PR": "PUERTO RICO", "RI": "RHODE ISLAND", "SC": "SOUTH CAROLINA",
    "SD": "SOUTH DAKOTA", "TN": "TENNESSEE", "TX": "TEXAS", "UT": "UTAH", "VA": "VIRGINIA", "VI": "VIRGIN ISLANDS",
    "VT": "VERMONT", "WA": "WASHINGTON", "WI": "WISCONSIN", "WV": "WEST VIRGINIA", "WY": "WYOMING"
}

NEW_STATES = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California', 'CO': 'Colorado', 
    'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho', 
    'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 
    'ME': 'Maine', 'MD': 'Maryland', 'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 
    'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey', 
    'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma', 
    'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee', 
    'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 
    'WI': 'Wisconsin', 'WY': 'Wyoming', 'DC': 'District of Columbia', 'AS': 'American Samoa', 'GU': 'Guam', 
    'MP': 'Northern Mariana Islands', 'PR': 'Puerto Rico', 'UM': 'United States Minor Outlying Islands', 'VI': 'U.S. Virgin Islands'
}


CA_PT_LIST = ["NL", "PE", "NS", "NB", "QC", "ON", "MB", "SK", "AB", "BC", "YT", "NT", "NU"]

COUNTRY_LIST = ["US", "CA"]


def format_reply(state, new_cases, new_deaths, total_cases, total_deaths, report_date):
    reply = "Covid-19 (\x02{}\x02): " \
    "New Cases: \x02{:,}\x02 | " \
    "New Deaths: \02{:,}\02 | " \
    "Total Cases: \x02{:,}\x02 | " \
    "Total Deaths: \x02{:,}\x02 | " \
    "Report Date: \x02{}\x02" \
    .format(STATES[state], new_cases, new_deaths, total_cases, total_deaths, report_date )
    return reply


@hook.api_key("covidactnow")
@hook.command()
def covid19(inp, api_key=None):
    state = inp.upper()
    if state in STATE_LIST:
        data = http.get_json("{}{}.json?apiKey={}".format(CAN_URL, state, api_key))

        new_cases = data["actuals"]["newCases"]
        new_deaths = data["actuals"]["newDeaths"]
        try:
            date = data["annotations"]["cases"]["anomalies"][0]["date"]
        except:
            date = data["lastUpdatedDate"]
        total_cases = data["actuals"]["cases"]
        total_deaths = data["actuals"]["deaths"]

        reply = format_reply(state, new_cases, new_deaths, total_cases, total_deaths, date)
        return reply
