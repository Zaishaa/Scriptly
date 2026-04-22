const API_BASE = (window.location.hostname === 'localhost' || 
                  window.location.hostname === '127.0.0.1')
    ? 'http://127.0.0.1:8000/api'
    : 'https://scriptly-jl4l.onrender.com/api';

const api = {
    getToken() {
        return localStorage.getItem('access_token');
    },

    getHeaders() {
        return {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.getToken()}`
        };
    },

    async request(method, endpoint, data = null) {
        const config = { method, headers: this.getHeaders() };
        if (data) config.body = JSON.stringify(data);

        try {
            const response = await fetch(`${API_BASE}${endpoint}`, config);
            if (response.status === 401) {
                localStorage.clear();
                window.location.href = 'login.html';
                return;
            }
            const json = await response.json();
            return { status: response.status, data: json };
        } catch (err) {
            console.error('API Error:', err);
            throw err;
        }
    },

    get(endpoint) { return this.request('GET', endpoint); },
    post(endpoint, data) { return this.request('POST', endpoint, data); },
    put(endpoint, data) { return this.request('PUT', endpoint, data); },
    delete(endpoint) { return this.request('DELETE', endpoint); }
};

function logout() {
    localStorage.clear();
    window.location.href = 'login.html';
}

function requireAuth() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = 'login.html';
    }
}