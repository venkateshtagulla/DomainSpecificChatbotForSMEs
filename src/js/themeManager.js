export class ThemeManager {
    constructor() {
        this.themeSelect = document.getElementById('themeSelect');
        this.setupEventListeners();
        this.loadSavedTheme();
    }

    setupEventListeners() {
        this.themeSelect.addEventListener('change', () => {
            this.setTheme(this.themeSelect.value);
        });
    }

    setTheme(themeName) {
        document.body.className = themeName;
        localStorage.setItem('chatbot-theme', themeName);
    }

    loadSavedTheme() {
        const savedTheme = localStorage.getItem('chatbot-theme') || 'theme-dark';
        this.themeSelect.value = savedTheme;
        this.setTheme(savedTheme);
    }
}