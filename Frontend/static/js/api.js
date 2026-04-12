const API_BASE = 'https://scriptly-jl4l.onrender.com/api';

function isTokenExpired(token) {
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        return payload.exp * 1000 < Date.now();
    } catch {
        return true;
    }
}

async function refreshAccessToken() {
    const refresh = localStorage.getItem('refresh_token');
    if (!refresh) return false;

    try {
        const response = await fetch('https://scriptly-jl4l.onrender.com/api/token/refresh/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh })
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('access_token', data.access);
            return true;
        }
        return false;
    } catch {
        return false;
    }
}

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
        const token = this.getToken();
        if (token && isTokenExpired(token)) {
            await refreshAccessToken();
        }

        const config = {
            method,
            headers: this.getHeaders()
        };
        if (data) config.body = JSON.stringify(data);

        try {
            const response = await fetch(`${API_BASE}${endpoint}`, config);

            if (response.status === 401) {
                const refreshed = await refreshAccessToken();
                if (refreshed) {
                    config.headers = this.getHeaders();
                    const retryResponse = await fetch(`${API_BASE}${endpoint}`, config);
                    const retryJson = await retryResponse.json();
                    return { status: retryResponse.status, data: retryJson };
                }
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

async function requireAuth() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = 'login.html';
        return;
    }
    if (isTokenExpired(token)) {
        const refreshed = await refreshAccessToken();
        if (!refreshed) {
            localStorage.clear();
            window.location.href = 'login.html';
        }
    }
}