import os

import extract_participating_orgs


def test_extract_participating_orgs(chdir_fixtures):
    extract_participating_orgs.extract_participating_orgs()
    for fname in [
        "activity_count_by_reporting_org.json",
        "dataset_by_reporting_org.json",
        "participating_org_details_by_orgs.json",
        "participating_org_ref_dict_by_reporting_org.json",
    ]:
        assert open(os.path.join("out", fname)).read().strip("\n") == open(
            os.path.join("out_expected", fname)
        ).read().strip("\n")
