#!/usr/bin/env python

import numpy as np
import pandas as pd
from pathlib import Path
import argparse
import llm_eval_utils as leu
from typing import List, Tuple, Dict


# lots of little teeny functions to tidy stuff up a bit

def construct_args_per_obj(objs: str)  -> Tuple[Dict, Dict]:
    rubrics = {}
    instructions = {}
    for o in objs:
        rubrics[o] = leu.build_rubric(obj=o)
        instructions[o] = leu.build_orig_instruction(obj=o)
    return rubrics, instructions

def build_response_list(response: List[str]) -> str:
    return '\n'.join(response)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--response", required=True)
    parser.add_argument("-id", required=True, type=int)
    parser.add_argument('--objs', nargs='+', required=True)
    parser.add_argument('-v', '--verbose', action='store_true', default=False)

    args = parser.parse_args()

    r = Path(args.response)

    if not r.exists():
        print(f"Error: cannot find file {r}")
        exit(-1)

    # slap the data into a dataframe
    df = pd.read_csv(r)

    user_responses = dict( (k, []) for k in args.objs)

    for o in args.objs:
        user_responses[o] = list(df[(df['object'] == o) & (df['user_id'] == args.id)]['response'])

    #print(f"Instruction: {build_instruction(args.objs[0])}")

    print(f"Recv'd {user_responses}")
    
    print(f"response list for user {args.id} for object '{args.objs[0]}': {build_response_list(user_responses[args.objs[0]])}")
    
    # set up our LLM ...
    # (very) standard role
    role = "You are a helpful, smart, kind, creative, original and efficient AI assistant. You always fulfill the user's requests to the best of your ability."
    
    
    # score_rubric = leu.build_rubric(obj=obj)


    rubric, instruction = construct_args_per_obj(objs=args.objs)
    print(f"Instructions: {instruction}")
    # build our score rubric
    print(f"Rubrics: {rubric}")
    
    # now we build our prompts ...

    

    # prompt = leu.build_absolute_prompt(instruction=instruction, response=response, rubric=rubric)


    

if __name__ == "__main__":
    main()