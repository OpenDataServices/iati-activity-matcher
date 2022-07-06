import json
import os
from collections import defaultdict

import iatikit

if not os.path.isdir("__iatikitcache__"):
    iatikit.download.data()

os.makedirs("out", exist_ok=True)

registry = iatikit.data()
participating_org_details_by_orgs = defaultdict(lambda: defaultdict(list))
participating_org_ref_dict_by_reporting_org = defaultdict(list)
dataset_by_reporting_org = defaultdict(list)

for i, activity in enumerate(registry.activities):
    try:
        reporting_org = activity.etree.find("reporting-org").attrib["ref"]
        participating_org_refs_and_activity_ids = [
            (p.attrib["ref"], p.attrib.get("activity-id"))
            for p in activity.etree.findall("participating-org")
            if "ref" in p.attrib
            and p.attrib["ref"] != reporting_org
            and p.attrib["role"] == "1"
        ]
    except (KeyError, AttributeError):
        print("Skipping", i, activity)
        continue
    participating_org_refs = {p for p, _ in participating_org_refs_and_activity_ids}
    if reporting_org not in participating_org_ref_dict_by_reporting_org:
        participating_org_ref_dict_by_reporting_org[reporting_org] = []
    for (
        participating_org_ref,
        participating_org_activity_id,
    ) in participating_org_refs_and_activity_ids:
        participating_org_details_by_orgs[reporting_org][participating_org_ref].append(
            {
                "dataset": activity.dataset.name,
                "iati_identifier": activity.iati_identifier,
                "reporting_org": reporting_org,
                "partcipiating_org_ref": participating_org_ref,
                "participating_org_activity_id": participating_org_activity_id,
            }
        )
    for participating_org_ref in participating_org_refs:
        participating_org_ref_dict = {
            "dataset": activity.dataset.name,
            "reporting_org": reporting_org,
            "participating_org_ref": participating_org_ref,
        }
        if i % 1000 == 0:
            print(i, participating_org_ref_dict)
        participating_org_ref_dict_list = participating_org_ref_dict_by_reporting_org[
            reporting_org
        ]
        if participating_org_ref_dict not in participating_org_ref_dict_list:
            participating_org_ref_dict_list.append(participating_org_ref_dict)
    if activity.dataset.name not in dataset_by_reporting_org[reporting_org]:
        dataset_by_reporting_org[reporting_org].append(activity.dataset.name)
    if i != 0 and i % 100000 == 0:
        with open("out/participating_org_ref_dict_by_reporting_org.json", "w") as fp:
            json.dump(participating_org_ref_dict_by_reporting_org, fp)
        with open("out/participating_org_details_by_orgs.json", "w") as fp:
            json.dump(participating_org_details_by_orgs, fp)
        with open("out/dataset_by_reporting_org.json", "w") as fp:
            json.dump(dataset_by_reporting_org, fp)

with open("out/participating_org_ref_dict_by_reporting_org.json", "w") as fp:
    json.dump(participating_org_ref_dict_by_reporting_org, fp)
with open("out/participating_org_details_by_orgs.json", "w") as fp:
    json.dump(participating_org_details_by_orgs, fp)
with open("out/dataset_by_reporting_org.json", "w") as fp:
    json.dump(dataset_by_reporting_org, fp)
