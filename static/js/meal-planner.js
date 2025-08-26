// Meal Planner functionality
class MealPlanner {
    constructor() {
        this.currentWeek = this.getWeekStart(new Date());
        this.mealPlan = {};
        this.recipes = [];
        this.init();
    }

    init() {
        this.loadMealPlan();
        this.loadSavedRecipes();
        this.setupEventListeners();
        this.setupDragAndDrop();
        this.renderCalendar();
        
        // Check for recipe parameter from URL
        this.checkForRecipeParameter();
    }

    setupEventListeners() {
        // Week navigation
        const prevWeekBtn = document.getElementById('prevWeek');
        const nextWeekBtn = document.getElementById('nextWeek');
        const todayBtn = document.getElementById('todayBtn');

        if (prevWeekBtn) {
            prevWeekBtn.addEventListener('click', () => {
                this.currentWeek = new Date(this.currentWeek.getTime() - 7 * 24 * 60 * 60 * 1000);
                this.loadMealPlan();
                this.renderCalendar();
            });
        }

        if (nextWeekBtn) {
            nextWeekBtn.addEventListener('click', () => {
                this.currentWeek = new Date(this.currentWeek.getTime() + 7 * 24 * 60 * 60 * 1000);
                this.loadMealPlan();
                this.renderCalendar();
            });
        }

        if (todayBtn) {
            todayBtn.addEventListener('click', () => {
                this.currentWeek = this.getWeekStart(new Date());
                this.loadMealPlan();
                this.renderCalendar();
            });
        }

        // Save meal plan
        const savePlanBtn = document.getElementById('saveMealPlan');
        if (savePlanBtn) {
            savePlanBtn.addEventListener('click', () => this.saveMealPlan());
        }

        // Generate shopping list
        const shoppingListBtn = document.getElementById('generateWeeklyShoppingList');
        if (shoppingListBtn) {
            shoppingListBtn.addEventListener('click', () => this.generateWeeklyShoppingList());
        }

        // Clear meal plan
        const clearPlanBtn = document.getElementById('clearMealPlan');
        if (clearPlanBtn) {
            clearPlanBtn.addEventListener('click', () => this.clearMealPlan());
        }
    }

    setupDragAndDrop() {
        // Enable dragging for recipe cards
        document.addEventListener('dragstart', (e) => {
            if (e.target.classList.contains('recipe-card-draggable')) {
                e.dataTransfer.setData('text/plain', JSON.stringify({
                    type: 'recipe',
                    data: JSON.parse(e.target.dataset.recipe)
                }));
            }
        });

        // Setup drop zones
        document.addEventListener('dragover', (e) => {
            if (e.target.classList.contains('meal-slot') || e.target.closest('.meal-slot')) {
                e.preventDefault();
            }
        });

        document.addEventListener('drop', (e) => {
            const mealSlot = e.target.classList.contains('meal-slot') ? 
                e.target : e.target.closest('.meal-slot');
            
            if (mealSlot) {
                e.preventDefault();
                const dragData = JSON.parse(e.dataTransfer.getData('text/plain'));
                
                if (dragData.type === 'recipe') {
                    this.addMealToSlot(mealSlot.dataset.day, mealSlot.dataset.meal, dragData.data);
                }
            }
        });
    }

    async loadSavedRecipes() {
        if (!RecipeApp.authToken()) {
            // For guest users, load mock recipes
            this.recipes = [
                { id: 'mock1', title: 'Chicken Stir Fry', cooking_time: 20, servings: 4, cuisine: 'chinese', ingredients: ['Chicken', 'Vegetables', 'Soy sauce'] },
                { id: 'mock2', title: 'Pasta Carbonara', cooking_time: 25, servings: 4, cuisine: 'italian', ingredients: ['Pasta', 'Eggs', 'Cheese', 'Bacon'] },
                { id: 'mock3', title: 'Vegetable Curry', cooking_time: 35, servings: 6, cuisine: 'indian', ingredients: ['Vegetables', 'Curry paste', 'Coconut milk'] },
                { id: 'mock4', title: 'Grilled Salmon', cooking_time: 15, servings: 2, cuisine: 'american', ingredients: ['Salmon', 'Lemon', 'Herbs'] }
            ];
            this.updateRecipeSuggestions();
            return;
        }

        try {
            const response = await fetch('/api/saved-recipes', {
                headers: {
                    'Authorization': `Bearer ${RecipeApp.authToken()}`
                }
            });

            const data = await response.json();
            
            if (data.success) {
                this.recipes = data.recipes || [];
                this.updateRecipeSuggestions();
            }
        } catch (error) {
            console.error('Load saved recipes error:', error);
            // Fall back to mock recipes
            this.recipes = [
                { id: 'mock1', title: 'Chicken Stir Fry', cooking_time: 20, servings: 4, cuisine: 'chinese', ingredients: ['Chicken', 'Vegetables', 'Soy sauce'] },
                { id: 'mock2', title: 'Pasta Carbonara', cooking_time: 25, servings: 4, cuisine: 'italian', ingredients: ['Pasta', 'Eggs', 'Cheese', 'Bacon'] }
            ];
            this.updateRecipeSuggestions();
        }
    }

    updateRecipeSuggestions() {
        const container = document.getElementById('recipeSuggestions');
        if (!container || !this.recipes.length) return;
        
        container.innerHTML = this.recipes.slice(0, 6).map(recipe => `
            <div class="recipe-suggestion-item mb-2">
                <div class="card card-sm recipe-card-draggable" draggable="true" data-recipe='${JSON.stringify(recipe)}'>
                    <div class="card-body p-2">
                        <h6 class="card-title mb-1">${recipe.title}</h6>
                        <small class="text-muted">${recipe.cooking_time} min • ${recipe.servings} servings</small>
                        <div class="mt-2">
                            <button class="btn btn-sm btn-primary" onclick="mealPlanner.showAddRecipeModal(${JSON.stringify(recipe).replace(/"/g, "'")})">                                
                                <i class="fas fa-plus me-1"></i>Add
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
        
        // Setup drag for new elements
        this.setupDragAndDrop();
    }
    
    async loadMealPlan() {
        if (!RecipeApp.authToken()) {
            this.renderGuestView();
            return;
        }

        try {
            const weekStart = this.formatDate(this.currentWeek);
            const response = await fetch(`/api/meal-plan?week_start=${weekStart}`, {
                headers: {
                    'Authorization': `Bearer ${RecipeApp.authToken()}`
                }
            });

            const data = await response.json();
            
            if (data.success) {
                this.mealPlan = data.meal_plan.plan || {};
            }
        } catch (error) {
            console.error('Load meal plan error:', error);
            RecipeApp.showAlert('Failed to load meal plan', 'error');
        }
    }

    async saveMealPlan() {
        if (!RecipeApp.authToken()) {
            RecipeApp.showAlert('Please login to save meal plans', 'warning');
            return;
        }

        try {
            RecipeApp.showLoading('Saving meal plan...');

            const response = await fetch('/meal-plan', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${RecipeApp.authToken()}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    week_start: this.formatDate(this.currentWeek),
                    plan: this.mealPlan
                })
            });

            const data = await response.json();
            RecipeApp.hideLoading();

            if (data.success) {
                RecipeApp.showAlert('Meal plan saved successfully!', 'success');
            } else {
                RecipeApp.showAlert('Failed to save meal plan', 'error');
            }
        } catch (error) {
            RecipeApp.hideLoading();
            console.error('Save meal plan error:', error);
            RecipeApp.showAlert('Failed to save meal plan', 'error');
        }
    }

    renderCalendar() {
        const calendarContainer = document.getElementById('mealPlanCalendar');
        if (!calendarContainer) return;

        const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
        const meals = ['breakfast', 'lunch', 'dinner'];

        // Update week display
        const weekDisplay = document.getElementById('currentWeek');
        if (weekDisplay) {
            const weekEnd = new Date(this.currentWeek.getTime() + 6 * 24 * 60 * 60 * 1000);
            weekDisplay.textContent = `${this.formatDisplayDate(this.currentWeek)} - ${this.formatDisplayDate(weekEnd)}`;
        }

        calendarContainer.innerHTML = `
            <div class="meal-plan-grid">
                <div class="meal-plan-header">
                    <div class="meal-header"></div>
                    ${days.map(day => `<div class="day-header">${day}</div>`).join('')}
                </div>
                
                ${meals.map(meal => `
                    <div class="meal-row">
                        <div class="meal-label">
                            <h6 class="mb-0">${meal.charAt(0).toUpperCase() + meal.slice(1)}</h6>
                        </div>
                        ${days.map(day => {
                            const dayKey = day.toLowerCase();
                            const mealData = this.mealPlan[dayKey] && this.mealPlan[dayKey][meal];
                            return `
                                <div class="meal-slot" 
                                     data-day="${dayKey}" 
                                     data-meal="${meal}"
                                     ondrop="drop(event)" 
                                     ondragover="allowDrop(event)">
                                    ${mealData ? this.renderMealCard(mealData) : this.renderEmptySlot()}
                                </div>
                            `;
                        }).join('')}
                    </div>
                `).join('')}
            </div>
        `;
    }

    renderMealCard(mealData) {
        return `
            <div class="meal-card">
                <div class="meal-card-header">
                    <h6 class="meal-title">${mealData.title}</h6>
                    <button class="btn btn-sm btn-outline-danger ms-auto" onclick="mealPlanner.removeMeal('${mealData.day}', '${mealData.meal}')">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="meal-card-body">
                    ${mealData.cooking_time ? `<small class="text-muted"><i class="fas fa-clock me-1"></i>${mealData.cooking_time} min</small>` : ''}
                    ${mealData.servings ? `<small class="text-muted ms-2"><i class="fas fa-users me-1"></i>${mealData.servings} servings</small>` : ''}
                </div>
                <div class="meal-card-actions">
                    <button class="btn btn-sm btn-outline-primary" onclick="mealPlanner.viewRecipe('${mealData.id}')">
                        <i class="fas fa-eye me-1"></i>View
                    </button>
                    <button class="btn btn-sm btn-outline-success" onclick="mealPlanner.cookMeal('${mealData.id}')">
                        <i class="fas fa-utensils me-1"></i>Cook
                    </button>
                </div>
            </div>
        `;
    }

    renderEmptySlot() {
        return `
            <div class="empty-meal-slot">
                <div class="empty-slot-content">
                    <i class="fas fa-plus text-muted mb-2"></i>
                    <p class="text-muted mb-0">Drop recipe here</p>
                </div>
            </div>
        `;
    }

    renderGuestView() {
        const calendarContainer = document.getElementById('mealPlanCalendar');
        if (!calendarContainer) return;

        calendarContainer.innerHTML = `
            <div class="guest-meal-planner text-center py-5">
                <i class="fas fa-calendar-alt fa-4x text-muted mb-4"></i>
                <h3>Plan Your Meals</h3>
                <p class="lead text-muted mb-4">
                    Create personalized weekly meal plans and generate smart shopping lists.
                </p>
                <a href="/auth/login" class="btn btn-primary btn-lg">
                    <i class="fas fa-sign-in-alt me-2"></i>Login to Start Planning
                </a>
            </div>
        `;
    }

    addMealToSlot(day, meal, recipeData) {
        if (!this.mealPlan[day]) {
            this.mealPlan[day] = {};
        }

        this.mealPlan[day][meal] = {
            id: recipeData.id,
            title: recipeData.title,
            cooking_time: recipeData.cooking_time,
            servings: recipeData.servings,
            ingredients: recipeData.ingredients,
            day: day,
            meal: meal
        };

        this.renderCalendar();
        
        // Auto-save after 2 seconds
        clearTimeout(this.autoSaveTimeout);
        this.autoSaveTimeout = setTimeout(() => {
            if (RecipeApp.authToken()) {
                this.saveMealPlan();
            }
        }, 2000);
    }

    removeMeal(day, meal) {
        if (this.mealPlan[day] && this.mealPlan[day][meal]) {
            delete this.mealPlan[day][meal];
            
            // Clean up empty day objects
            if (Object.keys(this.mealPlan[day]).length === 0) {
                delete this.mealPlan[day];
            }
            
            this.renderCalendar();
            
            // Auto-save
            clearTimeout(this.autoSaveTimeout);
            this.autoSaveTimeout = setTimeout(() => {
                if (RecipeApp.authToken()) {
                    this.saveMealPlan();
                }
            }, 1000);
        }
    }

    async generateWeeklyShoppingList() {
        if (!RecipeApp.authToken()) {
            RecipeApp.showAlert('Please login to generate shopping lists', 'warning');
            return;
        }

        const recipes = this.getWeeklyRecipes();
        if (recipes.length === 0) {
            RecipeApp.showAlert('No meals planned for this week', 'warning');
            return;
        }

        try {
            RecipeApp.showLoading('Generating weekly shopping list...');

            const response = await fetch('/ai/shopping-list', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${RecipeApp.authToken()}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    recipes: recipes.map(recipe => this.formatRecipeForShoppingList(recipe)),
                    name: `Weekly Shopping List - ${this.formatDisplayDate(this.currentWeek)}`
                })
            });

            const data = await response.json();
            RecipeApp.hideLoading();

            if (data.success) {
                this.displayShoppingListModal(data.shopping_list);
            } else {
                RecipeApp.showAlert('Failed to generate shopping list', 'error');
            }
        } catch (error) {
            RecipeApp.hideLoading();
            console.error('Shopping list error:', error);
            RecipeApp.showAlert('Failed to generate shopping list', 'error');
        }
    }

    displayShoppingListModal(shoppingList) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header bg-success text-white">
                        <h5 class="modal-title">
                            <i class="fas fa-shopping-cart me-2"></i>
                            Weekly Shopping List
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="shopping-list-content">
                            ${Object.entries(shoppingList.categories).map(([category, items]) => `
                                <div class="category-section mb-4">
                                    <h6 class="category-header bg-light p-2 rounded">
                                        <i class="fas fa-${this.getCategoryIcon(category)} me-2"></i>
                                        ${category}
                                    </h6>
                                    <div class="items-list">
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
                            `).join('')}
                        </div>
                        <div class="shopping-summary mt-4 p-3 bg-light rounded">
                            <div class="row">
                                <div class="col-md-6">
                                    <strong>Total Items: ${shoppingList.total_items}</strong>
                                </div>
                                <div class="col-md-6">
                                    <strong>Estimated Cost: ${shoppingList.estimated_cost}</strong>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Close</button>
                        <button type="button" class="btn btn-primary" onclick="mealPlanner.printShoppingList()">
                            <i class="fas fa-print me-1"></i>Print
                        </button>
                        <button type="button" class="btn btn-success" onclick="mealPlanner.exportShoppingList()">
                            <i class="fas fa-download me-1"></i>Export PDF
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        this.currentShoppingListModal = modal;
        
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();

        modal.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(modal);
        });
    }

    clearMealPlan() {
        if (confirm('Are you sure you want to clear all meals for this week?')) {
            this.mealPlan = {};
            this.renderCalendar();
            
            if (RecipeApp.authToken()) {
                this.saveMealPlan();
            }
            
            RecipeApp.showAlert('Meal plan cleared', 'success');
        }
    }

    checkForRecipeParameter() {
        const urlParams = new URLSearchParams(window.location.search);
        const recipeData = urlParams.get('recipe');
        
        if (recipeData) {
            try {
                const recipe = JSON.parse(decodeURIComponent(recipeData));
                this.showAddRecipeModal(recipe);
            } catch (error) {
                console.error('Error parsing recipe data:', error);
            }
        }
    }

    showAddRecipeModal(recipe) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Add Recipe to Meal Plan</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <h6>${recipe.title}</h6>
                        <p class="text-muted">Select when you want to prepare this recipe:</p>
                        
                        <div class="meal-selection">
                            <div class="mb-3">
                                <label for="selectDay" class="form-label">Day</label>
                                <select class="form-select" id="selectDay">
                                    <option value="monday">Monday</option>
                                    <option value="tuesday">Tuesday</option>
                                    <option value="wednesday">Wednesday</option>
                                    <option value="thursday">Thursday</option>
                                    <option value="friday">Friday</option>
                                    <option value="saturday">Saturday</option>
                                    <option value="sunday">Sunday</option>
                                </select>
                            </div>
                            
                            <div class="mb-3">
                                <label for="selectMeal" class="form-label">Meal</label>
                                <select class="form-select" id="selectMeal">
                                    <option value="breakfast">Breakfast</option>
                                    <option value="lunch">Lunch</option>
                                    <option value="dinner">Dinner</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" onclick="mealPlanner.addRecipeFromModal('${encodeURIComponent(JSON.stringify(recipe))}')">
                            Add to Meal Plan
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();

        modal.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(modal);
        });
    }

    addRecipeFromModal(recipeDataEncoded) {
        const recipe = JSON.parse(decodeURIComponent(recipeDataEncoded));
        const day = document.getElementById('selectDay').value;
        const meal = document.getElementById('selectMeal').value;
        
        this.addMealToSlot(day, meal, recipe);
        
        // Close modal
        const modal = document.querySelector('.modal.show');
        if (modal) {
            bootstrap.Modal.getInstance(modal).hide();
        }
        
        RecipeApp.showAlert(`${recipe.title} added to ${day} ${meal}`, 'success');
    }

    // Helper methods
    getWeekStart(date) {
        const d = new Date(date);
        const day = d.getDay();
        const diff = d.getDate() - day + (day === 0 ? -6 : 1); // Adjust when day is sunday
        return new Date(d.setDate(diff));
    }

    formatDate(date) {
        return date.toISOString().split('T')[0];
    }

    formatDisplayDate(date) {
        return date.toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric',
            year: 'numeric'
        });
    }

    getWeeklyRecipes() {
        const recipes = [];
        Object.values(this.mealPlan).forEach(day => {
            Object.values(day).forEach(meal => {
                recipes.push(meal);
            });
        });
        return recipes;
    }

    formatRecipeForShoppingList(recipe) {
        return `${recipe.title}\nIngredients: ${recipe.ingredients ? recipe.ingredients.join(', ') : 'N/A'}`;
    }

    getCategoryIcon(category) {
        const icons = {
            'Produce': 'apple-alt',
            'Meat & Seafood': 'drumstick-bite',
            'Dairy': 'cheese',
            'Pantry': 'boxes',
            'Spices & Seasonings': 'pepper-hot'
        };
        return icons[category] || 'shopping-basket';
    }

    generateId() {
        return Math.random().toString(36).substr(2, 9);
    }

    viewRecipe(recipeId) {
        // Implementation for viewing recipe details
        window.location.href = `/api/recipes/${recipeId}`;
    }

    cookMeal(recipeId) {
        // Implementation for cooking mode
        RecipeApp.showAlert('Cooking mode coming soon!', 'info');
    }

    printShoppingList() {
        if (!this.currentShoppingListModal) return;
        
        const shoppingContent = this.currentShoppingListModal.querySelector('.shopping-list-content').innerHTML;
        const printWindow = window.open('', '_blank');
        
        printWindow.document.write(`
            <html>
                <head>
                    <title>Weekly Shopping List</title>
                    <style>
                        body { font-family: Arial, sans-serif; padding: 20px; }
                        .category-section { margin-bottom: 20px; }
                        .category-header { background: #f8f9fa; padding: 8px; font-weight: bold; }
                        .form-check { margin: 5px 0; }
                        .form-check-input { margin-right: 8px; }
                        @media print { body { font-size: 12pt; } }
                    </style>
                </head>
                <body>
                    <h1>Weekly Shopping List</h1>
                    <p>Week of: ${this.formatDisplayDate(this.currentWeek)}</p>
                    ${shoppingContent}
                </body>
            </html>
        `);
        
        printWindow.document.close();
        printWindow.print();
    }

    exportShoppingList() {
        if (!this.currentShoppingListModal) return;
        
        // Get the shopping list data from the modal
        const shoppingListContent = this.currentShoppingListModal.querySelector('.shopping-list-content');
        if (!shoppingListContent) return;
        
        // Show loading indicator
        RecipeApp.showAlert('Generating PDF...', 'info');
        
        // Extract shopping list data
        const categories = {};
        const categoryElements = shoppingListContent.querySelectorAll('.category-section');
        
        categoryElements.forEach(categorySection => {
            const categoryName = categorySection.querySelector('.category-header').textContent.trim();
            const items = [];
            
            categorySection.querySelectorAll('.form-check-label').forEach(label => {
                items.push(label.textContent.trim());
            });
            
            if (items.length > 0) {
                categories[categoryName] = items;
            }
        });
        
        // Prepare data for the request
        const data = {
            shopping_list: {
                name: `Weekly Shopping List - ${this.formatDisplayDate(this.currentWeek)}`,
                categories: categories,
                total_items: Object.values(categories).flat().length,
                estimated_cost: this.currentShoppingListModal.querySelector('.shopping-summary').textContent.includes('Estimated Cost:') ?
                    this.currentShoppingListModal.querySelector('.shopping-summary').textContent.split('Estimated Cost:')[1].trim() : 'N/A'
            }
        };
        
        // Make POST request to the PDF export endpoint
        fetch('/ai/shopping-list/export-pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/pdf'
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to generate PDF');
            }
            return response.blob();
        })
        .then(blob => {
            // Create a URL for the blob
            const url = window.URL.createObjectURL(blob);
            
            // Create a temporary link and trigger download
            const a = document.createElement('a');
            a.href = url;
            a.download = `${data.shopping_list.name}.pdf`;
            document.body.appendChild(a);
            a.click();
            
            // Clean up
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            RecipeApp.showAlert('PDF downloaded successfully!', 'success');
        })
        .catch(error => {
            console.error('PDF export error:', error);
            RecipeApp.showAlert('Failed to generate PDF. Please try again.', 'error');
        });
    }
}

// Global functions for drag and drop
window.allowDrop = function(ev) {
    ev.preventDefault();
}

window.drop = function(ev) {
    ev.preventDefault();
}

// Initialize meal planner when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.mealPlanner = new MealPlanner();
});
