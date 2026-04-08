// ──────────────────────────────────────────────
// shared/api.js — Fetch wrapper with JWT injection
// All API calls go through this module
// ──────────────────────────────────────────────

// In development: http://localhost:8000
// In production: your Render backend URL (update after deploying to Render)
const API_BASE = window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : 'https://dh308-prototype-1.onrender.com';


/**
 * Make an authenticated API request.
 * Automatically injects JWT from localStorage.
 */
async function apiRequest(endpoint, options = {}) {
    const token = localStorage.getItem('medicore_token');

    const headers = {
        ...(options.headers || {})
    };

    // Add auth header if token exists
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    // Add JSON content-type if body is an object (not FormData)
    if (options.body && !(options.body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
        options.body = JSON.stringify(options.body);
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers
    });

    // Handle 401 — redirect to login
    if (response.status === 401) {
        localStorage.removeItem('medicore_token');
        localStorage.removeItem('medicore_refresh');
        localStorage.removeItem('medicore_role');
        localStorage.removeItem('medicore_user_id');
        const base = window.location.pathname.startsWith('/app') ? '/app' : '';
        window.location.href = `${base}/index.html`;
        return;
    }

    return response;
}

/**
 * GET request shorthand
 */
async function apiGet(endpoint) {
    const res = await apiRequest(endpoint);
    if (!res) return null;
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'Request failed');
    }
    return res.json();
}

/**
 * POST request shorthand (JSON body)
 */
async function apiPost(endpoint, data) {
    const res = await apiRequest(endpoint, {
        method: 'POST',
        body: data
    });
    if (!res) return null;
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'Request failed');
    }
    return res.json();
}

/**
 * PUT request shorthand
 */
async function apiPut(endpoint, data) {
    const res = await apiRequest(endpoint, {
        method: 'PUT',
        body: data
    });
    if (!res) return null;
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'Request failed');
    }
    return res.json();
}

/**
 * PATCH request shorthand
 */
async function apiPatch(endpoint, data) {
    const res = await apiRequest(endpoint, {
        method: 'PATCH',
        body: data
    });
    if (!res) return null;
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'Request failed');
    }
    return res.json();
}

/**
 * DELETE request shorthand
 */
async function apiDelete(endpoint) {
    const res = await apiRequest(endpoint, { method: 'DELETE' });
    if (!res) return null;
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'Request failed');
    }
    return res.json();
}

/**
 * POST with FormData (for file uploads)
 */
async function apiUpload(endpoint, formData) {
    const res = await apiRequest(endpoint, {
        method: 'POST',
        body: formData
    });
    if (!res) return null;
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'Upload failed');
    }
    return res.json();
}
