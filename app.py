from flask import Flask, render_template, request, jsonify
import torch
from transformers import AutoModelForQuestionAnswering, AutoTokenizer

chapters = {
    "Chapter 1": "chapters/chapter1.txt"
    #"Chapter 2": "chapters/chapter2.txt",
    #"Chapter 3": "chapters/chapter3.txt"
}

model_name = 'valhalla/longformer-base-4096-finetuned-squadv1'
model = AutoModelForQuestionAnswering.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

def QnA(question, context):
    input = tokenizer(question, context, return_tensors="pt")
    output = model(**input)
    ans_start_idx = torch.argmax(output.start_logits)
    ans_end_idx = torch.argmax(output.end_logits)
    ans_tokens = input.input_ids[0, ans_start_idx:ans_end_idx + 1]
    ans = tokenizer.decode(ans_tokens)
    return ans

app = Flask(__name__)

@app.route('/chapter/<name>', methods=['GET', 'POST'])
def chapter(name):
    file_path = chapters.get(name)
    if not file_path:
        return jsonify({"error": "Chapter not found"}), 404
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        if request.method == 'POST':
            question_text = request.form['question']
            try:
                result = QnA(question_text, content)
                return render_template('chapter.html', name=name, content=content, question=question_text, result=result)
            except (ValueError, IndexError) as e:
                error_msg = f'Invalid input! Please enter a valid question. Error: {str(e)}'
                return render_template('chapter.html', name=name, content=content, error_msg=error_msg)
        else:
            return render_template('chapter.html', name=name, content=content)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', chapters=chapters)

if __name__ == '__main__':
    app.run(debug=True)
