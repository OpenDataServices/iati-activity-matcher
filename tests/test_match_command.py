import os
import textwrap

import pytest

import extract_participating_orgs
import match


@pytest.mark.parametrize(
    "args",
    [
        ["--recipient-org-ref", "XE-EXAMPLE-AA"],
        ["--recipient-org-ref", "XE-EXAMPLE-AA", "--funder-org-ref", "XE-EXAMPLE-BB"],
        ["--recipient-org-ref", "XE-EXAMPLE-AA", "--transaction-tolerance", "100"],
    ],
)
def test_match_command(chdir_fixtures, cli_runner, args):
    extract_participating_orgs.extract_participating_orgs()
    result = cli_runner.invoke(match.match_command, args)
    assert result.exit_code == 0
    assert (
        open("out/matches.csv").read().strip("\n")
        == textwrap.dedent(
            """
                100,XE-EXAMPLE-AA-02,XE-EXAMPLE-BB-03,A title,A title,False
                77,XE-EXAMPLE-AA-03,XE-EXAMPLE-BB-02,Some other title,Some title,False
                100,XE-EXAMPLE-AA-04,XE-EXAMPLE-BB-04,An activity with transaction,An activity with transaction,True
            """
        ).strip("\n")
    )
    assert open(os.path.join("out", "recipient-activities.xml")).read().strip(
        "\n"
    ) == open(os.path.join("out_expected", "recipient-activities.xml")).read().strip(
        "\n"
    )
