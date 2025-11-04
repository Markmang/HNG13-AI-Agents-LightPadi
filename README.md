# HNG13-AI-Agents-LightPadi

LightPadi is an intelligent AI-powered agent that predicts and records real-time electricity status across major Nigerian cities.
It learns from user-submitted power reports to forecast when NEPA will bring or take light, offering users a friendly, chat-style experience.

This agent integrates seamlessly with Telex for conversational AI automation, but it can also function independently via API calls.


---

🚀 Features

✅ Predicts power (electricity) status in Nigerian cities
✅ Records user reports of light being “on” or “off”
✅ Supports conversational integrations (e.g., Telex A2A)
✅ Responds in friendly, natural language
✅ Returns structured JSON responses
✅ Handles invalid or unsupported city queries gracefully
✅ Includes a /ping/ endpoint for health checks


---

🏗 Tech Stack

Python 3.10+

Django 5.2+

Django REST Framework (DRF)

SQLite (default for local & PythonAnywhere free tier)



---

🧩 Project Structure

HNG13-AI-Agents-LightPadi/
│
├── agent/
│   ├── migrations/
│   ├── models.py          # PowerReport model
│   ├── views.py           # Core logic for /predict/, /report/, /ping/
│   ├── utils.py           # AI logic & Nigerian cities dictionary
│   ├── urls.py            # API route definitions
│   └── admin.py
│
├── lightpadi_project/
│   ├── settings.py        # Django configuration
│   ├── urls.py            # Main URL entry point
│   └── wsgi.py
│
├── requirements.txt       # Python dependencies
├── manage.py
└── README.md              # Documentation (this file)


---

⚙ Installation and Setup

1️⃣ Clone the repository

git clone https://github.com/Markmang/HNG13-AI-Agents-LightPadi.git
cd HNG13-AI-Agents-LightPadi

2️⃣ Create and activate a virtual environment

python -m venv venv
source venv/bin/activate       # On Mac/Linux
venv\Scripts\activate          # On Windows

3️⃣ Install dependencies

pip install -r requirements.txt

4️⃣ Run migrations

python manage.py migrate

5️⃣ Start the development server

python manage.py runserver

Then visit:
👉 http://127.0.0.1:8000/


---

🧠 API Documentation

🔹 Health Check

GET /ping/

Returns a quick status response to confirm the app is running.

Example

curl https://mangi.pythonanywhere.com/ping/

Response

{
  "status": "ok",
  "app": "LightPadi running live on PythonAnywhere",
  "version": "v1.0.0"
}


---

🔹 Predict Power Status

POST /predict/

Predicts the likely current power status for a given city using recent data.

Request Body

{
  "message": {
    "parts": [
      {"kind": "text", "text": "check power status, location lagos"}
    ]
  }
}

Response

{
  "text": "🔆 LightPadi: Power looks stable in Lagos right now. (Confidence: 0.89)"
}

If no data exists yet:

{
  "text": "🔆 LightPadi: No data for Lagos yet. Help me learn — tell me if there’s light 💡."
}


---

🔹 Report Power Status

POST /report/

Records the user’s report of whether light is on or off in a given Nigerian city.

Request Body

{
  "message": {
    "parts": [
      {"kind": "text", "text": "There is no light in Abuja"}
    ]
  }
}

Response

{
  "text": "⚡ LightPadi: Got it! I’ve recorded that there’s no light in Abuja."
}

If unsupported city:

{
  "text": "🇳🇬 Sorry, LightPadi currently supports only major Nigerian cities."
}


---

💬 Telex Integration (A2A Workflow)

LightPadi integrates directly with Telex as an AI agent workflow.

Example workflow JSON:

{
  "active": true,
  "category": "utilities",
  "description": "AI agent that predicts and records power status across Nigerian cities.",
  "name": "LightPadi – Nigeria’s Smart Power Companion ⚡",
  "nodes": [
    {
      "id": "lightpadi_predict",
      "name": "LightPadi Predict",
      "parameters": { "historyLength": 2 },
      "type": "a2a/mastra-a2a-node",
      "url": "https://mangi.pythonanywhere.com/predict/"
    },
    {
      "id": "lightpadi_report",
      "name": "LightPadi Report",
      "parameters": { "historyLength": 2 },
      "type": "a2a/mastra-a2a-node",
      "url": "https://mangi.pythonanywhere.com/report/"
    },
    {
      "id": "lightpadi_ping",
      "name": "LightPadi Ping",
      "parameters": {},
      "type": "a2a/mastra-a2a-node",
      "url": "https://mangi.pythonanywhere.com/ping/"
    }
  ]
}

This configuration:

Limits Telex message history to the last 2 messages

Connects /predict/, /report/, and /ping/ directly

Prevents confusion from long chat logs



---

🧪 Testing with cURL

Predict:

curl -X POST http://127.0.0.1:8000/predict/ \
  -H "Content-Type: application/json" \
  -d '{
        "message": {
          "parts": [
            {"kind": "text", "text": "check power status, location abuja"}
          ]
        }
      }'

Report:

curl -X POST http://127.0.0.1:8000/report/ \
  -H "Content-Type: application/json" \
  -d '{
        "message": {
          "parts": [
            {"kind": "text", "text": "there is light in lagos"}
          ]
        }
      }'


---

🌍 Deployment

Deployed live on PythonAnywhere:
🔗 https://mangi.pythonanywhere.com


---

👨‍💻 Author

Udeagha Mark Mang
Backend Developer | AI Agent Integrator | ALX Software Engineering Graduate
📧 marku@mangi
🌐 GitHub – Markmang
