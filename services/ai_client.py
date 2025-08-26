import google.generativeai as genai
import requests
import json
import logging
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define config directly
class Config:
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

class AIClient:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.gemini_client = self._initialize_gemini()
        self.granite_config = self._initialize_granite()
    
    def _initialize_gemini(self):
        """Initialize Gemini AI client"""
        try:
            if Config.GEMINI_API_KEY:
                self.logger.info(f"Initializing Gemini with API key: {Config.GEMINI_API_KEY[:5]}...")
                genai.configure(api_key=Config.GEMINI_API_KEY)
                return True
            else:
                self.logger.warning("Gemini API key not configured. Using mock responses for development.")
                return False
        except Exception as e:
            self.logger.error(f"Error initializing Gemini: {str(e)}")
            return False
    
    def _initialize_granite(self):
        """Initialize IBM Granite configuration"""
        try:
            # We're using Hugging Face directly, so we don't need the API key anymore
            self.logger.info("Initializing IBM Granite with Hugging Face integration")
            return {
                'use_huggingface': True
            }
        except Exception as e:
            self.logger.error(f"Error initializing IBM Granite: {str(e)}")
            return {
                'use_huggingface': False
            }
    
    async def generate_recipe(self, ingredients: str, dietary_restrictions: str = "", 
                            cuisine: str = "", servings: int = 4, language: str = "en") -> Dict[str, Any]:
        """Generate recipe using Gemini 2.5 Flash"""
        try:
            if not self.gemini_client:
                # Return mock data for development when API key is not available
                self.logger.info("Using mock recipe data (no API key configured)")
                return {
                    "success": True,
                    "data": {
                        "title": f"Mock {cuisine or 'Mixed'} Recipe with {ingredients.split(',')[0]}",
                        "ingredients": [ingredient.strip() for ingredient in ingredients.split(',')],
                        "instructions": ["Prepare ingredients", "Cook according to preference", "Serve and enjoy"],
                        "cooking_time": 30,
                        "difficulty": "Medium",
                        "cuisine": cuisine or "International",
                        "servings": servings,
                        "flavor_profile": {
                            "spicy": 3,
                            "sweet": 5,
                            "salty": 4,
                            "sour": 2,
                            "umami": 7
                        }
                    }
                }
            
            prompt = f"""
            Create a detailed recipe using these ingredients: {ingredients}
            Dietary restrictions: {dietary_restrictions or 'None'}
            Cuisine preference: {cuisine or 'Any'}
            Servings: {servings}
            Language: {language}
            
            Format the response as JSON with these fields:
            {{
                "title": "Recipe Title",
                "ingredients": ["ingredient 1", "ingredient 2", ...],
                "instructions": ["step 1", "step 2", ...],
                "cooking_time": minutes,
                "difficulty": "Easy/Medium/Hard",
                "cuisine": "cuisine_type",
                "servings": servings_count,
                "flavor_profile": {{
                    "spicy": 0-10,
                    "sweet": 0-10,
                    "salty": 0-10,
                    "sour": 0-10,
                    "umami": 0-10
                }}
            }}
            
            Respond in {language} language.
            """
            
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            
            # Extract JSON from response
            try:
                # Try to find JSON in the response text
                response_text = response.text.strip()
                # Look for JSON-like structure
                json_start = response_text.find('{')
                json_end = response_text.rfind('}')
                
                if json_start >= 0 and json_end > json_start:
                    json_str = response_text[json_start:json_end+1]
                    recipe_data = json.loads(json_str)
                    self.logger.info(f"Generated recipe: {recipe_data.get('title', 'Unknown')}")
                    return {"success": True, "data": recipe_data}
                else:
                    # If no JSON found, structure the text response as JSON
                    self.logger.warning("No JSON found in response, creating structured response")
                    return {
                        "success": True, 
                        "data": {
                            "title": "Generated Recipe",
                            "ingredients": ["Ingredients could not be parsed"],
                            "instructions": [response_text],
                            "cooking_time": 30,
                            "difficulty": "Medium",
                            "cuisine": "Mixed",
                            "servings": 4,
                            "flavor_profile": {
                                "spicy": 5,
                                "sweet": 5,
                                "salty": 5,
                                "sour": 5,
                                "umami": 5
                            }
                        }
                    }
            except Exception as json_error:
                self.logger.error(f"JSON parsing error: {str(json_error)}")
                return {"success": False, "error": f"Failed to parse response: {str(json_error)}"}
            
        except Exception as e:
            self.logger.error(f"Recipe generation error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def explain_culinary_concept(self, query: str, language: str = "en") -> Dict[str, Any]:
        """Explain culinary concepts using Gemini 2.0 Flash"""
        try:
            if not self.gemini_client:
                # Return mock data for development when API key is not available
                self.logger.info("Using mock culinary explanation (no API key configured)")
                return {
                    "success": True, 
                    "explanation": f"Mock explanation for '{query}':\n\n"
                                   f"1. Definition: {query} is a culinary term or technique.\n"
                                   f"2. Techniques: Various methods are used in {query}.\n"
                                   f"3. Science: The science behind {query} involves chemical reactions.\n"
                                   f"4. Applications: {query} is commonly used in various cuisines.\n"
                                   f"5. Tips: Start with simple recipes to master {query}.\n"
                                   f"6. Related concepts: Similar techniques include variations of {query}."
                }
            
            prompt = f"""
            Provide a comprehensive culinary explanation for: {query}
            
            Include:
            1. Definition and explanation
            2. Techniques involved
            3. Science behind it (if applicable)
            4. Common applications
            5. Tips for beginners
            6. Related concepts
            
            Respond in {language} language.
            Make it educational but accessible.
            """
            
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(prompt)
            
            # Safely handle the response text
            try:
                response_text = response.text.strip()
                # Check if the response is HTML (common error case)
                if response_text.startswith('<!DOCTYPE') or response_text.startswith('<html'):
                    self.logger.error("Received HTML response instead of text")
                    return {"success": False, "error": "Received invalid response format"}
                
                return {"success": True, "explanation": response_text}
            except Exception as text_error:
                self.logger.error(f"Response processing error: {str(text_error)}")
                return {"success": False, "error": f"Failed to process response: {str(text_error)}"}
            
        except Exception as e:
            self.logger.error(f"Culinary explanation error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def suggest_ingredient_substitution(self, ingredient: str, context: str = "", 
                                           language: str = "en") -> Dict[str, Any]:
        """Suggest ingredient substitutions using Gemini 2.0 Flash-Lite"""
        try:
            if not self.gemini_client:
                # Return mock data for development when API key is not available
                self.logger.info("Using mock ingredient substitution (no API key configured)")
                return {
                    "success": True, 
                    "data": {
                        "substitutions": [
                            {
                                "alternative": f"Alternative to {ingredient}",
                                "ratio": "1:1",
                                "flavor_impact": "Similar flavor profile",
                                "texture_changes": "Minimal texture difference",
                                "availability": "Common"
                            },
                            {
                                "alternative": f"Another option for {ingredient}",
                                "ratio": "1.5:1",
                                "flavor_impact": "Slightly different flavor",
                                "texture_changes": "May be more firm/soft",
                                "availability": "Common"
                            }
                        ]
                    }
                }
            
            prompt = f"""
            Suggest substitutions for ingredient: {ingredient}
            Recipe context: {context}
            
            For each substitution, provide:
            1. Alternative ingredient
            2. Quantity ratio (e.g., 1:1, 2:1)
            3. Flavor impact
            4. Texture changes
            5. Nutritional differences
            6. Availability/cost considerations
            
            Format as JSON:
            {{
                "original_ingredient": "{ingredient}",
                "substitutions": [
                    {{
                        "alternative": "substitute name",
                        "ratio": "1:1",
                        "flavor_impact": "description",
                        "texture_impact": "description",
                        "nutritional_notes": "notes",
                        "availability": "Common/Rare",
                        "best_for": "specific use cases"
                    }}
                ]
            }}
            
            Respond in {language} language.
            """
            
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(prompt)
            
            # Extract JSON from response
            try:
                # Try to find JSON in the response text
                response_text = response.text.strip()
                # Check if the response is HTML (common error case)
                if response_text.startswith('<!DOCTYPE') or response_text.startswith('<html'):
                    self.logger.error("Received HTML response instead of text")
                    return {"success": False, "error": "Received invalid response format"}
                
                # Look for JSON-like structure
                json_start = response_text.find('{')
                json_end = response_text.rfind('}')
                
                if json_start >= 0 and json_end > json_start:
                    json_str = response_text[json_start:json_end+1]
                    substitution_data = json.loads(json_str)
                    return {"success": True, "data": substitution_data}
                else:
                    # If no JSON found, create a basic structure
                    self.logger.warning("No JSON found in response, creating structured response")
                    return {
                        "success": True, 
                        "data": {
                            "original_ingredient": ingredient,
                            "substitutions": [
                                {
                                    "alternative": "Could not parse alternatives",
                                    "ratio": "1:1",
                                    "flavor_impact": response_text,
                                    "texture_impact": "Unknown",
                                    "nutritional_notes": "Unknown",
                                    "availability": "Unknown"
                                }
                            ]
                        }
                    }
            except Exception as json_error:
                self.logger.error(f"JSON parsing error: {str(json_error)}")
                return {"success": False, "error": f"Failed to parse response: {str(json_error)}"}
            
        except Exception as e:
            self.logger.error(f"Substitution suggestion error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def analyze_flavor_profile(self, recipe_text: str, language: str = "en") -> Dict[str, Any]:
        """Analyze flavor profile using Gemini 2.0 Flash"""
        try:
            prompt = f"""
            Analyze the flavor profile of this recipe: {recipe_text}
            
            Provide analysis as JSON:
            {{
                "flavor_scores": {{
                    "spicy": 0-10,
                    "sweet": 0-10,
                    "salty": 0-10,
                    "sour": 0-10,
                    "umami": 0-10,
                    "bitter": 0-10
                }},
                "dominant_flavors": ["flavor1", "flavor2"],
                "flavor_description": "overall taste description",
                "complementary_dishes": ["dish1", "dish2", "dish3"],
                "wine_pairings": ["wine1", "wine2"],
                "enhancement_suggestions": ["suggestion1", "suggestion2"],
                "cuisine_style": "cuisine classification"
            }}
            
            Respond in {language} language.
            """
            
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(prompt)
            
            # Extract JSON from response
            try:
                # Try to find JSON in the response text
                response_text = response.text.strip()
                # Check if the response is HTML (common error case)
                if response_text.startswith('<!DOCTYPE') or response_text.startswith('<html'):
                    self.logger.error("Received HTML response instead of text")
                    return {"success": False, "error": "Received invalid response format"}
                
                # Look for JSON-like structure
                json_start = response_text.find('{')
                json_end = response_text.rfind('}')
                
                if json_start >= 0 and json_end > json_start:
                    json_str = response_text[json_start:json_end+1]
                    flavor_data = json.loads(json_str)
                    return {"success": True, "data": flavor_data}
                else:
                    # If no JSON found, create a basic structure
                    self.logger.warning("No JSON found in response, creating structured response")
                    return {
                        "success": True, 
                        "data": {
                            "flavor_scores": {
                                "spicy": 5,
                                "sweet": 5,
                                "salty": 5,
                                "sour": 5,
                                "umami": 5,
                                "bitter": 5
                            },
                            "dominant_flavors": ["Could not analyze"],
                            "flavor_description": response_text,
                            "complementary_dishes": ["Could not determine"],
                            "wine_pairings": ["Could not determine"],
                            "enhancement_suggestions": ["Could not determine"],
                            "cuisine_style": "Unknown"
                        }
                    }
            except Exception as json_error:
                self.logger.error(f"JSON parsing error: {str(json_error)}")
                return {"success": False, "error": f"Failed to parse response: {str(json_error)}"}
            
        except Exception as e:
            self.logger.error(f"Flavor analysis error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _get_mock_shopping_list(self):
        """Return mock shopping list data"""
        return {
            "success": True,
            "data": {
                "categories": {
                    "Produce": ["Onions", "Garlic", "Tomatoes", "Lettuce", "Carrots"],
                    "Meat & Seafood": ["Chicken breast", "Ground beef", "Salmon fillet"],
                    "Dairy": ["Milk", "Eggs", "Cheese", "Butter"],
                    "Pantry": ["Rice", "Pasta", "Flour", "Sugar", "Olive oil"],
                    "Spices & Seasonings": ["Salt", "Pepper", "Basil", "Oregano"]
                },
                "total_items": 20,
                "estimated_cost": "$30-$40"
            }
        }
    
    async def generate_shopping_list(self, recipes: list, language: str = "en") -> Dict[str, Any]:
        """Generate shopping list using Ollama with granite3.1-moe:1b model"""
        try:
            recipes_text = "\n\n".join([f"Recipe {i+1}: {recipe}" for i, recipe in enumerate(recipes)])
            
            prompt = f"""
            Generate a structured shopping list from these recipes:
            {recipes_text}
            
            Organize by category and combine similar items.
            Format as JSON:
            {{
                "categories": {{
                    "Produce": ["item1", "item2"],
                    "Meat & Seafood": ["item1", "item2"],
                    "Dairy": ["item1", "item2"],
                    "Pantry": ["item1", "item2"],
                    "Spices & Seasonings": ["item1", "item2"]
                }},
                "total_items": count,
                "estimated_cost": "price_range"
            }}
            
            Language: {language}
            """
            
            # Use Ollama with granite3.1-moe:1b model
            try:
                self.logger.info("Using Ollama with granite3.1-moe:1b model")
                import ollama
                import re
                
                # Create message for Ollama
                response = ollama.chat(
                    model='granite3.1-moe:1b',
                    messages=[{'role': 'user', 'content': prompt}],
                    options={
                        'temperature': 0.3,
                        'num_predict': 1000,
                    }
                )
                
                # Get the response text
                response_text = response['message']['content']
                
                # Parse the JSON response
                try:
                    # Extract JSON from the response text (it might contain additional text)
                    json_match = re.search(r'\{[\s\S]*\}', response_text)
                    if json_match:
                        response_text = json_match.group(0)
                        
                    shopping_data = json.loads(response_text)
                    self.logger.info("Successfully generated shopping list using Ollama model")
                    return {"success": True, "data": shopping_data}
                except json.JSONDecodeError as json_err:
                    self.logger.error(f"JSON parsing error from model: {str(json_err)}")
                    # Fall back to mock data if JSON parsing fails
                    self.logger.info("Falling back to mock shopping list data due to JSON parsing error")
                    return self._get_mock_shopping_list()
                    
            except ImportError as e:
                self.logger.error(f"Failed to import required libraries for Ollama: {str(e)}")
                # Fall back to mock data if imports fail
                self.logger.info("Falling back to mock shopping list data due to import error")
                return self._get_mock_shopping_list()
            except Exception as model_err:
                self.logger.error(f"Error using model: {str(model_err)}")
                # Fall back to mock data if model usage fails
                self.logger.info("Falling back to mock shopping list data due to model error")
                return self._get_mock_shopping_list()
                
        except Exception as e:
            self.logger.error(f"Shopping list generation error: {str(e)}")
            # Return mock data as fallback
            return self._get_mock_shopping_list()
    
    async def translate_content(self, content: str, target_language: str) -> Dict[str, Any]:
        """Translate content using Gemini 2.0 Flash"""
        try:
            prompt = f"""
            Translate the following content to {target_language}:
            
            {content}
            
            Maintain the original structure and formatting.
            If the content is already in {target_language}, return it as-is.
            """
            
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(prompt)
            
            # Safely handle the response text
            try:
                response_text = response.text.strip()
                # Check if the response is HTML (common error case)
                if response_text.startswith('<!DOCTYPE') or response_text.startswith('<html'):
                    self.logger.error("Received HTML response instead of text")
                    return {"success": False, "error": "Received invalid response format"}
                
                return {"success": True, "translated_text": response_text}
            except Exception as text_error:
                self.logger.error(f"Response processing error: {str(text_error)}")
                return {"success": False, "error": f"Failed to process response: {str(text_error)}"}
            
        except Exception as e:
            self.logger.error(f"Translation error: {str(e)}")
            return {"success": False, "error": str(e)}

# Global AI client instance
ai_client = AIClient()
