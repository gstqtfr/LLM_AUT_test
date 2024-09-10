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
    obj = 'chair'
    # this just assumes we have these files in the current directory! but this is just a quick test ...
    r1 = Path('MetaLlama3Insruct_Chair_1.txt')
    r2 = Path('QwenChat_Chair_1.txt')

    # this is how we match numbered (some Roman numeral'd!) lists of responses from the LLMs
    pattern = r"^.*\.\s(.*)$"

    response1_list = leu.extract_responses(filename=r1, expr=pattern)
    response2_list = leu.extract_responses(filename=r2, expr=pattern)
    
    # AUT (original) prompt
    instruction = leu.build_orig_instruction(obj=obj)
    # grab a single response from each file
    response_A = response1_list[0]
    response_B = response2_list[0]

    # basic ruric, we can always modify if we need to ...
    rubric = f"Is the model responding with creative, fluent, original, and flexibile alternate uses of the given object, {obj}?"

    prompt = leu.build_relative_prompt(
        instruction=instruction,
        response_A=response_A,
        response_B=response_B,
        rubric=rubric)

    # (very) standard role
    role = "You are a helpful, smart, kind, creative, original and efficient AI assistant. You always fulfill the user's requests to the best of your ability."

    response = leu.send_request(role, prompt)
    bot_response = response.get("choices")[0].get("message").get("content") if response.get("choices") else "Sorry, I couldn't get a response."
    print("Bot:", bot_response)


if __name__ == "__main__":
    main()

