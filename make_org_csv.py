import csv
import json

with open("out/participating_org_ref_dict_by_reporting_org.json") as fp:
    participating_org_ref_dict_by_reporting_org = json.load(fp)

with open("out/participating_org_details_by_orgs.json") as fp:
    participating_org_details_by_orgs = json.load(fp)

with open("out/dataset_by_reporting_org.json") as fp:
    dataset_by_reporting_org = json.load(fp)

linked_orgs_csv = csv.writer(open("out/linked_orgs.csv", "w"))

for participating_org_ref_dicts in participating_org_ref_dict_by_reporting_org.values():
    for pord in participating_org_ref_dicts:
        if pord["participating_org_ref"] in dataset_by_reporting_org:
            linked_orgs_csv.writerow(
                [
                    pord["reporting_org"],
                    pord["dataset"],
                    pord["participating_org_ref"],
                    ",".join(dataset_by_reporting_org[pord["participating_org_ref"]]),
                    len(
                        participating_org_details_by_orgs[pord["reporting_org"]][
                            pord["participating_org_ref"]
                        ]
                    ),
                    len(
                        [
                            participating_org_details["participating_org_activity_id"]
                            for participating_org_details in participating_org_details_by_orgs[
                                pord["reporting_org"]
                            ][
                                pord["participating_org_ref"]
                            ]
                            if participating_org_details[
                                "participating_org_activity_id"
                            ]
                        ]
                    ),
                ]
            )
