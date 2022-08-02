import csv
import io
import textwrap

import pytest
from lxml import etree

import match


@pytest.mark.parametrize(
    "fixture_name,recipient_xml_in,funder_xml_in,expected_match_csv,recipient_xml_out,funder_org_ref",
    [
        (
            "No matches if there's no titles",
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
            "",
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
            "Match activities without transactions",
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
                    <iati-activity>
                        <iati-identifier>XE-EXAMPLE-AA-03</iati-identifier>
                        <title>
                            <narrative>Some other title</narrative>
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
                            <narrative>Some title</narrative>
                        </title>
                    </iati-activity>
                    <iati-activity>
                        <iati-identifier>XE-EXAMPLE-BB-03</iati-identifier>
                        <title>
                            <narrative>A title</narrative>
                        </title>
                    </iati-activity>
                </iati-activities>
            """,
            """
                100,XE-EXAMPLE-AA-02,XE-EXAMPLE-BB-03,A title,A title,False
                77,XE-EXAMPLE-AA-03,XE-EXAMPLE-BB-02,Some other title,Some title,False
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
                        <participating-org ref="XE-EXAMPLE-BB" activity-id="XE-EXAMPLE-BB-03"/>
                    </iati-activity>
                    <iati-activity>
                        <iati-identifier>XE-EXAMPLE-AA-03</iati-identifier>
                        <title>
                            <narrative>Some other title</narrative>
                        </title>
                        <participating-org ref="XE-EXAMPLE-BB" activity-id="XE-EXAMPLE-BB-02"/>
                    </iati-activity>
                </iati-activities>
            """,
            "XE-EXAMPLE-BB",
        ),
        (
            "Match activities with transactions",
            """
                <iati-activities>
                    <iati-activity>
                        <iati-identifier>XE-EXAMPLE-AA-01</iati-identifier>
                        <title>
                            <narrative>A title</narrative>
                        </title>
                        <participating-org ref="XE-EXAMPLE-BB"/>
                        <transaction>
                            <transaction-type code="1"/>
                            <value>1000</value>
                        </transaction>
                    </iati-activity>
                </iati-activities>
            """,
            """
                <iati-activities>
                    <iati-activity>
                        <iati-identifier>XE-EXAMPLE-BB-01</iati-identifier>
                        <title>
                            <narrative>A title</narrative>
                        </title>
                        <transaction>
                            <transaction-type code="3"/>
                            <value>1000</value>
                        </transaction>
                    </iati-activity>
                </iati-activities>
            """,
            """
                100,XE-EXAMPLE-AA-01,XE-EXAMPLE-BB-01,A title,A title,True
            """,
            """
                <iati-activities>
                    <iati-activity>
                        <iati-identifier>XE-EXAMPLE-AA-01</iati-identifier>
                        <title>
                            <narrative>A title</narrative>
                        </title>
                        <participating-org ref="XE-EXAMPLE-BB" activity-id="XE-EXAMPLE-BB-01"/>
                        <transaction>
                            <transaction-type code="1"/>
                            <value>1000</value>
                        </transaction>
                    </iati-activity>
                </iati-activities>
            """,
            "XE-EXAMPLE-BB",
        ),
        (
            "Test bad data",
            """
                <iati-activities>
                    <iati-activity>
                        <iati-identifier>XE-EXAMPLE-AA-01</iati-identifier>
                        <title>
                            <narrative>A title</narrative>
                        </title>
                        <participating-org ref="XE-EXAMPLE-BB"/>
                        <!-- transaction with no sub-elements -->
                        <transaction>
                        </transaction>
                        <!-- transaction with no value -->
                        <transaction>
                            <transaction-type code="1"/>
                        </transaction>
                    </iati-activity>
                </iati-activities>
            """,
            """
                <iati-activities>
                    <iati-activity>
                        <iati-identifier>XE-EXAMPLE-BB-01</iati-identifier>
                        <title>
                            <narrative>A title</narrative>
                        </title>
                        <!-- transaction with no sub-elements -->
                        <transaction>
                        </transaction>
                        <!-- transaction with no value -->
                        <transaction>
                            <transaction-type code="3"/>
                        </transaction>
                        <!-- transaction with no provider-org -->
                        <transaction>
                            <transaction-type code="3"/>
                            <value>1000</value>
                        </transaction>
                    </iati-activity>
                </iati-activities>
            """,
            """
                100,XE-EXAMPLE-AA-01,XE-EXAMPLE-BB-01,A title,A title,False
            """,
            None,
            None,
        ),
        (
            "Test bad data 2",
            """
                <iati-activities>
                    <iati-activity>
                        <iati-identifier>XE-EXAMPLE-AA-01</iati-identifier>
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
                    </iati-activity>
                </iati-activities>
            """,
            "",
            None,
            None,
        ),
    ],
)
@pytest.mark.parametrize("update_xml", [False, True])
def test_match_activities(
    fixture_name,
    recipient_xml_in,
    funder_xml_in,
    expected_match_csv,
    recipient_xml_out,
    update_xml,
    funder_org_ref,
):
    recipient_activities = etree.fromstring(recipient_xml_in)
    funder_activities = etree.fromstring(funder_xml_in)
    csv_output = io.StringIO()
    csvwriter = csv.writer(csv_output)

    match.match(
        recipient_activities,
        funder_activities,
        csvwriter,
        update_xml=update_xml,
        funder_org_ref=funder_org_ref,
    )

    assert csv_output.getvalue().replace("\r\n", "\n").strip(" \n") == textwrap.dedent(
        expected_match_csv
    ).strip(" \n")

    if not update_xml or not recipient_xml_out:
        recipient_xml_out = recipient_xml_in
    funder_xml_out = funder_xml_in
    assert etree.tostring(recipient_activities).decode("utf-8").strip(
        " \n"
    ) == recipient_xml_out.strip(" \n")
    assert etree.tostring(funder_activities).decode("utf-8").strip(
        " \n"
    ) == funder_xml_out.strip(" \n")
