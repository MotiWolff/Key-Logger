class LogExporter {
    constructor() {
        this.exportBtn = document.createElement('button');
        this.exportBtn.className = 'control-btn';
        this.exportBtn.innerHTML = '<i class="fas fa-download"></i> Export Logs';
        this.init();
    }

    init() {
        // Add export button to logs section
        document.querySelector('#logs').appendChild(this.exportBtn);
        this.exportBtn.addEventListener('click', () => this.exportLogs());
    }

    exportLogs() {
        const logs = document.getElementById('keylogger-output').textContent;
        const blob = new Blob([logs], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        
        a.href = url;
        a.download = `keylogger_logs_${new Date().toISOString()}.txt`;
        document.body.appendChild(a);
        a.click();
        
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }
} 