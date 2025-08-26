// Global RecipeApp object
const RecipeApp = {
    _currentUser: null,
    _authToken: localStorage.getItem('authToken'),
    
    // Getters
    currentUser: function() {
        return this._currentUser;
    },
    
    authToken: function() {
        return this._authToken;
    },
    
    // Setters
    setCurrentUser: function(user) {
        this._currentUser = user;
    },
    
    setAuthToken: function(token) {
        this._authToken = token;
        if (token) {
            localStorage.setItem('authToken', token);
        } else {
            localStorage.removeItem('authToken');
        }
    },
    
    // UI Helpers
    showAlert: function(message, type = 'info') {
        const alertContainer = document.getElementById('alertContainer') || this._createAlertContainer();
        
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        alertContainer.appendChild(alert);
        
        // Auto dismiss after 5 seconds
        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => alert.remove(), 150);
        }, 5000);
    },
    
    _createAlertContainer: function() {
        const container = document.createElement('div');
        container.id = 'alertContainer';
        container.className = 'alert-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1050';
        document.body.appendChild(container);
        return container;
    },
    
    showLoading: function(message = 'Loading...', subtext = '') {
        const loadingOverlay = document.getElementById('loadingOverlay') || this._createLoadingOverlay();
        
        document.getElementById('loadingMessage').textContent = message;
        document.getElementById('loadingSubtext').textContent = subtext;
        
        loadingOverlay.classList.add('show');
        document.body.classList.add('loading');
    },
    
    hideLoading: function() {
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) {
            loadingOverlay.classList.remove('show');
            document.body.classList.remove('loading');
        }
    },
    
    _createLoadingOverlay: function() {
        const overlay = document.createElement('div');
        overlay.id = 'loadingOverlay';
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="loading-spinner-container">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <div class="mt-3">
                    <h5 id="loadingMessage" class="text-white">Loading...</h5>
                    <p id="loadingSubtext" class="text-white-50 small"></p>
                </div>
            </div>
        `;
        
        // Add CSS if not already present
        if (!document.getElementById('loadingOverlayStyles')) {
            const style = document.createElement('style');
            style.id = 'loadingOverlayStyles';
            style.textContent = `
                .loading-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background-color: rgba(0, 0, 0, 0.7);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    z-index: 2000;
                    opacity: 0;
                    visibility: hidden;
                    transition: opacity 0.3s, visibility 0.3s;
                }
                .loading-overlay.show {
                    opacity: 1;
                    visibility: visible;
                }
                body.loading {
                    overflow: hidden;
                }
                .loading-spinner-container {
                    text-align: center;
                }
            `;
            document.head.appendChild(style);
        }
        
        document.body.appendChild(overlay);
        return overlay;
    }
};

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    loadUserState();
    initializeTheme();
});

// Initialize application
function initializeApp() {
    console.log('Initializing AI Recipe Hub...');
    
    // Check authentication state
    if (RecipeApp.authToken()) {
        validateToken();
    } else {
        showGuestMenu();
    }
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// Setup event listeners
function setupEventListeners() {
    // Theme toggle
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
    
    // Language selector
    const languageItems = document.querySelectorAll('[data-lang]');
    languageItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            changeLanguage(this.dataset.lang);
        });
    });
    
    // Logout button
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', logout);
    }
    
    // Global error handler
    window.addEventListener('error', function(e) {
        console.error('Global error:', e.error);
        RecipeApp.showAlert('An unexpected error occurred. Please try again.', 'error');
    });
    
    // Handle unhandled promise rejections
    window.addEventListener('unhandledrejection', function(e) {
        console.error('Unhandled promise rejection:', e.reason);
        RecipeApp.showAlert('A network error occurred. Please check your connection.', 'error');
    });
}

// Authentication functions
async function validateToken() {
    try {
        const response = await fetch('/auth/profile', {
            headers: {
                'Authorization': `Bearer ${RecipeApp.authToken()}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                RecipeApp.setCurrentUser(data.user);
                showUserMenu();
                updateLanguageDisplay(RecipeApp.currentUser().preferred_language);
            } else {
                clearAuthToken();
                showGuestMenu();
            }
        } else {
            clearAuthToken();
            showGuestMenu();
        }
    } catch (error) {
        console.error('Token validation error:', error);
        clearAuthToken();
        showGuestMenu();
    }
}

function clearAuthToken() {
    RecipeApp.setAuthToken(null);
    RecipeApp.setCurrentUser(null);
}

function showUserMenu() {
    const userMenu = document.getElementById('userMenu');
    const guestMenu = document.getElementById('guestMenu');
    const userName = document.getElementById('userName');
    
    if (userMenu && guestMenu) {
        userMenu.style.display = 'block';
        guestMenu.style.display = 'none';
        
        if (userName && RecipeApp.currentUser()) {
            userName.textContent = RecipeApp.currentUser().name;
        }
    }
}

function showGuestMenu() {
    const userMenu = document.getElementById('userMenu');
    const guestMenu = document.getElementById('guestMenu');
    
    if (userMenu && guestMenu) {
        userMenu.style.display = 'none';
        guestMenu.style.display = 'block';
    }
}

function logout() {
    clearAuthToken();
    showGuestMenu();
    RecipeApp.showAlert('Logged out successfully', 'success');
    
    // Redirect to home page
    if (window.location.pathname !== '/') {
        window.location.href = '/';
    }
}

// Theme functions
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
}

function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    
    const themeIcon = document.getElementById('themeIcon');
    if (themeIcon) {
        themeIcon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
    }
    
    // Update meta theme color for mobile browsers
    const metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (metaThemeColor) {
        metaThemeColor.content = theme === 'light' ? '#007bff' : '#1a1d23';
    }
}

// Language functions
function changeLanguage(langCode) {
    if (RecipeApp.currentUser() && RecipeApp.authToken()) {
        updateUserLanguage(langCode);
    } else {
        localStorage.setItem('preferred_language', langCode);
    }
    
    updateLanguageDisplay(langCode);
    RecipeApp.showAlert(`Language changed to ${getLanguageName(langCode)}`, 'success');
}

async function updateUserLanguage(langCode) {
    try {
        const response = await fetch('/auth/profile', {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${RecipeApp.authToken()}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                preferred_language: langCode
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                const user = RecipeApp.currentUser();
                if (user) {
                    user.preferred_language = langCode;
                    RecipeApp.setCurrentUser(user);
                }
            }
        }
    } catch (error) {
        console.error('Language update error:', error);
    }
}

function updateLanguageDisplay(langCode) {
    const currentLanguageEl = document.getElementById('currentLanguage');
    if (currentLanguageEl) {
        currentLanguageEl.textContent = langCode.toUpperCase();
    }
}

function getLanguageName(langCode) {
    const languages = {
        'en': 'English',
        'es': 'Español',
        'fr': 'Français',
        'de': 'Deutsch',
        'it': 'Italiano',
        'ja': '日本語'
    };
    return languages[langCode] || langCode;
}

// Recipe functions
async function saveRecipe(recipeId) {
    if (!RecipeApp.authToken()) {
        RecipeApp.showAlert('Please login to save recipes', 'warning');
        return;
    }
    
    try {
        RecipeApp.showLoading('Saving recipe...');
        
        const response = await fetch('/recipes/save', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${RecipeApp.authToken()}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                recipe_id: recipeId
            })
        });
        
        const data = await response.json();
        RecipeApp.hideLoading();
        
        if (data.success) {
            RecipeApp.showAlert('Recipe saved successfully!', 'success');
            
            // Update UI to show saved state
            const saveButtons = document.querySelectorAll(`[onclick*="${recipeId}"]`);
            saveButtons.forEach(btn => {
                btn.innerHTML = '<i class="fas fa-heart me-1"></i>Saved';
                btn.classList.remove('btn-outline-success');
                btn.classList.add('btn-success');
                btn.disabled = true;
            });
        } else {
            RecipeApp.showAlert(data.message || 'Failed to save recipe', 'error');
        }
    } catch (error) {
        RecipeApp.hideLoading();
        console.error('Save recipe error:', error);
        RecipeApp.showAlert('Failed to save recipe', 'error');
    }
}

async function rateRecipe(recipeId, rating, comment = '') {
    if (!RecipeApp.authToken()) {
        RecipeApp.showAlert('Please login to rate recipes', 'warning');
        return;
    }
    
    try {
        const response = await fetch('/recipes/rate', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${RecipeApp.authToken()}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                recipe_id: recipeId,
                rating: rating,
                comment: comment
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            RecipeApp.showAlert('Rating submitted successfully!', 'success');
        } else {
            RecipeApp.showAlert(data.message || 'Failed to submit rating', 'error');
        }
    } catch (error) {
        console.error('Rate recipe error:', error);
        RecipeApp.showAlert('Failed to submit rating', 'error');
    }
}

// Utility functions
// These functions are now part of the RecipeApp object

// This function is now part of the RecipeApp object

function formatTime(minutes) {
    if (minutes < 60) {
        return `${minutes} min`;
    } else {
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
    }
}

function truncateText(text, maxLength = 100) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            timeout = null;
            if (!immediate) func(...args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func(...args);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Form validation helpers
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePassword(password) {
    return password.length >= 6;
}

function sanitizeHtml(str) {
    const temp = document.createElement('div');
    temp.textContent = str;
    return temp.innerHTML;
}

// Local storage helpers
function loadUserState() {
    const savedLanguage = localStorage.getItem('preferred_language');
    if (savedLanguage && !RecipeApp.currentUser()) {
        updateLanguageDisplay(savedLanguage);
    }
}

// Network status handling
window.addEventListener('online', function() {
    RecipeApp.showAlert('Connection restored', 'success');
});

window.addEventListener('offline', function() {
    RecipeApp.showAlert('Connection lost. Some features may not work.', 'warning');
});

// Service worker registration (for PWA features)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/sw.js')
            .then(function(registration) {
                console.log('ServiceWorker registration successful');
            })
            .catch(function(err) {
                console.log('ServiceWorker registration failed');
            });
    });
}

// Export RecipeApp object for use in other files
window.RecipeApp = RecipeApp;

// Add additional utility functions to RecipeApp
Object.assign(RecipeApp, {
    saveRecipe,
    rateRecipe,
    formatTime,
    truncateText,
    debounce,
    throttle,
    validateEmail,
    validatePassword,
    sanitizeHtml
});
