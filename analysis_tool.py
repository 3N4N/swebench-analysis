import csv
import json
import pyperclip as pclip
import getch
import pandas as pd

models = [
    '20241121_autocoderover-v2.0-claude-3-5-sonnet-20241022',
    '20241103_OpenHands-CodeAct-2.1-sonnet-20241022',
    '20250227_sweagent-claude-3-7-20250219',
]

instances = [
    # "sympy__sympy-22714",
    # "sympy__sympy-23534",
    "sympy__sympy-24066",
    "sympy__sympy-24213",
    "sympy__sympy-24443",
    "sympy__sympy-24539",
]

df = pd.read_json('merged.jsonl', lines=True)

# df = df[df['instance_id'].isin(instances)]

break_flag = False

for _, row in df[df['instance_id'].isin(instances)].iterrows():
    if break_flag:
        break
    for model in models:
        instance_id = row['instance_id']
        # print(f"Copy {instance_id} for {model}?", end='', flush=True)
        print(f"Copy {instance_id} for {model}?")
        key = getch.getch()
        if key=='q':
            break_flag = True
            break
        patch_gold  = row['patch']
        patch_model = row[model]
        text = "\"{}\"\n\"{}\"\n".format(patch_gold, patch_model)
        print(f"Copied {instance_id} for {model}")
        pclip.copy(text)

