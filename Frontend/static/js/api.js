const API_BASE = 'https://scriptly-jl4l.onrender.com/api';

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
        const config = {
            method,
            headers: this.getHeaders()
        };
        if (data) config.body = JSON.stringify(data);

        const response = await fetch(`${API_BASE}${endpoint}`, config);
        const json = await response.json();

        if (response.status === 401) {
            // Token expired — redirect to login
            localStorage.clear();
            window.location.href = 'login.html';
            return;
        }

        return { status: response.status, data: json };
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
    if (!localStorage.getItem('access_token')) {
        window.location.href = 'login.html';
    }
}