from flask import Flask, render_template, request
import pandas as pd
import pyperclip as pclip

app = Flask(__name__)

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

model = models[0]
instance_id = instances[0]

def get_patches(df, model, instance_id):
    row = df[df['instance_id'] == instance_id]
    patch_gold  = row.iloc[0]['patch']
    patch_model = row.iloc[0][model]

    return patch_gold, patch_model

def copy_patches(patch_gold, patch_model, instance_id=None, model=None):
    text = "\"{}\"\n\"{}\"\n".format(patch_gold, patch_model)
    print(f"Copied {instance_id} for {model}")
    pclip.copy(text)

@app.route("/", methods=["GET", "POST"])
def compare():
    global model
    global instance_id
    global instances
    global models

    df = pd.read_json('merged.jsonl', lines=True)

    if request.method == "POST":
        clicked_on = request.form.get("model")
        if clicked_on == 'model1':
            model = models[0]
        elif clicked_on == 'model2':
            model = models[1]
        elif clicked_on == 'model3':
            model = models[2]

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

    left_patch, right_patch = get_patches(df, model, instance_id)

    if request.method == "POST":
        clicked_on = request.form.get("copy")
        if clicked_on == 'copy':
            copy_patches(left_patch, right_patch, instance_id, model)

    return render_template("compare.html", left=left_patch, right=right_patch,
                           instance_id=instance_id, model=model, model1=models[0],
                           model2=models[1], model3=models[2], instance_list=instances)

if __name__ == "__main__":
    app.run(debug=True)
