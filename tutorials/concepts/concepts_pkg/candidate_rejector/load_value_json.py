from ..utils.io import load_value_json

loc_rejection = load_value_json("loc_rejection")
org_rejection = load_value_json("org_rejection")


REF_VALUES = {"loc_rejection": loc_rejection, "org_rejection": org_rejection}
