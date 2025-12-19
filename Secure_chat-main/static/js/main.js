'use strict';

const socket = io();
const encoder = new TextEncoder();
const decoder = new TextDecoder();

const store = {
    username: '',
    fingerprint: '',
    keyPair: null,
    publicKeyB64: '',
    participants: new Map(),
    messages: [],
    connected: false,
    joinPending: false,
};

const usernameInput = document.getElementById('username');
const joinBtn = document.getElementById('join-btn');
const leaveBtn = document.getElementById('leave-btn');
const fingerprintEl = document.getElementById('self-fingerprint');
const participantListEl = document.getElementById('participant-list');
const participantCountEl = document.getElementById('participant-count');
const participantHintEl = document.getElementById('participant-hint');
const refreshParticipantsBtn = document.getElementById('refresh-participants');
const statusEl = document.getElementById('status');
const chatLogEl = document.getElementById('chat-log');
const messageInput = document.getElementById('message');
const sendBtn = document.getElementById('send-btn');
const messageTemplate = document.getElementById('message-template');

socket.on('connect', () => {
    console.log('[socket] connected');
    store.connected = true;
    store.joinPending = false;
    setStatus('Connected. Pick a username to join.');
    updateUiState();
});

socket.on('connect_error', (err) => {
    console.error('[socket] connect_error', err);
    setStatus('Socket connection failed. Check the server status.');
});

socket.on('disconnect', (reason) => {
    console.warn('[socket] disconnected', reason);
    store.connected = false;
    store.joinPending = false;
    setStatus('Disconnected from server. Reconnecting...');
    updateUiState();
});

joinBtn.addEventListener('click', () => {
    registerUser().catch((err) => {
        console.error(err);
        setStatus('Join failed. Open the console for details.');
        store.joinPending = false;
        updateUiState();
    });
});

leaveBtn.addEventListener('click', () => {
    if (!store.username) {
        setStatus('Join first, then you can leave.');
        return;
    }
    socket.emit('leave_chat');
    appendSystemMessage('You left the chat.');
    resetState();
    setStatus('Left the chat. Pick a username to rejoin.');
});

refreshParticipantsBtn.addEventListener('click', () => {
    refreshParticipants().catch((err) => {
        console.error(err);
        setStatus(err.message || 'Could not refresh the participant list.');
    });
});

sendBtn.addEventListener('click', () => {
    sendSecureMessage().catch((err) => {
        console.error(err);
        appendSystemMessage('Message failed to send.');
    });
});

messageInput.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
        event.preventDefault();
        sendSecureMessage().catch((err) => {
            console.error(err);
            appendSystemMessage('Message failed to send.');
        });
    }
});

messageInput.addEventListener('input', () => updateUiState());

socket.on('register_success', async (payload) => {
    console.log('[socket] register_success', payload);
    store.joinPending = false;
    store.username = payload.username;
    store.fingerprint = payload.fingerprint;
    fingerprintEl.textContent = payload.fingerprint;
    leaveBtn.removeAttribute('disabled');
    setStatus(`Joined as ${payload.username}.`);
    await syncParticipants(payload.participants || []);
    appendSystemMessage(`You joined as ${payload.username}.`);
    updateUiState();
});

socket.on('register_error', (payload) => {
    const message = payload && payload.message ? payload.message : 'Registration error.';
    console.warn('[socket] register_error', message);
    store.joinPending = false;
    setStatus(message);
    updateUiState();
});

socket.on('participants', async (payload) => {
    await syncParticipants((payload && payload.participants) || []);
});

socket.on('user_joined', (payload) => {
    if (!payload || !payload.username || payload.username === store.username) {
        return;
    }
    appendSystemMessage(`${payload.username} joined the chat.`);
});

socket.on('user_left', (payload) => {
    const username = payload && payload.username ? payload.username : null;
    if (!username || username === store.username) {
        return;
    }
    store.participants.delete(username);
    renderParticipants();
    updateUiState();
    appendSystemMessage(`${username} left the chat.`);
});

socket.on('receive_message', async (payload) => {
    if (!store.keyPair?.privateKey) {
        return;
    }
    const envelopeB64 = payload.envelopes?.[store.username];
    if (!envelopeB64) {
        return;
    }
    try {
        const encryptedKey = base64ToArrayBuffer(envelopeB64);
        const rawKey = await window.crypto.subtle.decrypt(
            { name: 'RSA-OAEP' },
            store.keyPair.privateKey,
            encryptedKey
        );
        const aesKey = await window.crypto.subtle.importKey(
            'raw',
            rawKey,
            { name: 'AES-GCM' },
            false,
            ['decrypt']
        );
        const iv = new Uint8Array(base64ToArrayBuffer(payload.iv));
        const ciphertext = base64ToArrayBuffer(payload.ciphertext);
        const plaintextBuffer = await window.crypto.subtle.decrypt(
            { name: 'AES-GCM', iv },
            aesKey,
            ciphertext
        );
        const plaintext = decoder.decode(plaintextBuffer);
        appendMessage({
            direction: payload.from === store.username ? 'outbound' : 'inbound',
            author: payload.from,
            body: plaintext,
            timestamp: payload.timestamp,
        });
    } catch (error) {
        console.error(error);
        appendSystemMessage('Failed to decrypt an incoming message.');
    }
});

socket.on('delivery_error', (payload) => {
    const message = payload && payload.message ? payload.message : 'Delivery error.';
    console.warn('[socket] delivery_error', message);
    setStatus(message);
    appendSystemMessage(message);
});

async function registerUser() {
    if (!store.connected) {
        setStatus('Still connecting to the server...');
        return;
    }

    if (store.joinPending) {
        setStatus('Join request already in progress.');
        return;
    }

    const requestedUsername = usernameInput.value.trim();
    if (!requestedUsername) {
        setStatus('Enter a username to join the chat.');
        return;
    }
    if (requestedUsername.length < 2) {
        setStatus('Usernames must have at least 2 characters.');
        return;
    }
    if (!ensureCryptoAvailable()) {
        return;
    }

    store.joinPending = true;
    updateUiState();

    try {
        setStatus('Generating RSA key pair...');
        store.keyPair = await window.crypto.subtle.generateKey(
            {
                name: 'RSA-OAEP',
                modulusLength: 2048,
                publicExponent: new Uint8Array([1, 0, 1]),
                hash: 'SHA-256',
            },
            true,
            ['encrypt', 'decrypt']
        );

        setStatus('Exporting public key...');
        const publicKeyBuffer = await window.crypto.subtle.exportKey('spki', store.keyPair.publicKey);
        store.publicKeyB64 = arrayBufferToBase64(publicKeyBuffer);

        setStatus(`Joining as ${requestedUsername}...`);
        socket.emit('register', {
            username: requestedUsername,
            public_key: store.publicKeyB64,
        });
    } catch (error) {
        store.joinPending = false;
        updateUiState();
        throw error;
    }
}

async function sendSecureMessage() {
    if (!store.username || !store.keyPair) {
        setStatus('Join the chat before sending messages.');
        return;
    }

    const message = messageInput.value.trim();
    if (!message) {
        updateUiState();
        return;
    }

    ensureSelfParticipant();
    const recipients = Array.from(store.participants.entries());
    if (!recipients.length) {
        appendSystemMessage('No one else is connected yet.');
        return;
    }

    const aesKey = await window.crypto.subtle.generateKey(
        { name: 'AES-GCM', length: 256 },
        true,
        ['encrypt', 'decrypt']
    );

    const iv = window.crypto.getRandomValues(new Uint8Array(12));
    const ciphertextBuffer = await window.crypto.subtle.encrypt(
        { name: 'AES-GCM', iv },
        aesKey,
        encoder.encode(message)
    );

    const rawAesKey = await window.crypto.subtle.exportKey('raw', aesKey);
    const envelopes = {};

    for (const [username, info] of recipients) {
        let cryptoKey = info.cryptoKey;
        if (username === store.username) {
            cryptoKey = store.keyPair.publicKey;
        } else if (!cryptoKey && info.publicKeyB64) {
            try {
                cryptoKey = await importPublicKey(info.publicKeyB64);
                info.cryptoKey = cryptoKey;
                store.participants.set(username, info);
            } catch (error) {
                console.error('Failed to import key for', username, error);
                setStatus(`Cannot encrypt for ${username}.`);
                return;
            }
        }

        if (!cryptoKey) {
            setStatus(`Public key for ${username} is unavailable.`);
            return;
        }

        const encryptedKeyBuffer = await window.crypto.subtle.encrypt(
            { name: 'RSA-OAEP' },
            cryptoKey,
            rawAesKey
        );
        envelopes[username] = arrayBufferToBase64(encryptedKeyBuffer);
    }

    const timestamp = new Date().toISOString();
    const payload = {
        from: store.username,
        ciphertext: arrayBufferToBase64(ciphertextBuffer),
        iv: arrayBufferToBase64(iv.buffer),
        timestamp,
        envelopes,
    };

    socket.emit('send_message', payload);
    appendMessage({ direction: 'outbound', author: store.username, body: message, timestamp });
    messageInput.value = '';
    updateUiState();
}

async function refreshParticipants() {
    if (!store.connected) {
        throw new Error('Connect to the server before refreshing users.');
    }
    const response = await fetch('/api/users', { cache: 'no-store' });
    if (!response.ok) {
        const errorPayload = await readJsonSafely(response);
        throw new Error((errorPayload && errorPayload.error) || 'Participant lookup failed.');
    }
    const payload = await response.json();
    await syncParticipants(payload.participants || []);
    setStatus('Participant list refreshed.');
}

async function syncParticipants(participants) {
    const seen = new Set();
    const tasks = participants.map(async (participant) => {
        if (!participant || !participant.username) {
            return;
        }
        const username = participant.username;
        const record = store.participants.get(username) || {};
        record.fingerprint = participant.fingerprint || record.fingerprint || 'unknown';
        record.publicKeyB64 = participant.public_key || record.publicKeyB64;
        if (username !== store.username && record.publicKeyB64) {
            try {
                record.cryptoKey = await importPublicKey(record.publicKeyB64);
            } catch (error) {
                console.error('Failed to import public key for', username, error);
            }
        }
        store.participants.set(username, record);
        seen.add(username);
    });
    await Promise.all(tasks);

    ensureSelfParticipant();

    for (const username of Array.from(store.participants.keys())) {
        if (username === store.username) {
            continue;
        }
        if (!seen.has(username)) {
            store.participants.delete(username);
        }
    }

    renderParticipants();
    updateUiState();
}

function ensureSelfParticipant() {
    if (!store.username) {
        return;
    }
    const self = store.participants.get(store.username) || {};
    self.fingerprint = store.fingerprint || self.fingerprint || 'self';
    self.publicKeyB64 = store.publicKeyB64 || self.publicKeyB64;
    store.participants.set(store.username, self);
}

function renderParticipants() {
    participantListEl.innerHTML = '';
    const entries = Array.from(store.participants.entries()).sort((a, b) => a[0].localeCompare(b[0]));
    const visible = entries.filter((entry) => entry[0] !== store.username);

    entries.forEach(([username, info]) => {
        const li = document.createElement('li');
        if (username === store.username) {
            li.classList.add('me');
        }
        const name = document.createElement('div');
        name.className = 'name';
        name.textContent = username === store.username ? `${username} (you)` : username;

        const fp = document.createElement('div');
        fp.className = 'fingerprint';
        fp.textContent = info.fingerprint ? `fp ${info.fingerprint}` : 'fingerprint unavailable';

        li.appendChild(name);
        li.appendChild(fp);
        participantListEl.appendChild(li);
    });

    participantCountEl.textContent = Math.max(visible.length, 0).toString();
    participantHintEl.style.display = entries.length > 0 ? 'none' : 'block';
}

function appendMessage(message) {
    store.messages.push({
        direction: message.direction || 'system',
        author: message.author,
        body: message.body,
        timestamp: message.timestamp || new Date().toISOString(),
    });
    renderMessages();
}

function appendSystemMessage(body) {
    appendMessage({ direction: 'system', author: 'system', body });
}

function renderMessages() {
    chatLogEl.innerHTML = '';
    store.messages.forEach((message) => {
        const bubble = messageTemplate.content.firstElementChild.cloneNode(true);
        bubble.classList.add(message.direction);
        const timestamp = new Date(message.timestamp).toLocaleTimeString();
        if (message.direction === 'system') {
            bubble.querySelector('.meta').textContent = timestamp;
            bubble.querySelector('.body').textContent = message.body;
        } else {
            const label = message.direction === 'outbound' ? 'You' : message.author;
            bubble.querySelector('.meta').textContent = `${label} • ${timestamp}`;
            bubble.querySelector('.body').textContent = message.body;
        }
        chatLogEl.appendChild(bubble);
    });
    chatLogEl.scrollTop = chatLogEl.scrollHeight;
}

function resetState() {
    store.joinPending = false;
    store.username = '';
    store.fingerprint = '';
    store.keyPair = null;
    store.publicKeyB64 = '';
    store.participants.clear();
    store.messages = [];
    fingerprintEl.textContent = 'Not joined';
    renderParticipants();
    renderMessages();
    updateUiState();
}

function updateUiState() {
    const joined = Boolean(store.username && store.keyPair);
    messageInput.disabled = !joined;
    sendBtn.disabled = !joined || !messageInput.value.trim();
    leaveBtn.disabled = !joined;

    if (joined) {
        joinBtn.setAttribute('disabled', 'true');
        usernameInput.setAttribute('disabled', 'true');
    } else {
        if (store.joinPending) {
            joinBtn.setAttribute('disabled', 'true');
            usernameInput.setAttribute('disabled', 'true');
        } else {
            usernameInput.removeAttribute('disabled');
            if (store.connected) {
                joinBtn.removeAttribute('disabled');
            } else {
                joinBtn.setAttribute('disabled', 'true');
            }
        }
    }

    if (store.connected) {
        refreshParticipantsBtn.removeAttribute('disabled');
    } else {
        refreshParticipantsBtn.setAttribute('disabled', 'true');
    }
}

function setStatus(message) {
    statusEl.textContent = message;
}

function ensureCryptoAvailable() {
    if (window.crypto && window.crypto.subtle) {
        return true;
    }
    const message = 'This browser requires a secure context (https or http://localhost) for cryptography.';
    setStatus(message);
    appendSystemMessage(message);
    return false;
}

function arrayBufferToBase64(buffer) {
    const bytes = new Uint8Array(buffer);
    let binary = '';
    const chunk = 0x8000;
    for (let i = 0; i < bytes.length; i += chunk) {
        const slice = bytes.subarray(i, i + chunk);
        binary += String.fromCharCode.apply(null, slice);
    }
    return window.btoa(binary);
}

function base64ToArrayBuffer(base64) {
    const binary = window.atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i += 1) {
        bytes[i] = binary.charCodeAt(i);
    }
    return bytes.buffer;
}

async function importPublicKey(publicKeyB64) {
    const keyBuffer = base64ToArrayBuffer(publicKeyB64);
    return window.crypto.subtle.importKey(
        'spki',
        keyBuffer,
        { name: 'RSA-OAEP', hash: 'SHA-256' },
        true,
        ['encrypt']
    );
}

async function readJsonSafely(response) {
    try {
        const clone = response.clone();
        return await clone.json();
    } catch (error) {
        console.debug('Failed to parse JSON response', error);
        return null;
    }
}

resetState();
updateUiState();
