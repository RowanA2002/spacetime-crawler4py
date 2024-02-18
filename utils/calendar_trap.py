from typing import Set
import re

def calendar_trap_check(base_url: str, urls: Set) -> int:
    number_pat = re.compile("[^a-zA-Z|\W]+([0-9]+)*.?")
    base_stripped = re.sub(number_pat, "", base_url)
    calender_matches = 0
    for parent in urls:
        parent_stripped = re.sub(number_pat, "", parent)
        if parent_stripped == base_stripped:
            calender_matches += 1
    return calender_matches
    





