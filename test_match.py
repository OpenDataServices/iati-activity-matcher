import pytest
from lxml import etree

import match


@pytest.mark.parametrize(
    "recipient_xml_in,funder_xml_in,recipient_xml_out,funder_org_ref",
    [
        (
            """
                <iati-activities>
                    <iati-activity>
                        <iati-identifier>XE-EXAMPLE-AA-01</iati-identifier>
                    </iati-activity>
                </iati-activities>
            """,
            """
                <iati-activities>
                    <iati-activity>
                        <iati-identifier>XE-EXAMPLE-BB-01</iati-identifier>
                    </iati-activity>
                </iati-activities>
            """,
            """
                <iati-activities>
                    <iati-activity>
                        <iati-identifier>XE-EXAMPLE-AA-01</iati-identifier>
                    </iati-activity>
                </iati-activities>
            """,
            None,
        ),
        (
            """
                <iati-activities>
                    <iati-activity>
                        <iati-identifier>XE-EXAMPLE-AA-01</iati-identifier>
                        <participating-org ref="XE-EXAMPLE-BB"/>
                    </iati-activity>
                    <iati-activity>
                        <iati-identifier>XE-EXAMPLE-AA-02</iati-identifier>
                        <title>
                            <narrative>A title</narrative>
                        </title>
                        <participating-org ref="XE-EXAMPLE-BB"/>
                    </iati-activity>
                </iati-activities>
            """,
            """
                <iati-activities>
                    <iati-activity>
                        <iati-identifier>XE-EXAMPLE-BB-01</iati-identifier>
                    </iati-activity>
                    <iati-activity>
                        <iati-identifier>XE-EXAMPLE-BB-02</iati-identifier>
                        <title>
                            <narrative>A title</narrative>
                        </title>
                    </iati-activity>
                </iati-activities>
            """,
            """
                <iati-activities>
                    <iati-activity>
                        <iati-identifier>XE-EXAMPLE-AA-01</iati-identifier>
                        <participating-org ref="XE-EXAMPLE-BB"/>
                    </iati-activity>
                    <iati-activity>
                        <iati-identifier>XE-EXAMPLE-AA-02</iati-identifier>
                        <title>
                            <narrative>A title</narrative>
                        </title>
                        <participating-org ref="XE-EXAMPLE-BB" activity-id="XE-EXAMPLE-BB-02"/>
                    </iati-activity>
                </iati-activities>
            """,
            "XE-EXAMPLE-BB",
        ),
    ],
)
@pytest.mark.parametrize("update_xml", [False, True])
def test_match_activities(
    recipient_xml_in, funder_xml_in, recipient_xml_out, update_xml, funder_org_ref
):
    recipient_activities = etree.fromstring(recipient_xml_in)
    funder_activities = etree.fromstring(funder_xml_in)
    match.match(
        recipient_activities,
        funder_activities,
        update_xml=update_xml,
        funder_org_ref=funder_org_ref,
    )
    if not update_xml:
        recipient_xml_out = recipient_xml_in
    funder_xml_out = funder_xml_in
    assert etree.tostring(recipient_activities).decode("utf-8").strip(
        " \n"
    ) == recipient_xml_out.strip(" \n")
    assert etree.tostring(funder_activities).decode("utf-8").strip(
        " \n"
    ) == funder_xml_out.strip(" \n")


def test_match_transaction():
    recipient_activities = etree.fromstring(
        """
        <iati-activities>
            <iati-activity>
                <iati-identifier ref="XE-EXAMPLE-AA-01"/>
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
                <iati-identifier ref="XE-EXAMPLE-BB-01"/>
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
                <iati-identifier ref="XE-EXAMPLE-AA-01"/>
                <!-- transaction with no sub-elements -->
                <transaction>
                </transaction>
                <!-- transaction with no value -->
                <transaction>
                    <transaction-type code="1"/>
                </transaction>
            </iati-activity>
        </iati-activities>
        """
    )
    funder_activities = etree.fromstring(
        """
        <iati-activities>
            <iati-activity>
                <iati-identifier ref="XE-EXAMPLE-BB-01"/>
                <!-- transaction with no sub-elements -->
                <transaction>
                </transaction>
                <!-- transaction with no value -->
                <transaction>
                    <transaction-type code="3"/>
                </transaction>
            </iati-activity>
        </iati-activities>
        """
    )
    match.match(recipient_activities, funder_activities)
