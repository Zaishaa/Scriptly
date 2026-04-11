// LOGIN
const loginForm = document.getElementById('login-form');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = document.getElementById('login-btn');
        const errorDiv = document.getElementById('error-msg');

        btn.textContent = 'Signing in...';
        btn.disabled = true;
        errorDiv.classList.add('hidden');

        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        try {
            const response = await fetch('http://127.0.0.1:8000/api/accounts/login/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            const data = await response.json();

            if (response.ok) {
                localStorage.setItem('access_token', data.tokens.access);
                localStorage.setItem('refresh_token', data.tokens.refresh);
                localStorage.setItem('user', JSON.stringify(data.user));
                window.location.href = 'dashboard.html';
            } else {
                errorDiv.textContent = data.error || 'Login failed. Please try again.';
                errorDiv.classList.remove('hidden');
            }
        } catch (err) {
            errorDiv.textContent = 'Server error. Make sure the backend is running.';
            errorDiv.classList.remove('hidden');
        }

        btn.textContent = 'Sign In';
        btn.disabled = false;
    });
}

// REGISTER
const registerForm = document.getElementById('register-form');
if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = document.getElementById('register-btn');
        const errorDiv = document.getElementById('error-msg');
        const successDiv = document.getElementById('success-msg');

        btn.textContent = 'Creating account...';
        btn.disabled = true;
        errorDiv.classList.add('hidden');
        successDiv.classList.add('hidden');

        const data = {
            email: document.getElementById('email').value,
            username: document.getElementById('username').value,
            password: document.getElementById('password').value,
            password2: document.getElementById('password2').value,
            first_name: document.getElementById('first_name').value,
            last_name: document.getElementById('last_name').value,
        };

        try {
            const response = await fetch('http://127.0.0.1:8000/api/accounts/register/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok) {
                localStorage.setItem('access_token', result.tokens.access);
                localStorage.setItem('refresh_token', result.tokens.refresh);
                localStorage.setItem('user', JSON.stringify(result.user));
                successDiv.textContent = 'Account created! Redirecting...';
                successDiv.classList.remove('hidden');
                setTimeout(() => window.location.href = 'dashboard.html', 1500);
            } else {
                const errors = Object.values(result).flat().join(' ');
                errorDiv.textContent = errors || 'Registration failed.';
                errorDiv.classList.remove('hidden');
            }
        } catch (err) {
            errorDiv.textContent = 'Server error. Make sure the backend is running.';
            errorDiv.classList.remove('hidden');
        }

        btn.textContent = 'Create Account';
        btn.disabled = false;
    });
}