import re
from random import shuffle
from typing import List
from pathlib import Path

# JKK: a couple of utility functions to process the LLM output files
# JKK: & sample them 

def repeated_sample_without_replacement(my_list: List, n: int) -> List[List]:
    """Create a sample, without replacement, of the given list, of sample size n."""
    shuffle(my_list)
    return [my_list[i::n] for i in range(n)]

def extract_model_responses(f: str) -> List[str]:
    """Process the output of various LLMs. We want to get of any numbers (or Roman numerals!) at the
        start of the model's output, since we might want to sample it into subsets.
        
        N.B.: only the most common expressions are matched: this is not comprehensive, so check the output."""
    # expression to match a line which begins with a number, a fullstop, and a space, like:
    # 11. Use a book to prop up your head while napping
    expr1 = r"^\d+\.\s(.*)"
    # expression to match a number followed by a bracket at the start of a line
    expr2 = r"^\d+\)\s(.*)"
    contents = []
    with f.open(mode="r", encoding="utf-8") as md_file:
        content = md_file.read()
        for line in content.splitlines():
            # match an empty line - we don't want these
            if len(line.strip()) == 0:
                continue
            # match a line with a number at the start
            m = re.search(expr1, line)
            if m:
                contents.append(m.group(1))
                continue
            m = re.search(expr2, line)
            if m:
                contents.append(m.group(1))
                continue
            # default behaviour: we add the line anyway
            contents.append(line)

    return contents

