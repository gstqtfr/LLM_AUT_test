#!/usr/bin/env python

from pathlib import Path
import typing
import argparse
import llm_eval_utils as leu

"""
Program to feed a prompt describing the alternate uses test (AUT) to an LLM, get the response, and write it out to a file,
"""

def main() -> None:

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", required=True)
    parser.add_argument("-obj", required=True)
    parser.add_argument("-v", "--verbose")
    parser.add_argument("-d", "--directory")

    args = parser.parse_args()

    output_path = ''
    output_dir = ''

    role = "You are a helpful, smart, kind, creative, original and efficient AI assistant. You always fulfill the user's requests to the best of your ability."

    # if the directory is spec'd, we need to create a path out of it 
    if args.directory:
        if not Path(args.directory).exists():
            print(f"Error: cannot find directory {args.directory}")
            exit(-1)
        else:
            output_dir = Path(args.directory) 
            if args.verbose:
                print(f"Directory: {output_dir}")
            output_path = output_dir / args.file
    else:
        print(f"Directory not specified, local directory assumed")
        output_path = Path(args.file)

    if args.verbose:
        print(f"Output path: {output_path}")

    with open(output_path, 'w') as f:
        # set up our AUT prompt 
        prompt = leu.set_LLM_prompt(args.obj)
        response = leu.send_request(role=role, message=prompt, temperature=1.0)
        bot_response = response.get("choices")[0].get("message").get("content") if response.get("choices") else "Sorry, I couldn't get a response."
        if args.verbose:
            print(f"Prompt: {prompt}") 
            print("Bot:", bot_response)
        # then we save this to a local file 
        f.write(bot_response)


if __name__ == "__main__":
    main()

