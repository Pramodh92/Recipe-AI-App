// Recipe-specific JavaScript functionality
class RecipeGenerator {
    constructor() {
        this.currentRecipe = null;
        this.flavorChart = null;
        this.init();
    }

    init() {
        this.setupFormValidation();
        this.setupEventListeners();
    }

    setupFormValidation() {
        const form = document.getElementById('recipeGeneratorForm');
        if (form) {
            form.addEventListener('submit', this.handleFormSubmit.bind(this));
        }
    }

    setupEventListeners() {
        // Save generated recipe
        const saveBtn = document.getElementById('saveGeneratedRecipe');
        if (saveBtn) {
            saveBtn.addEventListener('click', this.saveCurrentRecipe.bind(this));
        }

        // Generate shopping list
        const shoppingBtn = document.getElementById('generateShoppingList');
        if (shoppingBtn) {
            shoppingBtn.addEventListener('click', this.generateShoppingList.bind(this));
        }

        // Analyze flavor profile
        const flavorBtn = document.getElementById('analyzeFlavorProfile');
        if (flavorBtn) {
            flavorBtn.addEventListener('click', this.analyzeFlavorProfile.bind(this));
        }

        // Ingredient suggestion
        this.setupIngredientSuggestions();
    }

    setupIngredientSuggestions() {
        const ingredientsInput = document.getElementById('ingredients');
        if (ingredientsInput) {
            // Add ingredient suggestions/autocomplete
            ingredientsInput.addEventListener('input', this.debounce(this.suggestIngredients.bind(this), 300));
        }
    }

    async handleFormSubmit(e) {
        e.preventDefault();
        
        if (!this.validateForm()) {
            return;
        }

        const formData = new FormData(e.target);
        const ingredients = formData.get('ingredients');
        const cuisine = formData.get('cuisine');
        const servings = formData.get('servings');
        const dietaryRestrictions = this.getDietaryRestrictions();
        const additionalRestrictions = formData.get('additionalRestrictions');

        // Combine dietary restrictions
        const allRestrictions = [...dietaryRestrictions];
        if (additionalRestrictions) {
            allRestrictions.push(additionalRestrictions);
        }

        try {
            RecipeApp.showLoading('Generating your recipe...', 'Our AI is creating something delicious for you!');

            const response = await fetch('/recipes/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(RecipeApp.authToken() ? { 'Authorization': `Bearer ${RecipeApp.authToken()}` } : {})
                },
                body: JSON.stringify({
                    ingredients: ingredients,
                    cuisine: cuisine,
                    servings: parseInt(servings),
                    dietary_restrictions: allRestrictions.join(', ')
                })
            });

            const data = await response.json();
            RecipeApp.hideLoading();

            if (data.success) {
                this.currentRecipe = data.recipe;
                this.displayRecipeResult(data.recipe);
            } else {
                RecipeApp.showAlert(data.message || 'Failed to generate recipe', 'error');
            }
        } catch (error) {
            RecipeApp.hideLoading();
            console.error('Recipe generation error:', error);
            RecipeApp.showAlert('Failed to generate recipe. Please try again.', 'error');
        }
    }

    validateForm() {
        const ingredients = document.getElementById('ingredients').value.trim();
        
        if (!ingredients) {
            RecipeApp.showAlert('Please enter at least one ingredient', 'warning');
            return false;
        }

        if (ingredients.length < 10) {
            RecipeApp.showAlert('Please provide more detailed ingredient information', 'warning');
            return false;
        }

        return true;
    }

    getDietaryRestrictions() {
        const checkboxes = document.querySelectorAll('input[name="dietary[]"]:checked');
        return Array.from(checkboxes).map(cb => cb.value);
    }

    displayRecipeResult(recipe) {
        const modal = document.getElementById('recipeResultModal');
        const body = document.getElementById('recipeResultBody');

        if (!body) return;

        body.innerHTML = `
            <div class="recipe-result">
                <div class="row mb-4">
                    <div class="col-md-8">
                        <h2 class="mb-3">${this.sanitizeHtml(recipe.title)}</h2>
                        <div class="recipe-badges mb-3">
                            ${recipe.cuisine ? `<span class="badge bg-primary me-2"><i class="fas fa-globe me-1"></i>${recipe.cuisine}</span>` : ''}
                            ${recipe.difficulty ? `<span class="badge bg-info me-2"><i class="fas fa-chart-line me-1"></i>${recipe.difficulty}</span>` : ''}
                            ${recipe.cooking_time ? `<span class="badge bg-success me-2"><i class="fas fa-clock me-1"></i>${recipe.cooking_time} min</span>` : ''}
                            ${recipe.servings ? `<span class="badge bg-warning"><i class="fas fa-users me-1"></i>${recipe.servings} servings</span>` : ''}
                        </div>
                    </div>
                    <div class="col-md-4 text-md-end">
                        <div class="recipe-stats">
                            <div class="d-flex justify-content-end align-items-center">
                                <div class="rating-display me-3">
                                    ${this.generateStarRating(0)}
                                    <small class="text-muted ms-1">New Recipe</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="row">
                    <div class="col-lg-6">
                        <div class="ingredients-section">
                            <h4 class="mb-3">
                                <i class="fas fa-list-ul text-success me-2"></i>
                                Ingredients
                            </h4>
                            <div class="ingredients-list">
                                ${recipe.ingredients.map(ingredient => `
                                    <div class="ingredient-item d-flex align-items-center mb-2">
                                        <div class="form-check">
                                            <input class="form-check-input" type="checkbox" id="ingredient-${this.generateId()}">
                                            <label class="form-check-label">
                                                ${this.sanitizeHtml(ingredient)}
                                            </label>
                                        </div>
                                        <button class="btn btn-sm btn-outline-secondary ms-auto" onclick="recipeGenerator.substituteIngredient('${ingredient}')">
                                            <i class="fas fa-exchange-alt"></i>
                                        </button>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    </div>

                    <div class="col-lg-6">
                        <div class="instructions-section">
                            <h4 class="mb-3">
                                <i class="fas fa-list-ol text-primary me-2"></i>
                                Instructions
                            </h4>
                            <div class="instructions-list">
                                ${recipe.instructions.map((instruction, index) => `
                                    <div class="instruction-item mb-3">
                                        <div class="d-flex">
                                            <div class="step-number bg-primary text-white rounded-circle d-flex align-items-center justify-content-center me-3" style="width: 30px; height: 30px; font-weight: bold;">
                                                ${index + 1}
                                            </div>
                                            <div class="step-content flex-grow-1">
                                                <p class="mb-0">${this.sanitizeHtml(instruction)}</p>
                                            </div>
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                </div>

                ${recipe.flavor_profile ? `
                    <div class="row mt-4">
                        <div class="col-12">
                            <div class="flavor-preview card bg-light">
                                <div class="card-body">
                                    <h5 class="card-title">
                                        <i class="fas fa-palette text-info me-2"></i>
                                        Flavor Profile Preview
                                    </h5>
                                    <div class="flavor-tags">
                                        ${this.generateFlavorTags(recipe.flavor_profile)}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                ` : ''}

                <div class="row mt-4">
                    <div class="col-12">
                        <div class="recipe-actions d-flex gap-2 flex-wrap">
                            <button class="btn btn-outline-primary" onclick="recipeGenerator.printRecipe()">
                                <i class="fas fa-print me-1"></i>Print Recipe
                            </button>
                            <button class="btn btn-outline-success" onclick="recipeGenerator.shareRecipe()">
                                <i class="fas fa-share me-1"></i>Share
                            </button>
                            <button class="btn btn-outline-warning" onclick="recipeGenerator.addToMealPlan()">
                                <i class="fas fa-calendar-plus me-1"></i>Add to Meal Plan
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }

    async saveCurrentRecipe() {
        if (!this.currentRecipe) {
            RecipeApp.showAlert('No recipe to save', 'warning');
            return;
        }

        if (!RecipeApp.authToken()) {
            RecipeApp.showAlert('Please login to save recipes', 'warning');
            return;
        }

        try {
            // First check if we need to create a new recipe or save an existing one
            const isNewRecipe = !this.currentRecipe.id;
            
            let endpoint = isNewRecipe ? '/recipes/create' : '/recipes/save';
            let payload = isNewRecipe ? 
                this.currentRecipe : 
                { recipe_id: this.currentRecipe.id };
            
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${RecipeApp.authToken()}`
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (data.success) {
                RecipeApp.showAlert('Recipe saved successfully!', 'success');
                
                // Update save button
                const saveBtn = document.getElementById('saveGeneratedRecipe');
                if (saveBtn) {
                    saveBtn.innerHTML = '<i class="fas fa-heart me-1"></i>Saved';
                    saveBtn.classList.remove('btn-success');
                    saveBtn.classList.add('btn-outline-success');
                    saveBtn.disabled = true;
                }
            } else {
                RecipeApp.showAlert(data.message || 'Failed to save recipe', 'error');
            }
        } catch (error) {
            console.error('Save recipe error:', error);
            RecipeApp.showAlert('Failed to save recipe', 'error');
        }
    }

    async generateShoppingList() {
        if (!this.currentRecipe) {
            RecipeApp.showAlert('No recipe available for shopping list', 'warning');
            return;
        }

        try {
            RecipeApp.showLoading('Generating shopping list...');

            const response = await fetch('/ai/shopping-list', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(RecipeApp.authToken() ? { 'Authorization': `Bearer ${RecipeApp.authToken()}` } : {})
                },
                body: JSON.stringify({
                    recipes: [this.formatRecipeForShoppingList(this.currentRecipe)],
                    name: `Shopping List for ${this.currentRecipe.title}`
                })
            });

            const data = await response.json();
            RecipeApp.hideLoading();

            if (data.success) {
                this.displayShoppingList(data.shopping_list);
            } else {
                RecipeApp.showAlert('Failed to generate shopping list', 'error');
            }
        } catch (error) {
            RecipeApp.hideLoading();
            console.error('Shopping list error:', error);
            RecipeApp.showAlert('Failed to generate shopping list', 'error');
        }
    }

    async analyzeFlavorProfile() {
        if (!this.currentRecipe) {
            RecipeApp.showAlert('No recipe available for analysis', 'warning');
            return;
        }

        try {
            RecipeApp.showLoading('Analyzing flavor profile...');

            const recipeText = this.formatRecipeForAnalysis(this.currentRecipe);
            const response = await fetch('/ai/flavor-profile', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(RecipeApp.authToken() ? { 'Authorization': `Bearer ${RecipeApp.authToken()}` } : {})
                },
                body: JSON.stringify({
                    recipe_text: recipeText
                })
            });

            const data = await response.json();
            RecipeApp.hideLoading();

            if (data.success) {
                this.displayFlavorAnalysis(data.analysis);
            } else {
                RecipeApp.showAlert('Failed to analyze flavor profile', 'error');
            }
        } catch (error) {
            RecipeApp.hideLoading();
            console.error('Flavor analysis error:', error);
            RecipeApp.showAlert('Failed to analyze flavor profile', 'error');
        }
    }

    async substituteIngredient(ingredient) {
        try {
            RecipeApp.showLoading('Finding substitutes...');

            const response = await fetch('/ai/substitute-ingredient', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(RecipeApp.authToken() ? { 'Authorization': `Bearer ${RecipeApp.authToken()}` } : {})
                },
                body: JSON.stringify({
                    ingredient: ingredient,
                    context: this.currentRecipe ? this.currentRecipe.title : ''
                })
            });

            const data = await response.json();
            RecipeApp.hideLoading();

            if (data.success) {
                this.displaySubstitutionSuggestions(ingredient, data.substitutions);
            } else {
                RecipeApp.showAlert('Failed to find substitutes', 'error');
            }
        } catch (error) {
            RecipeApp.hideLoading();
            console.error('Substitution error:', error);
            RecipeApp.showAlert('Failed to find substitutes', 'error');
        }
    }

    displayFlavorAnalysis(analysis) {
        const modal = document.getElementById('flavorProfileModal');
        const analysisDiv = document.getElementById('flavorAnalysis');

        // Create radar chart
        this.createFlavorChart(analysis.flavor_scores);

        // Display additional analysis
        analysisDiv.innerHTML = `
            <div class="flavor-analysis">
                <div class="row">
                    <div class="col-md-6">
                        <h6>Dominant Flavors</h6>
                        <div class="dominant-flavors">
                            ${analysis.dominant_flavors.map(flavor => `
                                <span class="badge bg-primary me-2 mb-2">${flavor}</span>
                            `).join('')}
                        </div>
                    </div>
                    <div class="col-md-6">
                        <h6>Cuisine Style</h6>
                        <p class="mb-2">${analysis.cuisine_style}</p>
                    </div>
                </div>
                
                <div class="row mt-3">
                    <div class="col-12">
                        <h6>Flavor Description</h6>
                        <p>${analysis.flavor_description}</p>
                    </div>
                </div>
                
                <div class="row mt-3">
                    <div class="col-md-6">
                        <h6>Wine Pairings</h6>
                        <ul class="list-unstyled">
                            ${analysis.wine_pairings.map(wine => `<li><i class="fas fa-wine-glass me-2"></i>${wine}</li>`).join('')}
                        </ul>
                    </div>
                    <div class="col-md-6">
                        <h6>Complementary Dishes</h6>
                        <ul class="list-unstyled">
                            ${analysis.complementary_dishes.map(dish => `<li><i class="fas fa-utensils me-2"></i>${dish}</li>`).join('')}
                        </ul>
                    </div>
                </div>
                
                <div class="row mt-3">
                    <div class="col-12">
                        <h6>Enhancement Suggestions</h6>
                        <ul class="list-unstyled">
                            ${analysis.enhancement_suggestions.map(suggestion => `<li><i class="fas fa-lightbulb me-2"></i>${suggestion}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            </div>
        `;

        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }

    createFlavorChart(flavorScores) {
        const ctx = document.getElementById('flavorChart');
        
        if (this.flavorChart) {
            this.flavorChart.destroy();
        }

        this.flavorChart = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: Object.keys(flavorScores).map(key => 
                    key.charAt(0).toUpperCase() + key.slice(1)
                ),
                datasets: [{
                    label: 'Flavor Intensity',
                    data: Object.values(flavorScores),
                    fill: true,
                    backgroundColor: 'rgba(0, 123, 255, 0.2)',
                    borderColor: 'rgba(0, 123, 255, 1)',
                    pointBackgroundColor: 'rgba(0, 123, 255, 1)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(0, 123, 255, 1)'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 10,
                        ticks: {
                            stepSize: 2
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    displaySubstitutionSuggestions(originalIngredient, substitutions) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-exchange-alt me-2"></i>
                            Substitutes for ${originalIngredient}
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="substitutions-list">
                            ${substitutions.substitutions.map(sub => `
                                <div class="substitution-item card mb-3">
                                    <div class="card-body">
                                        <h6 class="card-title">${sub.alternative}</h6>
                                        <div class="row">
                                            <div class="col-md-6">
                                                <p><strong>Ratio:</strong> ${sub.ratio}</p>
                                                <p><strong>Availability:</strong> ${sub.availability}</p>
                                            </div>
                                            <div class="col-md-6">
                                                <p><strong>Best for:</strong> ${sub.best_for}</p>
                                            </div>
                                        </div>
                                        <div class="impact-details">
                                            <p><strong>Flavor Impact:</strong> ${sub.flavor_impact}</p>
                                            <p><strong>Texture Impact:</strong> ${sub.texture_impact}</p>
                                            ${sub.nutritional_notes ? `<p><strong>Nutritional Notes:</strong> ${sub.nutritional_notes}</p>` : ''}
                                        </div>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();

        // Clean up modal after hiding
        modal.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(modal);
        });
    }

    // Helper methods
    generateStarRating(rating) {
        let stars = '';
        for (let i = 1; i <= 5; i++) {
            if (i <= rating) {
                stars += '<i class="fas fa-star text-warning"></i>';
            } else {
                stars += '<i class="far fa-star text-muted"></i>';
            }
        }
        return stars;
    }

    generateFlavorTags(flavorProfile) {
        const tags = [];
        for (const [flavor, intensity] of Object.entries(flavorProfile)) {
            if (intensity > 5) {
                const colorClass = this.getFlavorColor(flavor);
                tags.push(`<span class="badge ${colorClass} me-2 mb-2">${flavor} (${intensity}/10)</span>`);
            }
        }
        return tags.join('');
    }

    getFlavorColor(flavor) {
        const colors = {
            spicy: 'bg-danger',
            sweet: 'bg-warning',
            salty: 'bg-info',
            sour: 'bg-success',
            umami: 'bg-primary',
            bitter: 'bg-dark'
        };
        return colors[flavor.toLowerCase()] || 'bg-secondary';
    }

    formatRecipeForShoppingList(recipe) {
        return `${recipe.title}\nIngredients: ${recipe.ingredients.join(', ')}`;
    }
    
    displayShoppingList(shoppingList) {
        const resultsContainer = document.getElementById('shoppingListResults');
        if (!resultsContainer) {
            console.error('Shopping list results container not found');
            return;
        }
        
        // Show the results container
        resultsContainer.style.display = 'flex';
        
        // Find the shopping list content container
        const shoppingListContent = document.getElementById('shoppingListContent');
        if (!shoppingListContent) {
            console.error('Shopping list content container not found');
            return;
        }
        
        // Generate the shopping list HTML
        let shoppingListHtml = '';
        
        // Add categories and items
        Object.entries(shoppingList.categories).forEach(([category, items]) => {
            const categoryIcon = this.getCategoryIcon(category);
            
            shoppingListHtml += `
                <div class="category-section p-3 border-bottom">
                    <h6 class="category-header bg-light p-2 rounded">
                        <i class="fas fa-${categoryIcon} me-2"></i>
                        ${category}
                    </h6>
                    <div class="items-list mt-2">
                        ${items.map(item => `
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="item-${this.generateId()}">
                                <label class="form-check-label">
                                    ${item}
                                </label>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        });
        
        // Update the shopping list content
        shoppingListContent.innerHTML = shoppingListHtml;
        
        // Update summary information
        document.getElementById('totalItems').textContent = shoppingList.total_items;
        document.getElementById('estimatedCost').textContent = shoppingList.estimated_cost;
        
        // Reset shopping progress
        document.getElementById('shoppingProgress').style.width = '0%';
        
        // Add event listeners to checkboxes for progress tracking
        this.setupShoppingListCheckboxes();
        
        // Scroll to the results
        resultsContainer.scrollIntoView({ behavior: 'smooth' });
    }
    
    setupShoppingListCheckboxes() {
        const checkboxes = document.querySelectorAll('#shoppingListContent .form-check-input');
        const progressBar = document.getElementById('shoppingProgress');
        
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                // Calculate progress percentage
                const totalItems = checkboxes.length;
                const checkedItems = document.querySelectorAll('#shoppingListContent .form-check-input:checked').length;
                const progressPercentage = Math.round((checkedItems / totalItems) * 100);
                
                // Update progress bar
                progressBar.style.width = `${progressPercentage}%`;
            });
        });
    }
    
    getCategoryIcon(category) {
        const icons = {
            'produce': 'carrot',
            'dairy': 'cheese',
            'meat & seafood': 'drumstick-bite',
            'bakery': 'bread-slice',
            'pantry': 'box',
            'frozen': 'snowflake',
            'beverages': 'wine-bottle',
            'spices & seasonings': 'pepper-hot',
            'canned goods': 'can-food',
            'snacks': 'cookie',
            'condiments': 'bottle-droplet'
        };
        
        return icons[category.toLowerCase()] || 'shopping-basket';
    }

    formatRecipeForAnalysis(recipe) {
        return `Recipe: ${recipe.title}\nIngredients: ${recipe.ingredients.join(', ')}\nInstructions: ${recipe.instructions.join(' ')}`;
    }

    generateId() {
        return Math.random().toString(36).substr(2, 9);
    }

    sanitizeHtml(str) {
        const temp = document.createElement('div');
        temp.textContent = str;
        return temp.innerHTML;
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    async suggestIngredients(event) {
        // Future enhancement: implement ingredient autocomplete
        // This could connect to a food database API
    }

    // Recipe actions
    printRecipe() {
        if (!this.currentRecipe) return;
        
        const printWindow = window.open('', '_blank');
        printWindow.document.write(`
            <html>
                <head>
                    <title>${this.currentRecipe.title}</title>
                    <style>
                        body { font-family: Arial, sans-serif; padding: 20px; }
                        .recipe-header { border-bottom: 2px solid #333; padding-bottom: 10px; margin-bottom: 20px; }
                        .ingredients, .instructions { margin-bottom: 20px; }
                        .ingredients ul, .instructions ol { padding-left: 20px; }
                        .badge { background: #007bff; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px; }
                        @media print { body { font-size: 12pt; } }
                    </style>
                </head>
                <body>
                    <div class="recipe-header">
                        <h1>${this.currentRecipe.title}</h1>
                        <div class="meta">
                            ${this.currentRecipe.cuisine ? `<span class="badge">Cuisine: ${this.currentRecipe.cuisine}</span> ` : ''}
                            ${this.currentRecipe.cooking_time ? `<span class="badge">Time: ${this.currentRecipe.cooking_time} min</span> ` : ''}
                            ${this.currentRecipe.servings ? `<span class="badge">Servings: ${this.currentRecipe.servings}</span> ` : ''}
                            ${this.currentRecipe.difficulty ? `<span class="badge">Difficulty: ${this.currentRecipe.difficulty}</span>` : ''}
                        </div>
                    </div>
                    <div class="ingredients">
                        <h2>Ingredients</h2>
                        <ul>
                            ${this.currentRecipe.ingredients.map(ingredient => `<li>${ingredient}</li>`).join('')}
                        </ul>
                    </div>
                    <div class="instructions">
                        <h2>Instructions</h2>
                        <ol>
                            ${this.currentRecipe.instructions.map(instruction => `<li>${instruction}</li>`).join('')}
                        </ol>
                    </div>
                </body>
            </html>
        `);
        printWindow.document.close();
        printWindow.print();
    }

    shareRecipe() {
        if (!this.currentRecipe) return;
        
        if (navigator.share) {
            navigator.share({
                title: this.currentRecipe.title,
                text: `Check out this AI-generated recipe: ${this.currentRecipe.title}`,
                url: window.location.href
            });
        } else {
            // Fallback to clipboard
            const recipeText = `${this.currentRecipe.title}\n\nIngredients:\n${this.currentRecipe.ingredients.map(ing => `• ${ing}`).join('\n')}\n\nInstructions:\n${this.currentRecipe.instructions.map((inst, i) => `${i+1}. ${inst}`).join('\n')}`;
            
            navigator.clipboard.writeText(recipeText).then(() => {
                RecipeApp.showAlert('Recipe copied to clipboard!', 'success');
            });
        }
    }

    addToMealPlan() {
        if (!RecipeApp.authToken()) {
            RecipeApp.showAlert('Please login to add recipes to meal plan', 'warning');
            return;
        }
        
        // Redirect to meal planner with recipe data
        const recipeData = encodeURIComponent(JSON.stringify(this.currentRecipe));
        window.location.href = `/meal-planner?recipe=${recipeData}`;
    }
}

// Initialize recipe generator when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.recipeGenerator = new RecipeGenerator();
});
