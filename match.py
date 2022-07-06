import csv
import json
import os

import click
import iatikit
from fuzzywuzzy import fuzz


def activities_by_id(activities):
    return {
        activity.xpath("iati-identifier")[0].text: activity for activity in activities
    }


def titles_by_activity_id(activities):
    return {
        activity.xpath("iati-identifier")[0].text: "\n".join(
            activity.xpath("title/narrative/text()")
        )
        for activity in activities
    }


def match(recipient_activities, funder_activities, recipient_tree=None):

    recipient_activities_by_id = activities_by_id(recipient_activities)
    funder_activities_by_id = activities_by_id(funder_activities)

    recipient_titles = titles_by_activity_id(recipient_activities)
    funder_titles = titles_by_activity_id(funder_activities)

    os.makedirs("out", exist_ok=True)
    csvwriter = csv.writer(open("out/matches.csv", "w"))

    for recipient_iati_identifier, recipient_title in recipient_titles.items():
        ratios = []
        for funder_iati_identifier, funder_title in funder_titles.items():
            ratio = fuzz.token_set_ratio(recipient_title, funder_title)
            ratios.append((ratio, funder_iati_identifier, funder_title))
        ratios.sort(reverse=True)
        top_match = ratios[0]

        ratio, funder_iati_identifier, funder_title = top_match

        if ratio >= 90:
            participating_org = recipient_activities_by_id[
                recipient_iati_identifier
            ].find("participating-org[@ref='DAC-1601']")
            participating_org.attrib["activity-id"] = funder_iati_identifier

        recipient_transactions = recipient_activities_by_id[
            recipient_iati_identifier
        ].findall("transaction")
        recipient_transactions = [
            transaction
            for transaction in recipient_transactions
            if transaction.xpath("transaction-type/@code")[0] != "2"
        ]
        # Assume everything's USD
        recipient_values = [
            value.text
            for value in [
                transaction.find("value") for transaction in recipient_transactions
            ]
        ]

        assert len(recipient_values) == 1

        funder_transactions = funder_activities_by_id[funder_iati_identifier].findall(
            "transaction"
        )
        funder_values = [
            value.text
            for value in [
                transaction.find("value") for transaction in funder_transactions
            ]
        ]

        transaction_match = recipient_values[0] in funder_values

        csvwriter.writerow(
            [
                ratio,
                recipient_iati_identifier,
                funder_iati_identifier,
                recipient_title,
                funder_title,
                transaction_match,
            ]
        )

        if recipient_tree and ratio >= 90 and transaction_match:
            print(recipient_iati_identifier)
            recipient_transactions[0].find("provider-org").attrib[
                "provider-activity-id"
            ] = funder_iati_identifier

    if recipient_tree:
        recipient_tree.write("out/recipient-activities-matched.xml")


@click.command()
@click.option("--recipient-org-ref", required=True)
@click.option("--funder-org-ref", required=True)
def match_command(recipient_org_ref, funder_org_ref):
    with open("out/dataset_by_reporting_org.json") as fp:
        dataset_by_reporting_org = json.load(fp)

    registry = iatikit.data()

    def get_activities(reporting_org_ref, xpath):
        activities = []
        dataset_names = dataset_by_reporting_org[reporting_org_ref]
        for dataset_name in dataset_names:
            dataset = registry.datasets.find(name=dataset_name)
            activities += dataset.etree.xpath(xpath)
        return activities

    recipient_activities = get_activities(
        recipient_org_ref,
        f"/iati-activities/iati-activity[reporting-org/@ref='{recipient_org_ref}' and participating-org[@ref='{funder_org_ref}' and @role='1']]",
    )
    funder_activities = get_activities(
        funder_org_ref,
        f"/iati-activities/iati-activity[reporting-org/@ref='{funder_org_ref}']",
    )
    print(len(recipient_activities), len(funder_activities))
    match(recipient_activities, funder_activities)


if __name__ == "__main__":
    match_command()
