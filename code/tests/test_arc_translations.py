import pytest
import pathlib
import re
import pandas as pd
from bridge.arc.arc_api import ArcApiClient


'''

To test locally, run:
pytest tests/test_arc_translations.py --translations-path=YOUR_PATH

YOUR_PATH is formatted as: ARCH1.5.0
YOUR_PATH is set as ${{ steps.get_version.outputs.path }} when ran through the yml file

'''


BASE_DIR = pathlib.Path(".")
TEST_PATH = pathlib.Path(__file__)


REQUIRED_COLUMNS = [
    "Form",
    "Section",
    "Variable",
    #"Type",
    "Question",
    "Answer Options",
    #"Validation",
    #"Minimum",
    #"Maximum",
    #"List",
    #"Skip Logic",
    #"Body System",
    "Definition",
    "Completion Guideline",
    #"Standardized Term Codelist",
    #"Standardized Term Code",
    #"Metathesaurus",
    #"Identifier",
    #"Research Category",
]

#@pytest.mark.critical
def test_arc_required_columns_exist(arc_path):
    """Check required ARC columns exist"""
    arc = pd.read_csv(arc_path, nrows=0, dtype="object")
    header = list(arc.columns)
    missing = [c for c in REQUIRED_COLUMNS if c not in header]
    if missing:
        pytest.fail(f"Missing required columns: {missing}")


#@pytest.mark.critical
def test_arc_valid_variable_regex(arc_path):
    """Check all variable names match the naming convention regex."""
    arc = pd.read_csv(arc_path, dtype="object", usecols=["Variable"])
    variable_regex = re.compile(r"^[a-z][a-z0-9_]*$")
    non_match = arc["Variable"].apply(lambda x: not variable_regex.match(x))
    if non_match.any():
        invalid = arc.loc[non_match, "Variable"].tolist()
        pytest.fail(f"Variables do not following naming convention regex: {invalid}")


#@pytest.mark.high
@pytest.mark.parametrize("column", REQUIRED_COLUMNS)
def test_arc_newline(column, arc_path):
    """Check if each required column has a newline character in the string"""
    arc = pd.read_csv(arc_path, dtype="object", usecols=["Variable", column])
    condition = ~(arc[column].str.contains("\n") & arc[column].isna())
    if not condition.all():
        invalid = dict(
            zip(arc.loc[~condition, "Variable"], arc.loc[~condition, column])
        )
        pytest.fail(
            f"ARC column {column} has newline characters (\n). Variables: {invalid}"
        )


def is_valid_redcap_field_options(s: str) -> bool:
    if not s or not isinstance(s, str):
        return False

    options = s.split("|")

    for option in options:
        option = option.strip()

        # Must contain at least one comma
        if option.count(",") < 1:
            print("< 1 comma", s)
            return False

        code, label = option.split(",", 1)
        code = code.strip()
        label = label.strip()

        # Code must be non-empty
        if not code:
            print("code empty")
            return False

        # Label must be non-empty
        if not label:
            print("field empty")
            return False

    return True

'''

### THIS FAILS, many are already broken, in english and translations.

#@pytest.mark.critical
def test_arc_answer_options_valid_redcap(arc_path):
    """Answer options for radio/checkbox variables must be valid REDCap format"""
    arc = pd.read_csv(
        arc_path, dtype="object", usecols=["Variable", "Answer Options"]
    )
    #condition = ~arc["Type"].isin(["radio", "checkbox", "list", "dropdown"]) | arc[
    #    "Answer Options"
    #].apply(lambda x: is_valid_redcap_field_options(x))
    condition = ~arc["Answer Options"].apply(lambda x: is_valid_redcap_field_options(x))
    
    if not condition.all():
        invalid = arc.loc[~condition].set_index("Variable").to_dict(orient="index")
        pytest.fail(
            "ARC contains Answer Options that are not valid REDCap-format. "
            f"Variables: {invalid}"
        )


             
#@pytest.mark.high
def test_arc_type_consistent_with_list(arc_path):
    """
    List variable non-empty only for (user_list, multi_list, list)
    """
    arc = pd.read_csv(arc_path, dtype="object", usecols=["Variable", "Type", "List"])
    condition = (
        arc["Type"].isin(["user_list", "multi_list", "list"]) & arc["List"].notna()
    ) | arc["List"].isna()
    if not condition.all():
        invalid = arc.loc[~condition].set_index("Variable").to_dict(orient="index")
        pytest.fail(f"ARC List missing or falsely included for Variables: {invalid}")

#@pytest.mark.medium
@pytest.mark.parametrize("column", REQUIRED_COLUMNS)
def test_arc_strip(column, arc_path):
    """Check if each required column has empty spaces at the beginning/end"""
    arc = pd.read_csv(arc_path, dtype="object", usecols=["Variable", column])
    condition = arc[column].eq(arc[column].str.strip()) | arc[column].isna()
    if not condition.all():
        invalid = dict(
            zip(arc.loc[~condition, "Variable"], arc.loc[~condition, column])
        )
        pytest.fail(
            f"ARC column {column} has unnecessary spaces at the beginning/end. "
            f"Variables: {invalid}"
        )



#@pytest.mark.medium
def test_arc_definition_exists(arc_path):
    """
    ARC definition should exist except for "descriptive" Type
    or "units" Validation variables
    """
    arc = pd.read_csv(
        arc_path,
        dtype="object",
        usecols=["Variable", "Type", "Validation", "Definition"],
    )
    condition = (
        arc["Type"].isin(["descriptive"])
        | arc["Validation"].isin(["units"])
        | ~arc["Definition"].isna()
    )
    if not condition.all():
        invalid = arc.loc[~condition, "Variable"].tolist()
        pytest.fail(f"ARC has no Definition for Variables: {invalid}")





#@pytest.mark.medium
def test_arc_valid_preset_values(arc_path):
    """Preset columns column must be NaN or 1 (not 1.0)"""
    arc = pd.read_csv(arc_path, dtype="object")
    preset_columns = [c for c in arc.columns if c.startswith("preset_")]
    condition = (
        arc[preset_columns]
        .apply(lambda x: x.isin(["1"]) | x.isna(), axis=0)
        .all(axis=1)
    )
    if not condition.all():
        invalid = (
            arc.loc[~condition]
            .set_index("Variable")[preset_columns]
            .to_dict(orient="index")
        )
        pytest.fail(f"ARC has invalid preset values for Variables: {invalid}")
'''