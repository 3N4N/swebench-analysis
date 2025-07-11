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
