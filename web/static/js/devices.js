class DevicesManager {
    constructor() {
        this.devicesList = document.querySelector('.devices-list');
        this.devices = new Map();
        this.init();
    }

    init() {
        // Initialize WebSocket connection
        this.connectWebSocket();
        // Update devices status periodically
        setInterval(() => this.updateDevicesStatus(), 30000);
    }

    connectWebSocket() {
        // Replace with your WebSocket server URL
        const ws = new WebSocket('ws://your-server-url/ws');

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.updateDevice(data);
        };
    }

    updateDevice(deviceData) {
        const deviceId = deviceData.id;
        
        if (!this.devices.has(deviceId)) {
            // Create new device card
            const deviceCard = this.createDeviceCard(deviceData);
            this.devicesList.appendChild(deviceCard);
            this.devices.set(deviceId, deviceCard);
        } else {
            // Update existing device card
            this.updateDeviceCard(this.devices.get(deviceId), deviceData);
        }
    }

    createDeviceCard(device) {
        const card = document.createElement('div');
        card.className = 'device-card';
        card.innerHTML = `
            <div class="device-header">
                <i class="device-icon fab ${this.getOSIcon(device.os)}"></i>
                <span class="device-name">${device.name}</span>
            </div>
            <div class="device-info">
                <div class="device-detail">
                    <span>OS:</span>
                    <span>${device.os}</span>
                </div>
                <div class="device-detail">
                    <span>IP:</span>
                    <span>${device.ip}</span>
                </div>
                <div class="device-detail">
                    <span>Last Active:</span>
                    <span>${this.formatDate(device.lastActive)}</span>
                </div>
                <div class="device-detail">
                    <span>Status:</span>
                    <div class="device-status">
                        <div class="status-indicator ${device.active ? 'status-active' : 'status-inactive'}"></div>
                        <span>${device.active ? 'Active' : 'Inactive'}</span>
                    </div>
                </div>
            </div>
        `;
        return card;
    }

    updateDeviceCard(card, device) {
        // Update status indicator
        const statusIndicator = card.querySelector('.status-indicator');
        statusIndicator.className = `status-indicator ${device.active ? 'status-active' : 'status-inactive'}`;
        
        // Update last active time
        const lastActive = card.querySelector('.device-detail:nth-child(3) span:last-child');
        lastActive.textContent = this.formatDate(device.lastActive);
    }

    getOSIcon(os) {
        const osLower = os.toLowerCase();
        if (osLower.includes('windows')) return 'fa-windows';
        if (osLower.includes('mac')) return 'fa-apple';
        if (osLower.includes('linux')) return 'fa-linux';
        return 'fa-desktop';
    }

    formatDate(date) {
        return new Date(date).toLocaleString();
    }

    updateDevicesStatus() {
        // Check for inactive devices
        const now = Date.now();
        this.devices.forEach((card, deviceId) => {
            const lastActive = new Date(card.querySelector('.device-detail:nth-child(3) span:last-child').textContent);
            const inactive = (now - lastActive) > 5 * 60 * 1000; // 5 minutes threshold
            
            const statusIndicator = card.querySelector('.status-indicator');
            statusIndicator.className = `status-indicator ${inactive ? 'status-inactive' : 'status-active'}`;
        });
    }
}

// Initialize devices manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new DevicesManager();
}); 