class LogSearch {
    constructor() {
        this.searchInput = document.createElement('input');
        this.searchInput.type = 'text';
        this.searchInput.className = 'search-input';
        this.searchInput.placeholder = 'Search logs...';
        this.init();
    }

    init() {
        // Add search input before logs container
        const logsContainer = document.querySelector('.logs-container');
        logsContainer.parentNode.insertBefore(this.searchInput, logsContainer);
        
        this.searchInput.addEventListener('input', () => this.filterLogs());
    }

    filterLogs() {
        const searchTerm = this.searchInput.value.toLowerCase();
        const logContent = document.getElementById('keylogger-output');
        const lines = logContent.textContent.split('\n');
        
        const filteredContent = lines
            .filter(line => line.toLowerCase().includes(searchTerm))
            .join('\n');
        
        logContent.textContent = filteredContent || 'No matching logs found';
    }
} 