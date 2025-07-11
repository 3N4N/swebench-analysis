from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

def get_patches(df, model, instance_id):
    row = df[df['instance_id'] == instance_id]
    patch_gold  = row.iloc[0]['patch']
    patch_model = row.iloc[0][model]

    return patch_gold, patch_model

@app.route("/", methods=["GET", "POST"])
def compare():
    df = pd.read_json('merged.jsonl', lines=True)
    models = [
        '20241121_autocoderover-v2.0-claude-3-5-sonnet-20241022',
        '20241103_OpenHands-CodeAct-2.1-sonnet-20241022',
        '20250227_sweagent-claude-3-7-20250219',
    ]

    model = models[0]

    if request.method == "POST":
        action = request.form.get("action")
        if action == 'model1':
            model = models[0]
        elif action == 'model2':
            model = models[1]
        elif action == 'model3':
            model = models[2]
        else:
            raise ValueError(f"Selected action {action} is unknown")

    instance_id = "sympy__sympy-24066"
    left_patch, right_patch = get_patches(df, model, instance_id)
    return render_template("compare.html", left=left_patch, right=right_patch,
                           instance_id=instance_id, model1=models[0],
                           model2=models[1], model3=models[2])

if __name__ == "__main__":
    app.run(debug=True)

