from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import pyttsx3
import speech_recognition as sr
import os

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

engine = pyttsx3.init()
recognizer = sr.Recognizer()

def speak(text):
    engine.say(text)
    engine.runAndWait()

@app.route('/ask-question', methods=['GET'])
def ask_question():
    prompt = "Generate one technical interview question for a student."

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}]
    )

    question = response.choices[0].message.content
    speak(question)

    return jsonify({"question": question})

@app.route('/speech-to-text', methods=['GET'])
def speech_to_text():
    with sr.Microphone() as source:
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
    except:
        text = "Could not understand audio"

    return jsonify({"text": text})

@app.route('/evaluate', methods=['POST'])
def evaluate():
    data = request.json
    question = data.get("question", "")
    answer = data.get("answer", "")

    prompt = f"""
    You are an expert interviewer.

    Question: {question}
    Answer: {answer}

    Evaluate based on:
    Communication, Fluency, Confidence, Relevance.

    Return JSON:
    {{
        "communication": number,
        "fluency": number,
        "confidence": number,
        "relevance": number,
        "feedback": "short feedback"
    }}
    """

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}]
    )

    result = response.choices[0].message.content

    return jsonify({"result": result})

@app.route('/overall-feedback', methods=['POST'])
def overall_feedback():
    data = request.json
    qa_list = data.get("qa_list", [])

    prompt = f"""
    You are a professional interview evaluator.

    Analyze this interview:
    {qa_list}

    Give JSON output:
    {{
        "communication": number,
        "fluency": number,
        "confidence": number,
        "relevance": number,
        "strengths": [],
        "improvements": [],
        "final_feedback": "detailed paragraph"
    }}
    """

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}]
    )

    result = response.choices[0].message.content

    speak(result)

    return jsonify({"result": result})

if __name__ == '__main__':
    app.run(debug=True)
