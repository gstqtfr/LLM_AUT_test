#!/usr/bin/env python

import os
import subprocess
from pathlib import Path
from typing import List
import argparse

from pathlib import Path
from collections import OrderedDict
import configparser 
from time import sleep
import llm_eval_utils as leu

def start_LLM_process(model: str, objects: List, d: Path, iteration: int = 1, llm_cmd: str='prompt_LLM_AUT.py') -> None:
    for obj in objects:
        cmd=f"python {llm_cmd} -d {output_dir} -f {model}-{obj}{iteration}.txt -obj {obj}"
        print(f"About to execute {cmd}")
        os.popen(cmd).read()

def load_model(model: str) -> None:
    # we unload by default
    print(os.popen('lms unload --all').read())
    print(os.popen(f'lms load {model}').read() )

def main() -> None:
    parser = argparse.ArgumentParser()
    #parser.add_argument("-f", "--file", required=True)
    #parser.add_argument("-obj", required=True)
    parser.add_argument("-v", "--verbose")
    parser.add_argument("-s", "--start", type=int, required=True) 
    parser.add_argument("-n", "--number", type=int, required=True)
    parser.add_argument("-d", "--directory", required=True)
    parser.add_argument("-c", "--config", required=True)

    args = parser.parse_args()
    output_dir = Path(args.directory)

    if not output_dir.exists():
        print(f"Cannot find {output_dir}. Does this directory exist, and is it accessible?")
        exit(0)

    cfg = Path(args.cfg)

    if not cfg.exists():
        print(f"Cannot find config file {cfg}.")
        exit(0)

    # let's get our configuration - these are the models & objects we're using
    config = configparser.ConfigParser()
    config.read(cfg)

    llms = config._sections['llm']
    objects = config._sections['objects']['objs'].split(', ')

    for iteration in range(args.start, args.start+args.number):
        for name, model in OrderedDict(reversed(list(llms.items()))).items():
            print(f"Loading {name} -> {model}")
            load_model(model)
            print(os.popen("lms status").read())
            print(f"Load {name} -> {model}")
            print(f"Starting process ...")
            start_LLM_process(model=name, objects=objects, d=output_dir, iteration=iteration)
            print(f"Finished process")
            sleep(5)

if __name__ == "__main__":
    main()