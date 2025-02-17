class EncryptionUtil {
    constructor(key) {
        this.key = key;
        this.encoder = new TextEncoder();
        this.decoder = new TextDecoder();
    }

    async encrypt(text) {
        try {
            const keyBuffer = await crypto.subtle.importKey(
                'raw',
                this.encoder.encode(this.key),
                { name: 'AES-GCM' },
                false,
                ['encrypt']
            );

            const iv = crypto.getRandomValues(new Uint8Array(12));
            const encrypted = await crypto.subtle.encrypt(
                {
                    name: 'AES-GCM',
                    iv: iv
                },
                keyBuffer,
                this.encoder.encode(text)
            );

            // Combine IV and encrypted data
            const combined = new Uint8Array(iv.length + encrypted.byteLength);
            combined.set(iv);
            combined.set(new Uint8Array(encrypted), iv.length);

            return btoa(String.fromCharCode(...combined));
        } catch (error) {
            console.error('Encryption error:', error);
            throw error;
        }
    }

    async decrypt(encryptedText) {
        try {
            const combined = new Uint8Array(
                atob(encryptedText).split('').map(char => char.charCodeAt(0))
            );

            const iv = combined.slice(0, 12);
            const data = combined.slice(12);

            const keyBuffer = await crypto.subtle.importKey(
                'raw',
                this.encoder.encode(this.key),
                { name: 'AES-GCM' },
                false,
                ['decrypt']
            );

            const decrypted = await crypto.subtle.decrypt(
                {
                    name: 'AES-GCM',
                    iv: iv
                },
                keyBuffer,
                data
            );

            return this.decoder.decode(decrypted);
        } catch (error) {
            console.error('Decryption error:', error);
            throw error;
        }
    }
} 