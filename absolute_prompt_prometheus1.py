#!/usr/bin/env python

from prometheus_eval.vllm import VLLM
from prometheus_eval import PrometheusEval
from prometheus_eval.prompts import ABSOLUTE_PROMPT, SCORE_RUBRIC_TEMPLATE

from pathlib import Path
from typing import List
import argparse
import llm_eval_utils as leu

"""
This code instructs Prometheus to evaluate an attempt on the Alternate Uses Test.

The code assumes that soe version of `prometheus-eval` is running locally.

The score varies between 1-5, with 5 being the highest mark, & uses the absolute score - i.e. not relative bwteen two or more responses.
No 'ground-truth' statement  or 'corretc answer' is given, since the task is inherently creative.

The rubric is given in the `llm_eval_utils` module.
"""

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--response", required=True)
    parser.add_argument("-obj", required=True)
    parser.add_argument('-v', '--verbose', action='store_true', default=False)

    args = parser.parse_args()

    r = Path(args.response)

    if not r.exists():
        print(f"Error: cannot find file {r}")
        exit(-1)

    # build our score rubric
    score_rubric = leu.build_rubric(obj=args.obj)

     # this is how we match numbered (some Roman numeral'd!) lists of responses from the LLMs
     # probably unnecessary, but might be useful for some LLM outputs, so included for completeness
    pattern = r"^.*\.\s(.*)$"

    llm_response = leu.raw_extract_responses(filename=r)

    if args.verbose:
        print(f"LLM response:\n\n{llm_response}")

    # AUT (original) prompt
    instruction = leu.build_orig_instruction(obj=args.obj)

    # set up our LLM ...
    # (very) standard role
    role = "You are a helpful, smart, kind, creative, original and efficient AI assistant. You always fulfill the user's requests to the best of your ability."

    # now we build our prompt ...
    prompt = leu.build_absolute_prompt(instruction=instruction, response=llm_response, rubric=score_rubric)

    # ... & present it to `prometheus`
    prometheus_response = leu.send_request(role=role, message=prompt, temperature=0.01)
    bot_response = prometheus_response.get("choices")[0].get("message").get("content") if prometheus_response.get("choices") else "Sorry, I couldn't get a response."
    print("Bot:", bot_response)

    res = leu.match_bot_response(bot_response=bot_response) 
    print(f"Evaluation: {res}")

if __name__ == "__main__":
    main()