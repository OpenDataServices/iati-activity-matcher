import csv
import os

from fuzzywuzzy import fuzz


def match(recipient_activities, funder_activities, recipient_tree=None):
    def activity_lookup(activities):
        return {
            activity.xpath("iati-identifier")[0].text: activity
            for activity in activities
        }

    recipient_activity_lookup = activity_lookup(recipient_activities)
    funder_activity_lookup = activity_lookup(funder_activities)

    def titles(activities):
        return {
            activity.xpath("iati-identifier")[0].text: "\n".join(
                activity.xpath("title/narrative/text()")
            )
            for activity in activities
        }

    recipient_titles = titles(recipient_activities)
    funder_titles = titles(funder_activities)

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
            participating_org = recipient_activity_lookup[
                recipient_iati_identifier
            ].find("participating-org[@ref='DAC-1601']")
            participating_org.attrib["activity-id"] = funder_iati_identifier

        recipient_transactions = recipient_activity_lookup[
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

        funder_transactions = funder_activity_lookup[funder_iati_identifier].findall(
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
