#!/usr/bin/env python

from prometheus_eval.vllm import VLLM
from prometheus_eval import PrometheusEval
from prometheus_eval.prompts import ABSOLUTE_PROMPT, SCORE_RUBRIC_TEMPLATE

from pathlib import Path
import typing
from typing import List
import requests
import json
import argparse
import re
import llm_eval_utils as leu

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-r1", "--response1", required=True)
    parser.add_argument("-r2", "--response2", required=True)
    parser.add_argument("-obj", required=True)
    parser.add_argument('--verbose', action='store_false', default=False)

    args = parser.parse_args()

    r1 = Path(args.response1)
    r2 = Path(args.response2)

    if not r1.exists():
        print(f"Error: cannot find file {r1}")
        exit(-1)

    if not r2.exists():
        print(f"Error: cannot find file {r2}")
        exit(-1)

     # this is how we match numbered (some Roman numeral'd!) lists of responses from the LLMs
    pattern = r"^.*\.\s(.*)$"

    response1_list = leu.extract_responses(filename=r1, expr=pattern)
    response2_list = leu.extract_responses(filename=r2, expr=pattern)
    
    # AUT (original) prompt
    instruction = leu.build_orig_instruction(obj=args.obj)

    # do we compare all of them? or one-by-one, side-by-side comparisons? that seems like a better proposal, we 
    # get an idea of the mean performance of each LLM/human

    # if there are fewer response in one set of responses than the other, we truncate the longer one
    # maybe not an ideal soution, but it's one way of doing this!
    
    if len(response1_list) < len(response2_list):
        response2_list = response2_list[:len(response1_list)]
    elif len(response2_list) < len(response1_list):
        response1_list = response1_list[:len(response2_list)]
    
    # set up our LLM ...
    # (very) standard role
    role = "You are a helpful, smart, kind, creative, original and efficient AI assistant. You always fulfill the user's requests to the best of your ability."

    # basic rubric, we can always modify if we need to ...
    rubric = f"Is the model responding with creative, fluent, original, and flexibile alternate uses of the given object, {args.obj}?"

    a_pref = b_pref = 0

    for idx in range(len(response1_list)):
        # grab a single response from each file
        response_A = response1_list[idx]
        response_B = response2_list[idx]

        # build our Prometheus prompt 
        prompt = leu.build_relative_prompt(
            instruction=instruction,
            response_A=response_A,
            response_B=response_B,
            rubric=rubric)
        
        response = leu.send_request(role, prompt)
        bot_response = response.get("choices")[0].get("message").get("content") if response.get("choices") else "Sorry, I couldn't get a response."
        if args.verbose:
            print("Bot:", bot_response)

        res = leu.match_bot_response(bot_response=bot_response) 

        if res == 'A':
            a_pref += 1
        elif res == 'B':
            b_pref += 1
        else:
            print(f"Neither A nor B response detected")

    print(f"A: {a_pref}")
    print(f"B: {b_pref}")


if __name__ == "__main__":
    main()