class ThemeManager {
    constructor() {
        this.themeToggle = document.createElement('button');
        this.themeToggle.className = 'theme-toggle control-btn';
        this.themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
        this.init();
    }

    init() {
        // Add theme toggle to header
        document.querySelector('.header').appendChild(this.themeToggle);
        
        // Set initial theme
        const savedTheme = localStorage.getItem('theme') || 'dark';
        document.body.setAttribute('data-theme', savedTheme);
        
        // Handle toggle
        this.themeToggle.addEventListener('click', () => this.toggleTheme());
    }

    toggleTheme() {
        const currentTheme = document.body.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        document.body.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        
        // Update icon
        this.themeToggle.innerHTML = newTheme === 'dark' ? 
            '<i class="fas fa-moon"></i>' : 
            '<i class="fas fa-sun"></i>';
    }
} 