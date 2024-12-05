import logging
import re
from dataclasses import dataclass
from typing import Dict, List

from concepts_pkg.utils.keyvaluefound import KeyValueFound
from concepts_pkg.utils.string_match import StringFound, StringMatch

from .k2v import CAND_SELECTOR

logger = logging.getLogger("Heuristic")


ALL_KEYS = [
    "ABA CODE",
    "ABA",
    "AMOUNT IN TOTAL",
    "ACCOUNT NUMBER",
    "ACCOUNT",
    "A/C",
    "ACCOUNT NO.",
    "ACCOUNT NU",
    "CUSTOMER ACCOUNT NUMBER",
    "ACCT #",
    "WITHHOLD OR OFFSET TO",
    "BENEFICIARY BANK",
    "BANKER",
    "SWIFT CODE",
    "SWIFT ADDRESS",
    "SWIFT (BIC)",
    "SWIFT/BIC",
    "BIC",
    "SWIFT NO",
    "CORRESPONDENT BANK",
    "INTERMEDIARY BANK",
    "BENIFICIARY",
    "PAYABLE TO",
    "BENEFICIARY",
    "PAY IN",
    "BY WIRE",
    "IBAN",
    "TERMS OF DELIVERY",
    "SORT CODE",
    "SORT",
]


def get_swift_regex(text):
    result = []
    regex_list = list()
    regex_list.append("\\b[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?\\b")
    text = re.sub("[^a-zA-Z0-9]", " ", text)
    for pattern in regex_list:
        matches = re.finditer(pattern, text)
        for match in matches:
            swift_code = match.group(0).strip()
            result.append(swift_code)
    # Modifier code
    # result = [word for word in result if len(word)>5 and len(word)<2]
    # result = [word for word in result if word.upper()== word]
    # result = [word for word in result if word not in ALL_KEYS]
    # result = [word for word in result if not word.lower() in set(word.words())]
    return result


def get_iban_regex(text):
    result = []
    regex_list = list()
    patterns = "\b((?:NO)(?:\s?[0-9]){2}(?:\s?[0-9a-zA-Z]){11})|((?:BE)(?:\s?[0-9]){2}(?:\s?[0-9a-zA-Z]){12})|((?:FO|GL|DK|FI|NL|SD|SI|MK)(?:\s?[0-9]){2}(?:\s?[0-9a-zA-Z]){14,15})|((?:AT|BA|EE|KZ|XK|LT|LU)(?:\s?[0-9]){2}(?:\s?[0-9a-zA-Z]){16})|((?:HR|LV|LI|CH)(?:\s?[0-9]){2}(?:\s?[0-9a-zA-Z]){17})|((?:BH|BG|CR|GE|DE|IE|ME|RS|GB|VA)(?:\s?[0-9]){2}(?:\s?[0-9a-zA-Z]){18})|((?:GI|IL|TL|AE|IQ)(?:\s?[0-9]){2}(?:\s?[0-9a-zA-Z]){19})|((?:CZ|MD|PK|RO|SA|SK|ES|SE|TN|VG)(?:\s?[0-9]){2}(?:\s?[0-9a-zA-Z]){20})|((?:PT|ST|LY|IS|TR)(?:\s?[0-9]){2}(?:\s?[0-9a-zA-Z]){21,22})|((?:FR|GR|IT|MR|MC|SM)(?:\s?[0-9]){2}(?:\s?[0-9a-zA-Z]){23})|((AL|AZ|CY|DO|GT|HU|LB|PL|BY|SV)(?:\s?[0-9]){2}(?:\s?[0-9a-zA-Z]){24})|((?:BR|EG|PS|QA|UA|JO|KW|MU|MT|SC|LC)(?:\s?[0-9]){2}(?:\s?[0-9a-zA-Z]){25,28})\b"
    regex_list.append(patterns)
    for pattern in regex_list:
        y = re.compile(pattern)
        x = y.findall(text)
        for k in list(x):
            for m in list(k):
                if m != "":
                    result.append(m)
    return result


Regex_pattern = {"swift_code": get_swift_regex, "iban_code": get_iban_regex}
# { "Heuristic":{"cand_generator_stgy":["CAND_GEN_USING_KEYALIASES"],"Regex_function":"swift_code"}}
@dataclass
class HEURISTIC_CAND_SELECTOR(CAND_SELECTOR):
    keyword: str
    keyword_config: Dict
    data: Dict
    doc_type: str

    def __post_init__(self):
        self.regex_function = Regex_pattern[
            self.keyword_config.field_config.cand_selector_stgy["Heuristic"][
                "Regex_function"
            ]
        ]
        # self.regex_function = Regex_pattern["swift_code"]

    def select_candidates(
        self, generated_candidates: Dict[str, List[KeyValueFound]]
    ) -> List[Dict]:
        combine_result = []
        if len(generated_candidates) > 1:
            combine_result = {}
            for cand in generated_candidates:
                for key, matched_result in cand.items():
                    combine_result[key] = matched_result
        elif len(generated_candidates) == 1:
            combine_result = generated_candidates[0]

        if combine_result:
            request  = self._get_result(combine_result) 
            return request
        return []

    def _get_result(self, combine_result):
        request = []
        value_ref_lids = []
        # TODO remove duplicate from keyword itself
        for key, match_result_lst in combine_result.items():
            for match_result in match_result_lst:
                temp_contour = match_result.value.contour
                print(match_result.value.match.match_string)
                for lid, line_info in temp_contour["line"].items():
                    if lid in match_result.value.lids:
                        signal = self.regex_function(line_info["text"])
                        if signal:
                            if line_info["line_id"] in value_ref_lids:
                                pass
                            else:
                                value_ref_lids.append(line_info["line_id"])
                                str_match = StringMatch(
                                    -1, 100, line_info["text"]
                                )
                                val_obj = StringFound(
                                    temp_contour, [lid], str_match
                                )
                                request.append(
                                    KeyValueFound(None, val_obj, 100)
                                )
        return request
