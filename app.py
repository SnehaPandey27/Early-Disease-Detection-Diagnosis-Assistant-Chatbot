import re
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)  # Correct Flask app initialization
CORS(app)

# Your API Key (consider using an environment variable for security)
OPENROUTER_API_KEY = "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"

modelR1 = "deepseek/deepseek-r1:free"
modelV1 = "deepseek/deepseek-chat:free"
model7B = "mistralai/mistral-7b-instruct:free"
model70B = "deepseek/deepseek-r1-distill-llama-70b:free"

BASEURL = "https://openrouter.ai/api/v1/chat/completions"


def checkCondition(query, model):
    try:
        response = requests.post(
            BASEURL,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [
            {"role": "system", "content": "You are a classification bot. Only return the category number."},
            {"role": "user", "content": f"""Categorize the following query into one of the categories below.  
            
            Query: "{query}"  
            
            Categories:  
            1 - General Medical Query  
            2 - Medical Symptoms  
            3 - Non-Medical  
            
            Respond with only the category number (1, 2, or 3). Do not add any extra text."""}
            ],
            },
        )
        response_json = response.json()
        return response_json["choices"][0]["message"]["content"].strip().lower()
    
    except Exception as e:
        print(f"Error in checkCondition: {e}")
        return "error"
    

def genResponse(query, context = 'None', queryCategory = "1", model = model7B):
    if queryCategory == "2":
        sysContent = f"You are an AI Health assistant providing structured responses by analysing the context."
        userContent = f"Analyse the context and provide a detailed analysis and solution for the query."
        context = f"Context: {context}"
        format = f"""Give response in following format:
            <Possible health issue>
            <probablity>
            <severaty level>
            <Possible cause>
            <Possible solution>
            <recommended action>
            
            Constraints: Give the response in dict format"""
    else:
        sysContent = f"You are an AI Health assistant providing structured responses for the query."
        userContent = f"Provide a detailed analysis and solution for the query."
        context = f""
        format = f""""""
            
    try:
        response = requests.post(
            BASEURL,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": f"{sysContent}"},
                    {"role": "user",
                    "content": f"""{userContent}\n
                    query: {query}\n
                    {context}\n
                    """ + format
                }],
            },
        )
        response_json = response.json()
        return response_json["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Error in gen_response: {e}")
        return "I'm sorry, I couldn't generate a response."


def genMedicalHistoryQues(query, model):
    medHistoryTemplate = """category 1. History of Present Illness (HPI) (Use the OLD CARTS or PQRST method):
                        Onset: When did the symptoms start?
                        Location: Where do you feel the pain or discomfort?
                        Duration: How long have you had this issue?
                        Character: Can you describe the symptom? (e.g., sharp, dull, burning)
                        Aggravating/Alleviating Factors: "What makes it worse or better?"
                        Radiation: Does the pain or discomfort spread anywhere?
                        Timing: Is it constant or does it come and go?
                        Severity: On a scale of 1-10, how severe is it?

                        category 2. Past Medical History (PMH):
                        Do you have any existing medical conditions?
                        Have you been diagnosed with any chronic illnesses (e.g., diabetes, hypertension)?
                        Have you had any surgeries or hospitalizations in the past?
                        Have you had any major infections or illnesses before?

                        category 3. Medications & Allergies:
                        Are you currently taking any medications, including over-the-counter or supplements?
                        Do you have any known drug, food, or environmental allergies?

                        category 4. Family History (FH):
                        Does anyone in your family have a history of chronic illnesses like diabetes, heart disease, or cancer?
                        Has anyone in your family had similar symptoms or conditions?
                        """
                        
    try:
        response = requests.post(
            BASEURL,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [{
                    "role": "user",
                    "content": f"""Query: {query},
                        Modify and give max 7 medical-history questions that are relevant to this query, from this set of medical-history questions:
                        
                        Medical-history Questions:
                        {medHistoryTemplate}
                        
                        Give response in this format:
                        <Question 1>
                        <Question 2>
                        <Question 3>
                        ...
                        
                        Constrains: Do not generate any other text other than the questions.
                        """
                }]
            },
        )
        return response.json()["choices"][0]["message"]["content"].strip().split('\n')[:3]
    except Exception as e:
        print(f"Error in gen_followups: {e}")
        return []
    
    
def getUserResponses():
    dummy_responses = [
    # Category 1: History of Present Illness (HPI)
    "I first experienced these migraines about 2 years ago.",
    "I feel the migraine pain mostly on one side of my head, sometimes behind my eyes.",
    "I've been experiencing these migraines on and off for the past 2 years.",
    "The migraine feels like a throbbing, pulsating pain.",
    "Stress and lack of sleep seem to trigger my migraines, while rest and hydration help alleviate them.",
    "Yes, sometimes the pain spreads to my neck and shoulders.",
    "They come and go, usually lasting for a few hours.",
    "I would rate the severity of my migraines around 7 out of 10.",

    # Category 2: Past Medical History (PMH)
    "I have no chronic illnesses, but I do have occasional tension headaches.",
    "No, I have never had any surgeries or hospitalizations related to migraines or other health issues.",
    "No major infections or illnesses that I can recall.",

    # Category 3: Medications & Allergies
    "I sometimes take over-the-counter painkillers like ibuprofen when the migraine is severe.",
    "I have no known drug, food, or environmental allergies.",

    # Category 4: Family History (FH)
    "Yes, my father has hypertension, and my mother has diabetes.",
    "Yes, my mother also experiences migraines occasionally."
    ]

    return dummy_responses

    
def getRealTimeData():
    normalData = {"timestamp": "2025-02-25 10:05:00",
    "heart_rate_bpm": 110,
    "spo2_percentage": 95,
    "body_temperature_c": 36.9,
    "steps": 650,
    "calories_burned": 35,
    "stress_level": 8,
    "sleep_hours": 6.5,
    "blood_pressure_mmHg": "100/95",
    "irregular_heartbeat": False
    }
    
    health_alert = {
    "timestamp": "2025-02-25 11:30:00",
    "heart_rate_bpm": 135,  # Elevated heart rate (Tachycardia)
    "spo2_percentage": 92,  # Low oxygen saturation
    "body_temperature_c": 37.2,  # Slightly elevated temperature
    "steps": 300,  # Low movement but high heart rate
    "calories_burned": 15,  # Not actively burning much energy
    "stress_level": 9,  # High stress level
    "sleep_hours": 4.0,  # Poor sleep
    "blood_pressure_mmHg": "150/95",  # High blood pressure (Hypertension)
    "irregular_heartbeat": True,  # Arrhythmia detected
    }
    return json.dumps(normalData, indent=4)


def mergeFollowupsResponse(medicalHistoryQues, userResponses, RealTimeData):
    context = ""
    
    # Correctly iterate through paired values
    for i, (question, response) in enumerate(zip(medicalHistoryQues, userResponses)):
        question_text = question.split(".", 1)[-1].strip()  # Handle only first period for better readability
        context += f"Follow-up {i + 1}: {question_text}. Response: {response}\n"
    
    context += f"\nReal-Time Data:\n{RealTimeData}\n"
    
    return context


@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"error": "No query provided"}), 400

    # Checking query category
    category = checkCondition(query, model7B)
    medicalHistoryQues = None
    context = ''
    response = ''
    
    if "1" in category:
        response = genResponse(query, queryCategory="1", model = model7B)
        return jsonify({"query": query, "response": response})
    elif "2" in category:
        medicalHistoryQues = genMedicalHistoryQues(query, model7B)
        # userResponses = getUserResponses()
        # RealTimeData = getRealTimeData()
        # print(medicalHistoryQues)
        # print(category)
        # context = mergeFollowupsResponse(medicalHistoryQues, userResponses, RealTimeData)
        # print(context)
        response = genResponse(query, queryCategory="1", model = model7B)
        return jsonify({"query": query, "response": response, "followups": medicalHistoryQues})
        
    else:
        return jsonify({"response": "I am sorry, I can only respond to medical-related queries!"})
    

@app.route('/answer', methods=['POST'])
def answer():
    data = request.json
    data = request.json
    
    medicalHistoryQues = data.get("followups", [])
    print(medicalHistoryQues)
    userResponses = data.get("responses", [])
    print(userResponses)
    RealTimeData = getRealTimeData()

    if not medicalHistoryQues or not userResponses:
        return jsonify({"error": "Missing follow-up questions or responses."}), 400

    context = mergeFollowupsResponse(medicalHistoryQues, userResponses, RealTimeData)
    query = "Analyse the context and give detailed response in the stated format."
    final_response =  genResponse(query, context = context, queryCategory="2", model = model7B)
    print(final_response)

    return jsonify({"final_response": final_response})

if __name__ == '__main__':  # Correct __name__ check
    app.run(debug=True, port=5001)
