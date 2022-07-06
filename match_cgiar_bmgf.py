import glob

from lxml import etree

import match

# Load CGIAR activities
recipient_tree = etree.parse("xml_in/cgiar-activities.xml")
# Use only those with BMGF as a participating org
recipient_activities = recipient_tree.xpath(
    "/iati-activities/iati-activity[participating-org[@ref='DAC-1601']]"
)

# Load BMGF activities
funder_activities = []
# Filter to only these Channel Codes, which are specifically for CGIAR and it's members
crs_channel_codes = [
    47015,
    47017,
    47018,
    47020,
    47021,
    47051,
    47056,
    47057,
    51001,
    47062,
    47063,
    47069,
    47070,
    47075,
    47101,
    47104,
]
crs_channel_codes_or_statement = " or ".join(
    f"@crs-channel-code='{code}'" for code in crs_channel_codes
)
for funder_file in glob.glob("xml_in/bmgf-activity-*.xml"):
    tree = etree.parse(funder_file)
    funder_activities += tree.xpath(
        f"/iati-activities/iati-activity[participating-org[{crs_channel_codes_or_statement}]]"
    )

match.match(recipient_activities, funder_activities, recipient_tree=recipient_tree)
