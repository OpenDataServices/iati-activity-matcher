import csv
import glob
import sys

from fuzzywuzzy import fuzz
from lxml import etree

tree = etree.parse("xml_in/cgiar-activities.xml")
cgiar_activities = tree.xpath("/iati-activities/iati-activity[participating-org[@ref='DAC-1601']]")

bmgf_activities = []
crs_channel_codes = [47015, 47017, 47018, 47020, 47021, 47051, 47056, 47057, 51001, 47062, 47063, 47069, 47070, 47075, 47101, 47104]
crs_channel_codes_or_statement = " or ".join(f"@crs-channel-code='{code}'" for code in crs_channel_codes)
for bmgf_file in glob.glob("xml_in/bmgf-activity-*.xml"):
    tree = etree.parse(bmgf_file)
    bmgf_activities += tree.xpath(f"/iati-activities/iati-activity[participating-org[{crs_channel_codes_or_statement}]]")

def titles(activities):
    return {activity.xpath("iati-identifier")[0].text: "\n".join(activity.xpath("title/narrative/text()")) for activity in activities}

cgiar_titles = titles(cgiar_activities)
bmgf_titles = titles(bmgf_activities)

csvwriter = csv.writer(sys.stdout)

for cgiar_iati_identifier, cgiar_title in cgiar_titles.items():
    ratios = []
    for bmgf_iati_identifier, bmgf_title in bmgf_titles.items():
        ratio = fuzz.token_set_ratio(cgiar_title, bmgf_title)
        ratios.append((ratio, bmgf_iati_identifier, bmgf_title))
    ratios.sort(reverse=True)
    top_match = ratios[0]
    csvwriter.writerow([top_match[0], cgiar_iati_identifier, top_match[1], cgiar_title, top_match[2]])
