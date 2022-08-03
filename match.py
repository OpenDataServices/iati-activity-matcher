import csv
import json
import os

import click
import iatikit
from thefuzz import fuzz

MIN_RATIO = 70


def first_or_none(l):
    if len(l):
        return l[0]


def activities_by_id(activities):
    return {
        activity.find("iati-identifier").text: activity
        for activity in activities
        if activity.find("iati-identifier") is not None
    }


def titles_by_activity_id(activities):
    return {
        activity.find("iati-identifier").text: "\n".join(
            activity.xpath("title/narrative/text()")
        )
        for activity in activities
        if activity.find("iati-identifier") is not None
    }


def match(
    recipient_activities,
    funder_activities,
    csvwriter,
    transaction_tolerance=0,
    update_xml=False,
    funder_org_ref=None,
):
    if len(recipient_activities) == 0 or len(funder_activities) == 0:
        return

    recipient_activities_by_id = activities_by_id(recipient_activities)
    funder_activities_by_id = activities_by_id(funder_activities)

    recipient_titles = titles_by_activity_id(recipient_activities)
    funder_titles = titles_by_activity_id(funder_activities)

    for recipient_iati_identifier, recipient_title in recipient_titles.items():
        if not recipient_title.strip(" \n"):
            continue
        ratios = []
        for funder_iati_identifier, funder_title in funder_titles.items():
            if not funder_title.strip(" \n"):
                continue
            ratio = fuzz.token_sort_ratio(recipient_title, funder_title)
            ratios.append((ratio, funder_iati_identifier, funder_title))
        if not ratios:
            continue
        ratios.sort(reverse=True)
        top_match = ratios[0]

        ratio, funder_iati_identifier, funder_title = top_match

        if update_xml and ratio >= MIN_RATIO:
            participating_org = recipient_activities_by_id[
                recipient_iati_identifier
            ].find(f"participating-org[@ref='{funder_org_ref}']")
            if participating_org is not None:
                participating_org.attrib["activity-id"] = funder_iati_identifier

        transaction_match = False
        # We could be matching disbursements, which is code 1 for incoming funds, and 3 for the outgoing funds
        # Or, matching commitments which are 11 incoming and 2 outgoing
        # https://iatistandard.org/en/iati-standard/203/codelists/transactiontype/
        for recipient_transaction_type, funder_transaction_type in [
            ("1", "3"),
            ("11", "2"),
        ]:
            recipient_transactions = recipient_activities_by_id[
                recipient_iati_identifier
            ].findall("transaction")
            recipient_transactions = [
                transaction
                for transaction in recipient_transactions
                if first_or_none(transaction.xpath("transaction-type/@code"))
                == recipient_transaction_type
            ]
            funder_transactions = funder_activities_by_id[
                funder_iati_identifier
            ].findall("transaction")
            funder_transactions = [
                transaction
                for transaction in funder_transactions
                if first_or_none(transaction.xpath("transaction-type/@code"))
                == funder_transaction_type
            ]
            # Assume everything's USD
            funder_values = [
                value.text
                for value in [
                    transaction.find("value") for transaction in funder_transactions
                ]
                if value is not None
            ]

            for recipient_transaction in recipient_transactions:
                recipient_value_element = recipient_transaction.find("value")
                if recipient_value_element is None:
                    continue
                recipient_value = recipient_value_element.text
                if recipient_value is None:
                    continue
                for funder_value in funder_values:
                    funder_value = float(funder_value)
                    recipient_value = float(recipient_value)
                    if (
                        recipient_value >= funder_value - transaction_tolerance
                        and recipient_value <= funder_value + transaction_tolerance
                    ):
                        transaction_match = True
                        if update_xml and ratio >= MIN_RATIO:
                            print(recipient_iati_identifier)
                            provider_org = recipient_transaction.find("provider-org")
                            if provider_org:
                                provider_org.attrib[
                                    "provider-activity-id"
                                ] = funder_iati_identifier
                        break

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


@click.command()
@click.option("--recipient-org-ref", required=True)
@click.option("--funder-org-ref", required=False)
@click.option("--transaction-tolerance", required=False, default=0)
def match_command(recipient_org_ref, funder_org_ref, transaction_tolerance):
    os.makedirs("out", exist_ok=True)
    csvwriter = csv.writer(open("out/matches.csv", "w"))

    with open("out/dataset_by_reporting_org.json") as fp:
        dataset_by_reporting_org = json.load(fp)

    if funder_org_ref is None:
        with open("out/participating_org_ref_dict_by_reporting_org.json") as fp:
            participating_org_ref_dict_by_reporting_org = json.load(fp)
            funder_org_refs = [
                pord["participating_org_ref"]
                for pord in participating_org_ref_dict_by_reporting_org[
                    recipient_org_ref
                ]
            ]
    else:
        funder_org_refs = [funder_org_ref]

    registry = iatikit.data()

    def get_activities(reporting_org_ref, xpath, datasets=None):
        activities = []
        dataset_names = dataset_by_reporting_org.get(reporting_org_ref, [])
        for dataset_name in dataset_names:
            if datasets and dataset_name in datasets:
                dataset = datasets[dataset_name]
            else:
                dataset = registry.datasets.find(name=dataset_name)
            activities += dataset.etree.xpath(xpath)
            if datasets is not None:
                if dataset not in datasets:
                    datasets[dataset_name] = dataset
        return activities

    recipient_datasets = {}

    for funder_org_ref in funder_org_refs:
        print(f"Funder org ref: {funder_org_ref}")
        recipient_activities = get_activities(
            recipient_org_ref,
            f"/iati-activities/iati-activity[reporting-org/@ref='{recipient_org_ref}' and participating-org[@ref='{funder_org_ref}' and @role='1']]",
            recipient_datasets,
        )
        funder_activities = get_activities(
            funder_org_ref,
            f"/iati-activities/iati-activity[reporting-org/@ref='{funder_org_ref}']",
        )
        print(f"{len(recipient_activities)} recipient activities")
        print(f"{len(funder_activities)} funder activities")
        print()
        match(
            recipient_activities,
            funder_activities,
            csvwriter,
            transaction_tolerance=transaction_tolerance,
            update_xml=True,
            funder_org_ref=funder_org_ref,
        )

    for dataset in recipient_datasets.values():
        dataset.etree.write(f"out/{dataset.name}.xml")


if __name__ == "__main__":
    match_command()
