// Web Crypto API for client-side message encryption

// Derive a symmetric key from a string (e.g., group ID or passkey)
async function deriveKey(secretString) {
    const enc = new TextEncoder();
    const keyMaterial = await window.crypto.subtle.importKey(
        "raw",
        enc.encode(secretString),
        { name: "PBKDF2" },
        false,
        ["deriveBits", "deriveKey"]
    );
    return window.crypto.subtle.deriveKey(
        {
            name: "PBKDF2",
            salt: enc.encode("chat-groups-salt"),
            iterations: 100000,
            hash: "SHA-256"
        },
        keyMaterial,
        { name: "AES-GCM", length: 256 },
        true,
        ["encrypt", "decrypt"]
    );
}

// Convert ArrayBuffer to Base64
function bufferToBase64(buffer) {
    let binary = '';
    const bytes = new Uint8Array(buffer);
    for (let i = 0; i < bytes.byteLength; i++) {
        binary += String.fromCharCode(bytes[i]);
    }
    return window.btoa(binary);
}

// Convert Base64 to ArrayBuffer
function base64ToBuffer(base64) {
    const binary_string = window.atob(base64);
    const len = binary_string.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) {
        bytes[i] = binary_string.charCodeAt(i);
    }
    return bytes.buffer;
}

// Encrypt a string message
async function encryptMessage(key, message) {
    try {
        const enc = new TextEncoder();
        const iv = window.crypto.getRandomValues(new Uint8Array(12));
        const ciphertext = await window.crypto.subtle.encrypt(
            {
                name: "AES-GCM",
                iv: iv
            },
            key,
            enc.encode(message)
        );
        // Combine IV and ciphertext, then base64 encode
        const combined = new Uint8Array(iv.length + ciphertext.byteLength);
        combined.set(iv, 0);
        combined.set(new Uint8Array(ciphertext), iv.length);
        return bufferToBase64(combined.buffer);
    } catch (e) {
        console.error("Encryption failed:", e);
        return message; // fallback to plaintext on failure
    }
}

// Decrypt a base64 encoded ciphertext
async function decryptMessage(key, encryptedBase64) {
    try {
        const combined = new Uint8Array(base64ToBuffer(encryptedBase64));
        const iv = combined.slice(0, 12);
        const data = combined.slice(12);
        const decrypted = await window.crypto.subtle.decrypt(
            {
                name: "AES-GCM",
                iv: iv
            },
            key,
            data
        );
        const dec = new TextDecoder();
        return dec.decode(decrypted);
    } catch (e) {
        // If decryption fails, assume it was a plaintext message
        return encryptedBase64;
    }
}
