import re

tax_reg_pattern_1 = re.compile(
    "[0-9]{9}|"  # United Kingdom (non-eu)
    "[0-9]{14,15}|"  # UAE
    "[0-9]{3}(\s)[0-9]{4}(\s)[0-9]{2}|"
    "(CHE)[-][.0-9]{11}|")

tax_reg_pattern = re.compile(
    "(CHE)[-][.0-9]{11}(\\s)?[A-Z]{3,4}$|"  # Switzerland
    "[0-9]{3}(\s)[0-9]{4}(\s)[0-9]{2}|"
    "[0-9]{3}[-][0-9]{3}[-][0-9]{3}[-][0-9]{3}|"
    "[A-Z]{0,1}[0-9]{8}[A-Z]{0,1}|"   #Spain
    "(BE)(\s)[.0-9]{12}|"   #Belgium
    "[a-zA-Z0-9]{2}[-\s][0-9]{7}[-][0-9]|"  # Singapore3333
    "[a-zA-Z0-9]{2}[a-zA-Z]{5}[0-9]{4}[a-zA-Z0-9]{4}|"   #Singapore
    "[A-Z0-9]{3}[-][0-9]{6}[-][A-Z]|"    #Singapore
    "(NL)(\\s)?[\\d|O]{9}(B)[0-9A-Z]{2}|"  # Netherlands
    "(NL)(\\s){0,1}[.0-9]{11}[.A-Z0-9]{3,5}|"      #Netherlands
    "(KR)(\s)?[0-9]{3}[-][0-9]{2}[-][0-9]{5}|"     # Korea(*not sure if this is the only format)
    "[0-9]{8}[A-Z]{2}[0-9]{1}[A-Z]{5}[0-9]{1}[A-Z]{1}|"  # SGS China
    "[0-9]{8}[A-Z]{1}[0-9]{8}[A-Z]{1}|"  #SGS China
    "[0-9]{2}[-][0-9]{7}|"  # United States
    "(GB)(\s)?[0-9]{3}(\s)?[0-9]{4}(\s)?[0-9]{2}|"  #Valid UK VAT
    "[A-Z]{2}(\s)[0-9]{7}[A-Z]{1}|" "(CH)[0-9]{6}|"
    "((CY)(\\s)?[\\d|O]{8}L|"
    "(CZ)(\\s)?[\\d|O]{8,10}|"
    "(DE)(\\s)?[\\d|O]{9}|"
    "(SE)(\\s)?[\\d|O]{12}|"
    "(DK)(\\s)?[\\d|O]{8}|"
    "(EE)(\\s)?[\\d|O]{9}|"
    "(EL|GR)(\\s)?[\\d|O]{9}|"
    "(ES)(\\s)?[0-9A-Z][\\d]{7}[0-9A-Z]|"
    "(FI)(\\s)?[\\d|O]{8}|"
    "(FR)(\\s)?[0-9A-Z]{2}[\\d|O]{9}|"
    "(GB)(\\s)?([\\d|O]{9}([\\d|O]{3})?|"
    "(HU)(\\s)?[\\d|O]{8}|"
    "(IE)(\\s)?[\\d|O]S[\\d|O]{5}L|"
    "(IT)(\\s)?[\\d|O]{11}|"
    "(LT)(\\s)?([\\d|O]{9}|"
    "(LU)(\\s)?[\\d|O]{8}|"
    "(BE)(\\s)?(0|O|1|l)?[\\d]{9}|"
    "(NL)(\\s)?[\\d]{9}(B[\\d|O]{2})?|"
    "(AT)(\\s)?U[\\d|O]{8}|"
    "(BG)(\\s)?[\\d|O]{9,10}|"
    "(LV)(\\s)?[\\d|O]{11}|"
    "(MT)(\\s)?[\\d|O]{8}|"
    "(PL)(\\s)?[\\d|O]{10}|"
    "(PT)(\\s)?[\\d|O]{9}|"
    "(RO)(\\s)?[\\d|O]{2,10}|"
    "(SE)(\\s)?[\\d|O]{12}|"
    "(SI)(\\s)?[\\d|O]{8}|"
    "(SK)(\\s)?[\\d|O]{10})))"
)