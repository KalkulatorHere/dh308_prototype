// ──────────────────────────────────────────────
// shared/components.js — Reusable UI component helpers
// Sidebar navigation, status pills, notifications
// ──────────────────────────────────────────────

/**
 * Generate the sidebar HTML for a given role.
 * Returns an HTML string to be injected into a container.
 */
function getSidebar(role, activePage) {
    const menus = {
        patient: [
            { href: '/app/patient/dashboard.html', icon: 'layout-dashboard', label: 'Dashboard' },
            { href: '/app/patient/timeline.html', icon: 'clock', label: 'Timeline' },
            { href: '/app/patient/prescriptions.html', icon: 'pill', label: 'Prescriptions' },
            { href: '/app/patient/labs.html', icon: 'flask-conical', label: 'Lab Reports' },
            { href: '/app/patient/consent.html', icon: 'shield-check', label: 'Consents' },
            { href: '/app/patient/appointments.html', icon: 'calendar', label: 'Appointments' },
            { href: '/app/patient/profile.html', icon: 'user', label: 'Profile' },
        ],
        doctor: [
            { href: '/app/doctor/dashboard.html', icon: 'layout-dashboard', label: 'Dashboard' },
            { href: '/app/doctor/patient-view.html', icon: 'users', label: 'Patients' },
            { href: '/app/doctor/notes.html', icon: 'file-text', label: 'Clinical Notes' },
            { href: '/app/doctor/prescribe.html', icon: 'pill', label: 'Prescribe' },
            { href: '/app/doctor/schedule.html', icon: 'calendar', label: 'Schedule' },
        ],
        lab_tech: [
            { href: '/app/lab/queue.html', icon: 'list-todo', label: 'Queue' },
            { href: '/app/lab/upload.html', icon: 'upload', label: 'Upload Report' },
        ],
        admin: [
            { href: '/app/admin/dashboard.html', icon: 'layout-dashboard', label: 'Dashboard' },
            { href: '/app/admin/users.html', icon: 'users', label: 'Users' },
            { href: '/app/admin/audit.html', icon: 'shield', label: 'Audit Logs' },
        ]
    };

    const items = menus[role] || [];
    
    let html = `
    <aside class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <div class="logo">
                <i data-lucide="heart-pulse" class="logo-icon"></i>
                <span class="logo-text">MediCore</span>
            </div>
        </div>
        <nav class="sidebar-nav">`;

    items.forEach(item => {
        const isActive = activePage === item.label.toLowerCase().replace(/\s+/g, '-');
        html += `
            <a href="${item.href}" class="nav-item ${isActive ? 'active' : ''}">
                <i data-lucide="${item.icon}"></i>
                <span>${item.label}</span>
            </a>`;
    });

    html += `
        </nav>
        <div class="sidebar-footer">
            <button onclick="logout()" class="nav-item logout-btn">
                <i data-lucide="log-out"></i>
                <span>Logout</span>
            </button>
        </div>
    </aside>`;

    return html;
}

/**
 * Get a status pill HTML for a given status string
 */
function statusPill(status) {
    const colors = {
        active: 'bg-emerald-500/20 text-emerald-400',
        approved: 'bg-emerald-500/20 text-emerald-400',
        completed: 'bg-blue-500/20 text-blue-400',
        scheduled: 'bg-blue-500/20 text-blue-400',
        pending: 'bg-amber-500/20 text-amber-400',
        cancelled: 'bg-red-500/20 text-red-400',
        denied: 'bg-red-500/20 text-red-400',
        revoked: 'bg-red-500/20 text-red-400',
        no_show: 'bg-gray-500/20 text-gray-400',
    };
    const cls = colors[status] || 'bg-gray-500/20 text-gray-400';
    return `<span class="inline-flex items-center rounded-full px-3 py-1 text-xs font-medium ${cls}">${status}</span>`;
}

/**
 * Initialize Lucide icons (call after DOM loads)
 */
function initIcons() {
    if (window.lucide) {
        lucide.createIcons();
    }
}

/**
 * Show a toast notification
 */
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    const bgColor = type === 'error' ? 'bg-red-500' : type === 'warning' ? 'bg-amber-500' : 'bg-emerald-500';
    toast.className = `fixed top-4 right-4 ${bgColor} text-white px-6 py-3 rounded-lg shadow-lg z-50 transform transition-all duration-300 translate-y-0 opacity-100`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.classList.add('opacity-0', '-translate-y-2');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

/**
 * Empty state placeholder
 */
function emptyState(message, icon = 'inbox') {
    return `
    <div class="flex flex-col items-center justify-center py-16 text-gray-500">
        <i data-lucide="${icon}" class="w-16 h-16 mb-4 opacity-30"></i>
        <p class="text-lg">${message}</p>
    </div>`;
}
