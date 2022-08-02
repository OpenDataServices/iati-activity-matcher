import extract_participating_orgs
import match


def test_match_command(chdir_fixtures, cli_runner):
    extract_participating_orgs.extract_participating_orgs()
    cli_runner.invoke(match.match_command, [])
