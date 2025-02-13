class KeyLoggerControl {
    constructor() {
        this.startButton = document.getElementById('start-logger');
        this.stopButton = document.getElementById('stop-logger');
        this.clearButton = document.getElementById('clear-logs');
        this.output = document.getElementById('keylogger-output');
        this.selectedOS = null;
        
        // Add OS selection handling
        const osButtons = document.querySelectorAll('.os-type-item');
        osButtons.forEach(button => {
            button.addEventListener('click', () => this.selectOS(button.dataset.os));
        });
        
        this.setupEventListeners();
        this.updateStatus();
    }

    selectOS(os) {
        this.selectedOS = os;
        // Update UI to show selected OS
        document.querySelectorAll('.os-type-item').forEach(btn => {
            btn.classList.remove('selected');
        });
        document.querySelector(`[data-os="${os}"]`).classList.add('selected');
        
        // Enable/disable controls based on OS selection
        const controls = document.querySelectorAll('.control-btn');
        controls.forEach(btn => {
            btn.disabled = false;
        });
        
        this.output.textContent = `Selected ${os} keylogger`;
    }

    setupEventListeners() {
        this.startButton.addEventListener('click', () => this.startLogging());
        this.stopButton.addEventListener('click', () => this.stopLogging());
        this.clearButton.addEventListener('click', () => this.clearLogs());
    }

    async startLogging() {
        if (!this.selectedOS) {
            this.output.textContent = 'Please select an operating system first';
            return;
        }

        try {
            const response = await fetch('http://localhost:5001/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ os: this.selectedOS })
            });
            const data = await response.json();
            this.output.textContent = `${this.selectedOS} keylogger started...`;
            this.updateStatus();
        } catch (error) {
            console.error('Error:', error);
            this.output.textContent = 'Error starting keylogger';
        }
    }

    async stopLogging() {
        try {
            const response = await fetch('/stop', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            const data = await response.json();
            this.output.textContent += '\nKeylogger stopped.';
            this.updateStatus();
        } catch (error) {
            console.error('Error:', error);
            this.output.textContent = 'Error stopping keylogger';
        }
    }

    async updateStatus() {
        try {
            const response = await fetch('/status');
            const data = await response.json();
            this.startButton.disabled = data.status === 'running';
            this.stopButton.disabled = data.status === 'stopped';
        } catch (error) {
            console.error('Error:', error);
        }
    }

    clearLogs() {
        this.output.textContent = 'Logs cleared.';
    }
} 