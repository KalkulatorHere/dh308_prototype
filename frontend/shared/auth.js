// ──────────────────────────────────────────────
// shared/auth.js — Authentication helpers
// Token management, role decoding, route guards
// ──────────────────────────────────────────────

/**
 * Save tokens and user info after login/register
 */
function saveAuth(data) {
    localStorage.setItem('medicore_token', data.access_token);
    localStorage.setItem('medicore_refresh', data.refresh_token);
    localStorage.setItem('medicore_role', data.role);
    localStorage.setItem('medicore_user_id', data.user_id);
}

/**
 * Get the current JWT access token
 */
function getToken() {
    return localStorage.getItem('medicore_token');
}

/**
 * Get the current user's role
 */
function getRole() {
    return localStorage.getItem('medicore_role');
}

/**
 * Get the current user's ID
 */
function getUserId() {
    return parseInt(localStorage.getItem('medicore_user_id'));
}

/**
 * Check if user is logged in
 */
function isLoggedIn() {
    return !!getToken();
}

/**
 * Decode JWT payload (without verification — client-side only)
 */
function decodeToken() {
    const token = getToken();
    if (!token) return null;
    try {
        const payload = token.split('.')[1];
        return JSON.parse(atob(payload));
    } catch {
        return null;
    }
}

/**
 * Logout — clear all stored auth data and redirect
 */
function logout() {
    localStorage.removeItem('medicore_token');
    localStorage.removeItem('medicore_refresh');
    localStorage.removeItem('medicore_role');
    localStorage.removeItem('medicore_user_id');
    const base = window.location.pathname.startsWith('/app') ? '/app' : '';
    window.location.href = `${base}/index.html`;
}

/**
 * Guard a route — redirect if not logged in or wrong role
 * @param {string[]} allowedRoles — array of roles allowed on this page
 */
function guardRoute(allowedRoles) {
    if (!isLoggedIn()) {
        const base = window.location.pathname.startsWith('/app') ? '/app' : '';
        window.location.href = `${base}/index.html`;
        return false;
    }
    const role = getRole();
    if (allowedRoles && !allowedRoles.includes(role)) {
        // Redirect to the correct dashboard based on role
        redirectToDashboard();
        return false;
    }
    return true;
}

/**
 * Redirect user to their role-appropriate dashboard
 */
function redirectToDashboard() {
    const role = getRole();
    const base = window.location.pathname.startsWith('/app') ? '/app' : '';
    
    switch (role) {
        case 'patient':
            window.location.href = `${base}/patient/dashboard.html`;
            break;
        case 'doctor':
            window.location.href = `${base}/doctor/dashboard.html`;
            break;
        case 'lab_tech':
            window.location.href = `${base}/lab/queue.html`;
            break;
        case 'admin':
            window.location.href = `${base}/admin/dashboard.html`;
            break;
        default:
            window.location.href = `${base}/index.html`;
    }
}

/**
 * Format a date string for display
 */
function formatDate(dateStr) {
    if (!dateStr) return '—';
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
}

/**
 * Format a datetime string for display
 */
function formatDateTime(dateStr) {
    if (!dateStr) return '—';
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}
