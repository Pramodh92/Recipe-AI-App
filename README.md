Awesome! Here's your cleaned-up, professional, and copy-paste-ready version of the Recipe AI Hub README, complete with collapsible sections, table of contents, and visual hierarchy for clarity:

🍳 Recipe AI Hub

A comprehensive AI-powered recipe management and meal planning application built with Flask and modern AI technologies.

📚 Table of Contents

🌟 Features

🛠️ Technology Stack

📋 Prerequisites

🚀 Installation & Setup

🔧 Configuration Options

📁 Project Structure

🔍 API Endpoints

🐛 Common Issues & Solutions

🔒 Security Considerations

🚀 Running the Application

🤝 Contributing

📄 License

🆘 Support

🔄 Updates & Maintenance

🌟 Features

<details> <summary>🍽️ Recipe Management</summary>

AI Recipe Generation using Google Gemini AI

Search & Filter by ingredients, cuisine, dietary restrictions

Rating System with comments

Save Recipes to personal collection

Categories by cuisine type (Italian, Chinese, Indian, etc.)

</details>

<details> <summary>🤖 AI-Powered Services</summary>

Culinary Encyclopedia

Ingredient Substitution

Flavor Profile Analysis

Multi-language Support

Smart Recipe Recommendations

</details>

<details> <summary>📅 Meal Planning</summary>

Weekly Planner

Drag & Drop Interface

Nutritional Info Tracking

Shopping List Generation

</details>

<details> <summary>🛒 Shopping List Management</summary>

Smart Lists

PDF Export

List Sharing

Item Categorization

</details>

<details> <summary>👤 User Management</summary>

Authentication & Profiles

Language Preferences

JWT-based Session Management

</details>

<details> <summary>📊 Analytics & Insights</summary>

Recipe Analytics

User Activity Monitoring

Cooking Statistics

</details>

🛠️ Technology Stack

🔙 Backend

Flask 3.0.0

SQLAlchemy

Flask-JWT-Extended

Flask-CORS

🧠 AI & ML

Google Gemini AI

IBM Granite via Hugging Face

Transformers

PyTorch

🗃️ Database

SQLite (dev)

PostgreSQL (prod)

🎨 Frontend

HTML5/CSS3

JavaScript

Bootstrap

🧰 Utilities

ReportLab (PDF)

Pillow (images)

bcrypt (security)

python-dotenv (env management)

📋 Prerequisites

Python 3.8+

pip

Git

Google Gemini API Key (optional)

🚀 Installation & Setup

# 1. Clone the repo
git clone https://github.com/yourusername/recipe-ai-app.git](https://github.com/Pramodh92/Recipe-AI-App
cd recipe-ai-app

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
# Example:
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
DATABASE_URL=sqlite:///recipe_app.db
GEMINI_API_KEY=your-gemini-api-key
FLASK_ENV=development
DEBUG=True

# 5. Initialize DB
python app.py

# 6. Run the app
python app.py

🔧 Configuration Options

🌍 Environment Variables

SECRET_KEY=...
JWT_SECRET_KEY=...
DATABASE_URL=...
GEMINI_API_KEY=...
FLASK_ENV=development
DEBUG=True

🗃️ Database

SQLite (default for dev)

PostgreSQL (configurable for production)

📁 Project Structure

recipe-ai-app/
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── models/
│   ├── database.py
│   ├── recipe.py
│   └── user.py
├── routes/
│   ├── main.py
│   ├── auth.py
│   ├── recipes.py
│   ├── ai_services.py
│   └── health.py
├── services/
│   ├── ai_client.py
│   ├── auth_service.py
│   └── utils.py
├── static/
├── templates/
├── logs/
├── instance/
└── migrations/

🔍 API Endpoints

<details> <summary>🔐 Authentication</summary>

POST /auth/signup

POST /auth/login

POST /auth/logout

GET /auth/profile

PUT /auth/profile

</details>

<details> <summary>📖 Recipes</summary>

GET /recipes

POST /recipes/generate

GET /recipes/saved

POST /recipes/save

DELETE /recipes/save

POST /recipes/rate

</details>

<details> <summary>🧠 AI Services</summary>

POST /ai/encyclopedia

POST /ai/substitute-ingredient

POST /ai/flavor-profile

</details>

<details> <summary>📅 Meal Planning</summary>

GET /meal-plan

POST /meal-plan

</details>

<details> <summary>🛒 Shopping Lists</summary>

GET /shopping-lists

POST /shopping-lists

GET /shopping-lists/pdf

</details>

🐛 Common Issues & Solutions

<details> <summary>Database Errors</summary>

rm instance/app.db
python app.py

</details>

<details> <summary>Import Errors</summary>

venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt

</details>

<details> <summary>AI Service Errors</summary>

Add Gemini API key to .env

Use mock data if key is missing

</details>

<details> <summary>Port Conflicts</summary>

lsof -ti:5000 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :5000   # Windows

</details>

<details> <summary>Other Errors</summary>

JWT expired → clear cookies

PDF/Image import errors → reinstall ReportLab/Pillow

CORS issues → check headers

Memory errors → optimize queries, close apps

</details>

🔒 Security Considerations

<details> <summary>Best Practices</summary>

Change default secrets

Secure API keys

Validate inputs

Never commit .env files

Use separate dev/prod keys

Rotate secrets regularly

</details>

🚀 Running the Application

python app.py

App runs at: http://localhost:5000

🤝 Contributing

Fork the repo

Create a feature branch

Make changes

Add tests

Submit a pull request

📄 License

MIT License — see LICENSE file.

🆘 Support

Open a GitHub issue

Check troubleshooting section

Review logs in logs/ directory

🔄 Updates & Maintenance

<details> <summary>Maintenance Tasks</summary>

pip install -r requirements.txt --upgrade

Monitor logs

Backup DB

Rotate API keys

</details>

<details> <summary>Version Updates</summary>

Test Flask compatibility

Validate AI integrations

Update documentation

</details>

Happy Cooking! 🍳✨

Let me know if you want this styled for GitHub Pages or turned into a documentation site. I can help scaffold that too.

