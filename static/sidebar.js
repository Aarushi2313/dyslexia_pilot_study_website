// Sidebar Logic
document.addEventListener('DOMContentLoaded', function () {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    const toggleBtn = document.getElementById('sidebarToggle'); // Needs to be added to layout
    const closeBtn = document.getElementById('sidebarClose'); // Inside sidebar for mobile
    const collapseBtn = document.getElementById('sidebarCollapseBtn'); // Desktop collapse
    const mainWrapper = document.querySelector('.main-content-wrapper');

    // Restore Sidebar State
    if (localStorage.getItem('sidebar-collapsed') === 'true') {
        sidebar.classList.add('collapsed');
        if (mainWrapper) mainWrapper.classList.add('expanded');
    }

    // Toggle Sidebar (Desktop)
    if (collapseBtn) {
        collapseBtn.addEventListener('click', function () {
            sidebar.classList.toggle('collapsed');
            if (mainWrapper) mainWrapper.classList.toggle('expanded');

            const isCollapsed = sidebar.classList.contains('collapsed');
            localStorage.setItem('sidebar-collapsed', isCollapsed);
        });
    }

    // Toggle Sidebar (Mobile)
    if (toggleBtn) {
        toggleBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            sidebar.classList.toggle('open');
            if (overlay) overlay.classList.toggle('active');
        });
    }

    if (closeBtn) {
        closeBtn.addEventListener('click', function () {
            sidebar.classList.remove('open');
            if (overlay) overlay.classList.remove('active');
        });
    }

    if (overlay) {
        overlay.addEventListener('click', function () {
            sidebar.classList.remove('open');
            overlay.classList.remove('active');
        });
    }

    // Accordion Logic
    const groupHeaders = document.querySelectorAll('.nav-group-header');

    groupHeaders.forEach(header => {
        header.addEventListener('click', function (e) {
            // If it's a link to a page (has href other than #), allow default navigation
            // But if it's meant to be an accordion toggler, prevent default
            if (this.getAttribute('href') === '#' || this.getAttribute('href') === 'javascript:void(0)') {
                e.preventDefault();
                const parentItem = this.parentElement;

                // Toggle current
                parentItem.classList.toggle('expanded');

                // Optional: Close others? 
                // Currently keeping multiple open allowed as per standard dashboard UX
            }
        });
    });

    // Dynamic Subtask Fetching
    // We need USER_ID injected into the page globally
    if (typeof USER_ID !== 'undefined') {
        loadSubtasks('reading', `/api/reading-tasks/${USER_ID}`);
        loadSubtasks('typing', `/api/typing-tasks/${USER_ID}`);
        loadSubtasks('comprehension', `/api/reading-comprehension-tasks/${USER_ID}`);
        loadSubtasks('math', `/api/mathematical-comprehension-tasks/${USER_ID}`);
        loadSubtasks('writing', `/api/writing-tasks/${USER_ID}`);
        loadSubtasks('aptitude', `/api/aptitude-tasks/${USER_ID}`);
    }

    // Active State Highlighting
    highlightActiveLink();

    // Check if viewing as child
    if (sessionStorage.getItem('viewing_as_child') === 'true') {
        const backBtn = document.getElementById('backToParentItem');
        if (backBtn) backBtn.style.display = 'block';

        const backBtnDesktop = document.getElementById('backToParentNavDesktop');
        if (backBtnDesktop) backBtnDesktop.classList.remove('hidden');
    }
});

function switchBackToParent(e) {
    if (e) e.preventDefault();
    fetch('/api/switch-back-to-parent', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                // Clear the viewing_as_child flag and redirect to parent dashboard
                sessionStorage.removeItem('viewing_as_child');
                window.location.href = '/parent';
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Switch back error:', error);
            alert('An error occurred while switching back to parent');
        });
}

async function loadSubtasks(category, apiUrl) {
    const container = document.getElementById(`subtasks-${category}`);
    if (!container) return;

    try {
        const response = await fetch(apiUrl); // Check if this endpoint exists/matches
        // Provide fallback or check response status
        if (!response.ok) return;

        const data = await response.json();
        if (data.success && data.tasks && data.tasks.length > 0) {
            container.innerHTML = ''; // Clear loading placeholder

            data.tasks.forEach(task => {
                const link = document.createElement('a');
                // Construct URL - assuming standard naming convention or task specific ID
                // dashboard logic uses: task_dynamic safe_name
                // or specific pages like task1.html?task_id=...

                let href = '#';
                if (category === 'reading') {
                    href = `/task11.html?task_id=${task.id}`;
                } else if (category === 'typing') {
                    href = `/task22.html?task_id=${task.id}`;
                } else if (category === 'comprehension') {
                    href = `/task33.html?task_id=${task.id}`;
                } else if (category === 'math') {
                    href = `/task44.html?task_id=${task.id}`;
                } else if (category === 'writing') {
                    href = `/task55.html?task_id=${task.id}`;
                } else if (category === 'aptitude') {
                    href = `/aptitude.html?task_id=${task.id}`;
                }

                link.href = href;
                link.className = 'sub-nav-link task-link';
                link.setAttribute('data-task-name', task.task_name);
                link.textContent = task.task_name;
                container.appendChild(link);
            });
        } else {
            container.innerHTML = '<span class="sub-nav-link text-gray-400 italic">No tasks available</span>';
        }
    } catch (e) {
        console.log(`Failed to load ${category} subtasks`, e);
        // container.innerHTML = '<span class="sub-nav-link text-red-300">Error loading tasks</span>';
    }
}

function highlightActiveLink() {
    const currentPath = window.location.pathname;
    const links = document.querySelectorAll('.nav-link, .sub-nav-link');

    links.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');

            // If valid sub-link, expand parent
            const parentGroup = link.closest('.nav-item');
            if (parentGroup) {
                parentGroup.classList.add('expanded');
            }
        }
    });
}

// Global Logout Function
function handleLogout() {
    fetch('/api/logout', {
        method: 'POST',
        credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json' }
    })
        .then(res => res.json())
        .then(data => {
            localStorage.clear();
            window.location.href = '/';
        })
        .catch(() => {
            localStorage.clear();
            window.location.href = '/';
        });
}
