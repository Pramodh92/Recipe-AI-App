# Recipe AI Hub 🍳

A comprehensive AI-powered recipe management and meal planning application built with Flask and modern AI technologies.

## 🌟 Features

### 🍽️ Recipe Management
- **AI Recipe Generation**: Generate personalized recipes using Google Gemini AI
- **Recipe Search & Filter**: Find recipes by ingredients, cuisine, dietary restrictions
- **Recipe Rating System**: Rate and review recipes with comments
- **Recipe Saving**: Save your favorite recipes to your personal collection
- **Recipe Categories**: Organize recipes by cuisine type (Italian, Chinese, Indian, etc.)

### 🤖 AI-Powered Services
- **Culinary Encyclopedia**: Get detailed explanations of cooking terms and techniques
- **Ingredient Substitution**: Find suitable substitutes for missing ingredients
- **Flavor Profile Analysis**: Analyze and understand flavor combinations
- **Multi-language Support**: Generate content in multiple languages
- **Smart Recipe Recommendations**: AI-powered recipe suggestions based on preferences

### 📅 Meal Planning
- **Weekly Meal Planner**: Plan your meals for the entire week
- **Drag & Drop Interface**: Easy-to-use meal planning interface
- **Nutritional Information**: Track nutritional content of planned meals
- **Shopping List Generation**: Automatically generate shopping lists from meal plans

### 🛒 Shopping List Management
- **Smart Shopping Lists**: Create and manage shopping lists
- **PDF Export**: Export shopping lists as PDF documents
- **List Sharing**: Share shopping lists with family members
- **Item Categories**: Organize items by categories (produce, dairy, etc.)

### 👤 User Management
- **User Authentication**: Secure login and registration system
- **User Profiles**: Manage personal information and preferences
- **Language Preferences**: Set preferred language for AI interactions
- **Session Management**: Secure JWT-based authentication

### 📊 Analytics & Insights
- **Recipe Analytics**: Track popular recipes and ratings
- **User Activity**: Monitor user engagement and preferences
- **Cooking Statistics**: View cooking history and patterns

## 🛠️ Technology Stack

### Backend
- **Flask 3.0.0**: Python web framework
- **SQLAlchemy**: Database ORM
- **Flask-JWT-Extended**: JWT authentication
- **Flask-CORS**: Cross-origin resource sharing

### AI & Machine Learning
- **Google Gemini AI**: Recipe generation and culinary assistance
- **IBM Granite**: Advanced AI capabilities via Hugging Face
- **Transformers**: Natural language processing
- **PyTorch**: Deep learning framework

### Database
- **SQLite**: Development database
- **PostgreSQL**: Production database (configurable)

### Frontend
- **HTML5/CSS3**: Modern responsive design
- **JavaScript**: Interactive user interface
- **Bootstrap**: UI framework for styling

### Utilities
- **ReportLab**: PDF generation
- **Pillow**: Image processing
- **bcrypt**: Password hashing
- **python-dotenv**: Environment variable management

## 📋 Prerequisites

Before running this application, make sure you have:

- **Python 3.8+** installed
- **pip** package manager
- **Git** for version control
- **Google Gemini API Key** (optional, for full AI features)

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/recipe-ai-app.git
cd recipe-ai-app
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the root directory:
```env
# Flask Configuration
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Database Configuration
DATABASE_URL=sqlite:///recipe_app.db

# AI API Keys (Optional)
GEMINI_API_KEY=your-gemini-api-key-here

# Production Settings
FLASK_ENV=development
DEBUG=True
```

### 5. Initialize Database
```bash
python app.py
```
The application will automatically create the database and default admin user on first run.

### 6. Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 🔧 Configuration Options

### Environment Variables
- `SECRET_KEY`: Flask secret key for session management
- `JWT_SECRET_KEY`: Secret key for JWT token generation
- `DATABASE_URL`: Database connection string
- `GEMINI_API_KEY`: Google Gemini AI API key
- `FLASK_ENV`: Environment mode (development/production)
- `DEBUG`: Debug mode flag

### Database Configuration
- **SQLite database** (default) - perfect for local development

## 📁 Project Structure

```
recipe-ai-app/
├── app.py                 # Main application entry point
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── models/              # Database models
│   ├── __init__.py
│   ├── database.py      # Database models and relationships
│   ├── recipe.py        # Recipe-related models
│   └── user.py          # User model
├── routes/              # Flask route handlers
│   ├── __init__.py
│   ├── main.py          # Main routes (home, about, etc.)
│   ├── auth.py          # Authentication routes
│   ├── recipes.py       # Recipe management routes
│   ├── ai_services.py   # AI service routes
│   └── health.py        # Health check routes
├── services/            # Business logic services
│   ├── __init__.py
│   ├── ai_client.py     # AI service client
│   ├── auth_service.py  # Authentication service
│   └── utils.py         # Utility functions
├── static/              # Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── images/
├── templates/           # HTML templates
│   ├── base.html        # Base template
│   ├── index.html       # Home page
│   ├── auth/            # Authentication templates
│   ├── recipes/         # Recipe templates
│   └── errors/          # Error page templates
├── logs/                # Application logs
├── instance/            # Instance-specific files
└── migrations/          # Database migrations
```

## 🔍 API Endpoints

### Authentication
- `POST /auth/signup` - User registration
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `GET /auth/profile` - Get user profile
- `PUT /auth/profile` - Update user profile

### Recipes
- `GET /recipes` - Get all recipes
- `POST /recipes/generate` - Generate AI recipe
- `GET /recipes/saved` - Get saved recipes
- `POST /recipes/save` - Save recipe
- `DELETE /recipes/save/<id>` - Remove saved recipe
- `POST /recipes/rate` - Rate recipe

### AI Services
- `POST /ai/encyclopedia` - Culinary encyclopedia
- `POST /ai/substitute-ingredient` - Ingredient substitution
- `POST /ai/flavor-profile` - Flavor profile analysis

### Meal Planning
- `GET /meal-plan` - Get meal plan
- `POST /meal-plan` - Save meal plan

### Shopping Lists
- `GET /shopping-lists` - Get shopping lists
- `POST /shopping-lists` - Create shopping list
- `GET /shopping-lists/<id>/pdf` - Export PDF

## 🐛 Common Issues & Solutions

### 1. Database Connection Errors
**Error**: `sqlite3.OperationalError: no such table`
**Solution**: 
```bash
# Delete existing database and recreate
rm instance/app.db
python app.py
```

### 2. Import Errors
**Error**: `ModuleNotFoundError: No module named 'flask'`
**Solution**: 
```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Reinstall dependencies
pip install -r requirements.txt
```

### 3. AI Service Errors
**Error**: `API key not configured`
**Solution**: 
- Add your Gemini API key to `.env` file
- Or use the application without AI features (mock data will be used)

### 4. Port Already in Use
**Error**: `Address already in use`
**Solution**: 
```bash
# Kill process using port 5000
lsof -ti:5000 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :5000   # Windows
```

### 5. Permission Errors
**Error**: `Permission denied`
**Solution**: 
```bash
# Check file permissions
chmod +x app.py  # macOS/Linux
```

### 6. JWT Token Errors
**Error**: `JWT token expired`
**Solution**: 
- Clear browser cookies
- Log in again
- Check system clock synchronization

### 7. PDF Generation Errors
**Error**: `ReportLab import error`
**Solution**: 
```bash
# Reinstall ReportLab
pip uninstall reportlab
pip install reportlab
```

### 8. Image Processing Errors
**Error**: `Pillow import error`
**Solution**: 
```bash
# Reinstall Pillow
pip uninstall Pillow
pip install Pillow
```

### 9. CORS Errors
**Error**: `CORS policy violation`
**Solution**: 
- Check CORS configuration in `app.py`
- Ensure proper headers are set
- Verify domain configuration

### 10. Memory Issues
**Error**: `MemoryError` or slow performance
**Solution**: 
- Increase system memory
- Optimize database queries
- Close other applications to free up memory

## 🔒 Security Considerations

### Security Best Practices
1. **Change Default Secrets**: Update SECRET_KEY and JWT_SECRET_KEY
2. **API Key Protection**: Store API keys securely
3. **Input Validation**: Validate all user inputs
4. **Environment Variables**: Never commit sensitive data to version control

### Environment Variables
- Never commit `.env` files to version control
- Use different keys for development and production
- Rotate secrets regularly

## 🚀 Running the Application

### Local Development
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section above
- Review the logs in the `logs/` directory

## 🔄 Updates & Maintenance

### Regular Maintenance Tasks
1. Update dependencies: `pip install -r requirements.txt --upgrade`
2. Check for security updates
3. Monitor application logs
4. Backup database regularly
5. Update API keys as needed

### Version Updates
- Check compatibility with new Flask versions
- Test AI service integrations
- Update documentation

---

**Happy Cooking! 🍳✨**
#   R e c i p e - A I - A p p  
 