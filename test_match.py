from lxml import etree

import match


def test_match_activities():
    recipient_activities = etree.fromstring(
        """
        <iati-activities>
            <iati-activity>
                <iati-identifier ref="XE-EXAMPLE-AA-01" />
            </iati-activity>
        </iati-activities>
        """
    )
    funder_activities = etree.fromstring(
        """
        <iati-activities>
            <iati-activity>
                <iati-identifier ref="XE-EXAMPLE-BB-01" />
            </iati-activity>
        </iati-activities>
        """
    )
    match.match(recipient_activities, funder_activities)


def test_match_transaction():
    recipient_activities = etree.fromstring(
        """
        <iati-activities>
            <iati-activity>
                <iati-identifier ref="XE-EXAMPLE-AA-01" />
                <transaction>
                    <transaction-type code="1" />
                    <value>1000</value>
                </transaction>
            </iati-activity>
        </iati-activities>
        """
    )
    funder_activities = etree.fromstring(
        """
        <iati-activities>
            <iati-activity>
                <iati-identifier ref="XE-EXAMPLE-BB-01" />
                <transaction>
                    <transaction-type code="3" />
                    <value>1000</value>
                </transaction>
            </iati-activity>
        </iati-activities>
        """
    )
    match.match(recipient_activities, funder_activities)


def test_match_bad_data():
    recipient_activities = etree.fromstring(
        """
        <iati-activities>
            <iati-activity>
                <iati-identifier ref="XE-EXAMPLE-AA-01" />
                <!-- transaction with no sub-elements -->
                <transaction>
                </transaction>
                <!-- transaction with no value -->
                <transaction>
                    <transaction-type code="1" />
                </transaction>
            </iati-activity>
        </iati-activities>
        """
    )
    funder_activities = etree.fromstring(
        """
        <iati-activities>
            <iati-activity>
                <iati-identifier ref="XE-EXAMPLE-BB-01" />
                <!-- transaction with no sub-elements -->
                <transaction>
                </transaction>
                <!-- transaction with no value -->
                <transaction>
                    <transaction-type code="3" />
                </transaction>
            </iati-activity>
        </iati-activities>
        """
    )
    match.match(recipient_activities, funder_activities)
