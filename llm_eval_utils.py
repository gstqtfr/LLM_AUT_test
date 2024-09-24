import requests
import typing
from typing import List
import re
import json
from prometheus_eval.prompts import ABSOLUTE_PROMPT, SCORE_RUBRIC_TEMPLATE

def raw_extract_responses(filename: str) -> List[str]:
    """Opens and iterates through the given file, nor processing, so raw response, & returns them in a list."""
    responses = []
    f = open(file=filename, mode='r')
    responses = f.read()
    return responses

def extract_responses(filename: str, expr: str) -> List[str]:
    """Opens and iterates through the given file, uses the given regular experssion to match responses, returns them in a list."""
    responses = []
    with open(file=filename, mode='r') as f:
        text = f.readline()
        while text:
            match = re.search(expr, text)
            # we're occasionally getting empty matches here, so let's avoid that ...
            #if match and len(match.group(1)) > 0:
            if match:
                responses.append(match.group(1))
            text = f.readline()
            print(f"Text: {text}")
    return responses

def send_request(role: str, message: str, temperature=0.7) -> typing.Any:
    
    url = "http://localhost:1234/v1/chat/completions"

    # Your request payload
    payload = {
        "messages": [
            { "role": "system", "content": role },
            { "role": "user", "content": message }
        ],
        "temperature": temperature,
        "max_tokens": -1,
        "stream": False
    }

    headers = {
        "Content-Type": "application/json"
    }

    # Send POST request
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    # Check for successful response
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Request failed with status code " + str(response.status_code)}
    
def set_LLM_prompt(object: str) -> str:
    return f"""
I'd like you to take the alternate uses test. This is a classic creativity test used to measure flexibility of thinking. It provides you with a random object . You have to come up with as many alternative uses for it as you can.

For example, if you were given the item ‘coffee cup’, you might come up with things like:

a small soup bowl
a plant pot for some basil
a scoop for a big barrel of oats
a hat for an elf in a thunderstorm
use upside down as a spider trap
a percussion instrument you hit with a drumstick
a template to draw a perfect circle

Some of these are more obvious than others. So you can measure your output for both quantity and quality. In fact, the classic test measures the output in four ways:

Fluency - this is the total number of alternative uses you come up with
Originality - this is how unique your answers are
Flexibility - this is the breadth of categories you cover with your ideas
Elaboration - this is the amount of detail you give in your answers

I just need a list of answers. Using the coffee cup example above, these would be of the form

Use an upside-down coffee cup as a hat for an elf
Use a coffee cup as a scoop for a big barrel of oats
Use a coffee cup as a percussion instrument you hit with a drumstick
... and so on

Generate fluent, original, flexible, and elaborate examples, using the random object given below. Humorous and absurd or surreal examples are welcome!

The random object is:

{object}

Please provide 40 examples.
"""
    
def match_bot_response(bot_response: str, result_pattern: str = r"\[RESULT\]\s(\d)") -> str:
    match = re.search(result_pattern, bot_response)
    if match:
        return match.group(1)
    else:
        return ''
    
def build_orig_instruction(obj: str) -> str:
    """Given a string of the object we're prompting for, build the original instruction."""
    return f"""
I'd like you to take the alternate uses test. This is a classic creativity test used to measure flexibility of thinking. It provides you with a random object . You have to come up with as many alternative uses for it as you can.

For example, if you were given the item ‘coffee cup’, you might come up with things like:

a small soup bowl
a plant pot for some basil
a scoop for a big barrel of oats
a hat for an elf in a thunderstorm
use upside down as a spider trap
a percussion instrument you hit with a drumstick
a template to draw a perfect circle

Some of these are more obvious than others. So you can measure your output for both quantity and quality. In fact, the classic test measures the output in four ways:

Fluency - this is the total number of alternative uses you come up with
Originality - this is how unique your answers are
Flexibility - this is the breadth of categories you cover with your ideas
Elaboration - this is the amount of detail you give in your answers

I just need a list of answers. Using the coffee cup example above, these would be of the form

Use an upside-down coffee cup as a hat for an elf
Use a coffee cup as a scoop for a big barrel of oats
Use a coffee cup as a percussion instrument you hit with a drumstick
... and so on

Generate fluent, original, flexible, and elaborate examples, using the random object given below. Humorous and absurd or surreal examples are welcome!


The random object is:

{obj}
"""

def build_relative_prompt(
    instruction: str,
    response_A: str,
    response_B: str,
    rubric: str,
    reference_answer: str = None) -> str:
    """We build the prompt from the (filled-in) template, the instructions, the two responses, and the citeria."""
    return f'###Task Description:\nAn instruction (might include an Input inside it), a response to evaluate, a reference answer, and a score rubric representing a evaluation criteria are given.\n1. Write a detailed feedback that assess the quality of two responses strictly based on the given score rubric, not evaluating in general.\n2. After writing a feedback, choose a better response between Response A and Response B. You should refer to the score rubric.\n3. The output format should look as follows: "(write a feedback for criteria) [RESULT] (A or B)"\n4. Please do not generate any other opening, closing, and explanations.\n\n###Instruction:\n{instruction}\n\n###Response A:\n{response_A}\n\n###Response B:\n{response_B}\n\n###Reference Answer:\n{reference_answer}\n\n###Score Rubric:\n{rubric}\n\n###Feedback: '
    
def build_absolute_prompt(
    instruction: str,
    response: str,
    rubric: str,
    reference_answer: str = None) -> str:
    """Build an absolute prompt. Since we're using a local version of `prometheus_eval`, we're going to use requests & mock the API call."""
    return f"""###Task Description:
An instruction (might include an Input inside it), a response to evaluate, a reference answer that gets a score of 5, and a score rubric representing a evaluation criteria are given.
1. Write a detailed feedback that assess the quality of the response strictly based on the given score rubric, not evaluating in general.
2. After writing a feedback, write a score that is an integer between 1 and 5. You should refer to the score rubric.
3. The output format should look as follows: "(write a feedback for criteria) [RESULT] (an integer number between 1 and 5)"
4. Please do not generate any other opening, closing, and explanations.

###The instruction to evaluate:
{instruction}

###Response to evaluate:
{response}

###Reference Answer (Score 5):
{reference_answer}

###Score Rubrics:
{rubric}

###Feedback: 
"""

def build_rubric(obj: str) -> str:
    """Build up our socring rubric."""
    rubric_data = {
        "criteria":f"Is the model responding with creative, fluent, original, and flexible alternate uses of the given object, {obj}?",
        "score1_description":"The model shows little creative, fluent, original and flexible alternate uses of the object.",
        "score2_description":"The model has some creative, fluent, original and flexible alternate uses of the object.",
        "score3_description":"The model shows some creativity and originality in its alternate uses of the object.",
        "score4_description":"The model consistently identifies creative, fluent, original and flexible alternate uses of the object.",
        "score5_description":"The model excels in identifying creative, fluent, original and flexible alternate uses of the object."
    }
    score_rubric = SCORE_RUBRIC_TEMPLATE.format(**rubric_data)
    return score_rubric

def build_absolute_prompt(
    instruction: str,
    response: str,
    rubric: str,
    reference_answer: str = None) -> str:
    """Build an absolute prompt. Since we're using a local version of `prometheus_eval`, we're going to use requests & mock the API call."""
    return f"""###Task Description:
An instruction (might include an Input inside it), a response to evaluate, a reference answer that gets a score of 5, and a score rubric representing a evaluation criteria are given.
1. Write a detailed feedback that assess the quality of the response strictly based on the given score rubric, not evaluating in general.
2. After writing a feedback, write a score that is an integer between 1 and 5. You should refer to the score rubric.
3. The output format should look as follows: "(write a feedback for criteria) [RESULT] (an integer number between 1 and 5)"
4. Please do not generate any other opening, closing, and explanations.

###The instruction to evaluate:
{instruction}

###Response to evaluate:
{response}

###Reference Answer (Score 5):
{reference_answer}

###Score Rubrics:
{rubric}

###Feedback: 
"""