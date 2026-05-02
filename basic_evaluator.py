from flask import Flask, request, jsonify
from flask_cors import CORS
import pyttsx3

app = Flask(__name__)
CORS(app)

engine = pyttsx3.init()

def speak_text(text):
    engine.say(text)
    engine.runAndWait()

@app.route('/evaluate', methods=['POST'])
def evaluate():
    data = request.json
    answer = data.get("answer", "")

    length_score = min(len(answer.split()) / 10, 1) * 10
    confidence_score = 8 if "I think" not in answer else 5
    relevance_score = 9 if len(answer) > 20 else 6
    fluency_score = 8

    feedback = {
        "communication": round(length_score, 2),
        "fluency": fluency_score,
        "confidence": confidence_score,
        "relevance": relevance_score
    }

    return jsonify(feedback)

@app.route('/overall-feedback', methods=['POST'])
def overall_feedback():
    data = request.json
    answers = data.get("answers", [])

    total_comm = 0
    total_fluency = 0
    total_conf = 0
    total_rel = 0

    for ans in answers:
        words = len(ans.split())
        total_comm += min(words / 10, 1) * 10
        total_fluency += 8
        total_conf += 8 if "I think" not in ans else 5
        total_rel += 9 if words > 20 else 6

    n = len(answers) if answers else 1

    avg_feedback = {
        "communication": round(total_comm / n, 2),
        "fluency": round(total_fluency / n, 2),
        "confidence": round(total_conf / n, 2),
        "relevance": round(total_rel / n, 2),
    }

    strengths = []
    improvements = []

    if avg_feedback["communication"] > 7:
        strengths.append("Good communication skills")
    else:
        improvements.append("Improve clarity and sentence structure")

    if avg_feedback["fluency"] > 7:
        strengths.append("Fluent speaking style")
    else:
        improvements.append("Work on speaking smoothly")

    if avg_feedback["confidence"] > 7:
        strengths.append("Confident delivery")
    else:
        improvements.append("Avoid hesitation and filler words")

    if avg_feedback["relevance"] > 7:
        strengths.append("Relevant answers")
    else:
        improvements.append("Stay focused on the question")

    summary_text = f"""
    Your interview performance is evaluated as follows:
    Communication: {avg_feedback['communication']},
    Fluency: {avg_feedback['fluency']},
    Confidence: {avg_feedback['confidence']},
    Relevance: {avg_feedback['relevance']}.

    Strengths: {', '.join(strengths)}.
    Areas to improve: {', '.join(improvements)}.
    """

    speak_text(summary_text)

    return jsonify({
        "average_scores": avg_feedback,
        "strengths": strengths,
        "improvements": improvements,
        "summary": summary_text
    })
    

if __name__ == '__main__':
    app.run(debug=True)
