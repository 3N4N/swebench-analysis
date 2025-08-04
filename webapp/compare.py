import json
from datasets import load_dataset
from flask import Flask, render_template, request
import pandas as pd
import pyperclip as pclip

app = Flask(__name__)

instances = [
    "django__django-16454",
    "sympy__sympy-23950",
]

model = 'devstral_24b_maxiter_30_N_v0.43.0-no-hint-run_1'
instance_id = instances[0]

def get_patches(df1, df2, instance_id):
    left_patch = df1[df1['instance_id'] == instance_id]['model_patch'].values[0]
    right_patch = df2[df2['instance_id'] == instance_id]['model_patch'].values[0]

    # patch_gold  = row.iloc[0]['patch']
    # patch_model = row.iloc[0]['model_patch']

    print(left_patch)
    return left_patch, right_patch

@app.route("/", methods=["GET", "POST"])
def compare():
    global model
    global instance_id
    global instances

    # sweb_full = load_dataset("SWE-bench/SWE-bench")
    # df = sweb_full['test'].to_pandas()
    df1 = pd.read_json('../OpenHands/evaluation/evaluation_outputs/outputs/SWE-bench__SWE-bench_Verified-test/CodeActAgent/devstral_24b_maxiter_30_N_v0.43.0-no-hint-run_1-default/output.swebench.jsonl', lines=True)
    df2 = pd.read_json('../OpenHands/evaluation/evaluation_outputs/outputs/SWE-bench__SWE-bench_Verified-test/CodeActAgent/devstral_24b_maxiter_30_N_v0.43.0-no-hint-run_1-notrace/output.swebench.jsonl', lines=True)

    if request.method == "POST":
        selected_instance = request.form.get("instance_choice")
        if selected_instance == 'left':
            index =  instances.index(instance_id) - 1
            instance_id = instances[index] if index>=0 else instance_id
        elif selected_instance == 'right':
            index =  instances.index(instance_id) + 1
            instance_id = instances[index] if index<len(instances) else instance_id
        elif selected_instance is not None:
            instance_id = selected_instance

    # print(instance_id)

    left_patch, right_patch = get_patches(df1, df2, instance_id)
    print(left_patch)
    print(type(left_patch))
    print(df1.head())

    return render_template("compare.html", left=left_patch, right=right_patch,
                           instance_id=instance_id, instance_list=instances)

if __name__ == "__main__":
    app.run(debug=True)
