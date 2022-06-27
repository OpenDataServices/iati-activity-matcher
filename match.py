import csv
import glob
import os

from fuzzywuzzy import fuzz
from lxml import etree

# Load CGIAR activities
cgiar_tree = etree.parse("xml_in/cgiar-activities.xml")
# Use only those with BMGF as a participating org
cgiar_activities = cgiar_tree.xpath("/iati-activities/iati-activity[participating-org[@ref='DAC-1601']]")

# Load BMGF activities
bmgf_activities = []
# Filter to only these Channel Codes, which are specifically for CGIAR and it's members
crs_channel_codes = [47015, 47017, 47018, 47020, 47021, 47051, 47056, 47057, 51001, 47062, 47063, 47069, 47070, 47075, 47101, 47104]
crs_channel_codes_or_statement = " or ".join(f"@crs-channel-code='{code}'" for code in crs_channel_codes)
for bmgf_file in glob.glob("xml_in/bmgf-activity-*.xml"):
    tree = etree.parse(bmgf_file)
    bmgf_activities += tree.xpath(f"/iati-activities/iati-activity[participating-org[{crs_channel_codes_or_statement}]]")

def activity_lookup(activities):
    return {activity.xpath("iati-identifier")[0].text: activity for activity in activities}

cgiar_activity_lookup = activity_lookup(cgiar_activities)
bmgf_activity_lookup = activity_lookup(bmgf_activities)

def titles(activities):
    return {activity.xpath("iati-identifier")[0].text: "\n".join(activity.xpath("title/narrative/text()")) for activity in activities}

cgiar_titles = titles(cgiar_activities)
bmgf_titles = titles(bmgf_activities)

os.makedirs("out", exist_ok=True)
csvwriter = csv.writer(open("out/matches.csv", "w"))

for cgiar_iati_identifier, cgiar_title in cgiar_titles.items():
    ratios = []
    for bmgf_iati_identifier, bmgf_title in bmgf_titles.items():
        ratio = fuzz.token_set_ratio(cgiar_title, bmgf_title)
        ratios.append((ratio, bmgf_iati_identifier, bmgf_title))
    ratios.sort(reverse=True)
    top_match = ratios[0]

    ratio, bmgf_iati_identifier, bmgf_title = top_match

    if ratio >= 90:
        print(cgiar_iati_identifier)
        participating_org = cgiar_activity_lookup[cgiar_iati_identifier].find("participating-org[@ref='DAC-1601']")
        participating_org.attrib["activity-id"] = bmgf_iati_identifier

    transactions = cgiar_activity_lookup[cgiar_iati_identifier].findall("transaction")
    transactions = [transaction for transaction in transactions if transaction.xpath("transaction-type/@code")[0] != "2"]
    # Assume everything's USD
    cgiar_values = [value.text for value in [transaction.find("value") for transaction in transactions]]

    assert len(cgiar_values) == 1

    transactions = bmgf_activity_lookup[bmgf_iati_identifier].findall("transaction")
    bmgf_values = [value.text for value in [transaction.find("value") for transaction in transactions]]
    bmgf_value_to_transaction = {transaction.find("value").text:transaction for transaction in transactions}

    transaction_match = cgiar_values[0] in bmgf_values

    csvwriter.writerow([ratio, cgiar_iati_identifier, bmgf_iati_identifier, cgiar_title, bmgf_title, transaction_match])

cgiar_tree.write("out/cgiar-activities-matched.xml")
