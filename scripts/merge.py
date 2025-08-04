"""
so final merged should have, instance_id, problem statement, hints, test patch,
solution leak type, autocoderover patch, swe-agent 1 patch, openhands patch,
and whatever other columns but these are main.
"""


import json
import pandas as pd
from datasets import load_dataset

sbf = load_dataset('princeton-nlp/SWE-bench', split='test')
sbl = load_dataset('princeton-nlp/SWE-bench_Lite', split='test')
sbv = load_dataset('princeton-nlp/SWE-bench_Verified', split='test')

df_swebf = sbf.to_pandas()
df_swebl = sbl.to_pandas()
df_swebv = sbv.to_pandas()

df_sweb = pd.read_csv('swe_bench.csv')

with open('unique_merged.txt', 'r') as f:
    instances = [line.strip().replace('"','').replace(',','') for line in f if line.strip()]

df = df_sweb[df_sweb['instance_id'].isin(instances)]


with open('swe_solution_leak_outputs.json', 'r') as f:
    data = json.load(f)
    df_leak = pd.json_normalize(data['results'])
    df = pd.merge(df, df_leak[['instance_id','Leakage Type']], on='instance_id', how='left')


models = [
    '20241121_autocoderover-v2.0-claude-3-5-sonnet-20241022',
    '20241103_OpenHands-CodeAct-2.1-sonnet-20241022',
    '20250227_sweagent-claude-3-7-20250219',
]

resolved_instances = []

for model in models:
    with open('evaluation/test/{}/results/results.json'.format(model), 'r') as f:
        data = json.load(f)
        resolved_instances.append(data['resolved'])

unique_instances = set.union(set(resolved_instances[0]), set(resolved_instances[1]), set(resolved_instances[2]))
common_instances = set.intersection(set(resolved_instances[0]), set(resolved_instances[1]), set(resolved_instances[2]))

unique_instances_f = [instance for instance in unique_instances if instance in df_swebf['instance_id'].tolist()]
unique_instances_v = [instance for instance in unique_instances if instance in df_swebv['instance_id'].tolist()]
unique_instances_l = [instance for instance in unique_instances if instance in df_swebl['instance_id'].tolist()]
unique_instances_vol = [instance for instance in unique_instances if instance in df_swebv['instance_id'].tolist() or instance in df_swebl['instance_id'].tolist()]
unique_instances_val = [instance for instance in unique_instances if instance in df_swebv['instance_id'].tolist() and instance in df_swebl['instance_id'].tolist()]

common_instances_f = [instance for instance in common_instances if instance in df_swebf['instance_id'].tolist()]
common_instances_v = [instance for instance in common_instances if instance in df_swebv['instance_id'].tolist()]
common_instances_l = [instance for instance in common_instances if instance in df_swebl['instance_id'].tolist()]
common_instances_vol = [instance for instance in common_instances if instance in df_swebv['instance_id'].tolist() or instance in df_swebl['instance_id'].tolist()]
common_instances_val = [instance for instance in common_instances if instance in df_swebv['instance_id'].tolist() and instance in df_swebl['instance_id'].tolist()]

for i,model in enumerate(models):
    resolved_instances_f = [instance for instance in resolved_instances[i] if instance in df_swebf['instance_id'].tolist()]
    resolved_instances_v = [instance for instance in resolved_instances[i] if instance in df_swebv['instance_id'].tolist()]
    resolved_instances_l = [instance for instance in resolved_instances[i] if instance in df_swebl['instance_id'].tolist()]
    print(i, model)
    print(i, len(resolved_instances_f), len(resolved_instances_v), len(resolved_instances_l))

len(unique_instances_f), len(unique_instances_v), len(unique_instances_l), len(unique_instances_vol), len(unique_instances_val)
len(common_instances_f), len(common_instances_v), len(common_instances_l), len(common_instances_vol), len(common_instances_val)

for model in models:
    df_model = pd.read_json('preds/{}.jsonl'.format(model), lines=True)
    df_model = df_model[df_model['instance_id'].isin(instances)]
    df = pd.merge(df, df_model[['instance_id','model_patch']], on='instance_id', how='left')
    df.rename(columns={'model_patch': model}, inplace=True)

# df = df.head(10)

df.to_json('merged.jsonl', orient='records', lines=True)




df = pd.read_csv('verilite.csv')
incomplete_instances = df[
        df['Pattern for AutoCodeRover'].isin(['Incorrect','Incomplete']) \
        | df['Pattern for OpenHands'].isin(['Incorrect','Incomplete']) \
        | df['Pattern for SWE-Agent'].isin(['Incorrect','Incomplete']) \
]['instance_id'].tolist()

import csv
with open('incomplete_instances.csv', 'w', newline='') as file:
        writer = csv.writer(file)
            writer.writerow(incomplete_instances)



problem_statements = df_swebf['problem_statement'].tolist()


def get_locality(patch):
    localities = { }
    lines = patch.split('\n')
    parsing = False
    filepath = None
    for line in lines:
        if line.startswith('---'):
            filepath = line[6:]
        elif line.startswith('@@'):
            ind = line.index('@@', len('@@'))
            signature = line[ind+len('@@')+1:]
            localities.setdefault(filepath, []).append(signature)
    return localities

localities = []
for _, instance in df.iterrows():
    patch = instance[models[0]]
    # print(patch)
    _localities = get_locality(patch)
    localities.append(_localities)
    if len(_localities) > 1:
        print(patch)
        print(_localities)
    # break

cnt = 0
x = []
for _, instance in df.iterrows():
    z = instance['FAIL_TO_PASS']
    z = ast.literal_eval(z)
    if len(z) >= 0:
        patch = instance['test_patch']
        if '+def ' not in patch:
            x.append(instance['instance_id'])
            print(instance['instance_id'])
            print('-'*10)
            print(patch)
        else:
            cnt += 1
