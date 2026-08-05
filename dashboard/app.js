// RKTC Dashboard

let allCategories = [];
let selectedCategories = new Set();
let currentTheme = 'light';

// DOM Elements
const searchInput = document.getElementById('searchInput');
const startDate = document.getElementById('startDate');
const endDate = document.getElementById('endDate');
const resetFilters = document.getElementById('resetFilters');
const showReplies = document.getElementById('showReplies');
const categoryList = document.getElementById('categoryList');
const selectAll = document.getElementById('selectAll');
const messagesContainer = document.getElementById('messagesContainer');
const viewTitle = document.getElementById('viewTitle');
const viewSubtitle = document.getElementById('viewSubtitle');
const statsText = document.getElementById('statsText');
const themeToggle = document.getElementById('themeToggle');
const moonIcon = document.getElementById('moonIcon');
const sunIcon = document.getElementById('sunIcon');

// Initialize
async function init() {
    loadTheme();
    bindEvents();
    await loadData();
}

function bindEvents() {
    themeToggle.addEventListener('click', toggleTheme);
    searchInput.addEventListener('input', debounce(renderMessages, 150));
    startDate.addEventListener('change', renderMessages);
    endDate.addEventListener('change', renderMessages);
    showReplies.addEventListener('change', renderMessages);
    resetFilters.addEventListener('click', resetAllFilters);
    selectAll.addEventListener('click', toggleSelectAll);
}

async function loadData() {
    try {
        const res = await fetch('/api/messages');
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        allCategories = await res.json();
        selectedCategories = new Set(allCategories.map(c => c.category_id));
        renderCategories();
        renderMessages();
    } catch (err) {
        console.error(err);
        messagesContainer.innerHTML = `
            <div class="text-center py-12">
                <div class="text-destructive font-medium mb-2">Error loading data</div>
                <div class="text-sm text-muted-foreground">${escapeHtml(err.message)}</div>
                <div class="text-xs text-muted-foreground mt-4">Make sure the server is running and category_messages.json exists.</div>
            </div>
        `;
        categoryList.innerHTML = `<div class="text-sm text-muted-foreground">No categories loaded</div>`;
        updateStats(0, 0, 0);
    }
}

// Theme
function loadTheme() {
    const saved = localStorage.getItem('rktc-theme') || 'light';
    setTheme(saved);
}

function setTheme(theme) {
    currentTheme = theme;
    if (theme === 'dark') {
        document.documentElement.classList.add('dark');
        moonIcon.classList.add('hidden');
        sunIcon.classList.remove('hidden');
    } else {
        document.documentElement.classList.remove('dark');
        moonIcon.classList.remove('hidden');
        sunIcon.classList.add('hidden');
    }
    localStorage.setItem('rktc-theme', theme);
}

function toggleTheme() {
    setTheme(currentTheme === 'light' ? 'dark' : 'light');
}

// Categories
function renderCategories() {
    categoryList.innerHTML = '';
    const allSelected = selectedCategories.size === allCategories.length && allCategories.length > 0;
    selectAll.textContent = allSelected ? 'Deselect all' : 'Select all';

    allCategories.forEach(cat => {
        const label = document.createElement('label');
        label.className = 'flex items-center gap-3 px-2 py-2 rounded-md hover:bg-accent cursor-pointer transition-colors group';
        const checked = selectedCategories.has(cat.category_id);
        label.innerHTML = `
            <input type="checkbox" value="${cat.category_id}" class="h-4 w-4 rounded border-border bg-background text-primary focus:ring-2 focus:ring-ring" ${checked ? 'checked' : ''}>
            <span class="text-sm flex-1 truncate text-foreground">${escapeHtml(cat.category_name)}</span>
            <span class="text-xs text-muted-foreground bg-secondary px-2 py-0.5 rounded-full shrink-0">${cat.messages.length}</span>
        `;
        const checkbox = label.querySelector('input');
        checkbox.addEventListener('change', () => {
            if (checkbox.checked) selectedCategories.add(cat.category_id);
            else selectedCategories.delete(cat.category_id);
            renderCategories();
            renderMessages();
        });
        categoryList.appendChild(label);
    });

    if (allCategories.length === 0) {
        categoryList.innerHTML = `<div class="text-sm text-muted-foreground">No categories found</div>`;
    }
}

function toggleSelectAll() {
    const allSelected = selectedCategories.size === allCategories.length;
    if (allSelected) {
        selectedCategories.clear();
    } else {
        selectedCategories = new Set(allCategories.map(c => c.category_id));
    }
    renderCategories();
    renderMessages();
}

// Filtering
function getFilterState() {
    const query = searchInput.value.trim().toLowerCase();
    const start = startDate.value ? new Date(startDate.value).setHours(0, 0, 0, 0) : null;
    const end = endDate.value ? new Date(endDate.value).setHours(23, 59, 59, 999) : null;
    return { query, start, end };
}

function matchesFilters(item, { query, start, end }) {
    const ts = new Date(item.timestamp).getTime();
    if (start && ts < start) return false;
    if (end && ts > end) return false;
    if (query) {
        const text = (item.text || '').toLowerCase();
        const keywords = (item.keywords || '').toLowerCase();
        if (!text.includes(query) && !keywords.includes(query)) return false;
    }
    return true;
}

function getFilteredCategories() {
    return allCategories.filter(cat => selectedCategories.has(cat.category_id));
}

function buildTimeline() {
    const { query, start, end } = getFilterState();
    const thread = showReplies.checked;
    const categories = getFilteredCategories();
    const visibleParents = [];
    let totalVisible = 0;

    categories.forEach(cat => {
        cat.messages.forEach(msg => {
            const parentMatches = matchesFilters(msg, { query, start, end });
            const visibleReplies = (msg.replies || []).filter(reply => matchesFilters(reply, { query, start, end }));
            const showReplies = thread ? visibleReplies : [];
            const showParent = parentMatches || visibleReplies.length > 0;

            if (showParent) {
                const item = {
                    ...msg,
                    category_id: cat.category_id,
                    category_name: cat.category_name,
                    replies: showReplies
                };
                visibleParents.push(item);
                totalVisible += 1 + showReplies.length;
            }
        });
    });

    visibleParents.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
    return { items: visibleParents, totalVisible };
}

// Rendering
function renderMessages() {
    const categories = getFilteredCategories();
    const { items, totalVisible } = buildTimeline();

    updateStats(totalVisible, items.length, categories.length);
    updateViewTitle(categories);

    if (items.length === 0) {
        messagesContainer.innerHTML = `
            <div class="text-center py-16">
                <div class="text-4xl mb-4">📭</div>
                <div class="text-muted-foreground font-medium">No messages match your filters</div>
                <div class="text-xs text-muted-foreground mt-2">Try adjusting search, dates, or categories</div>
            </div>
        `;
        return;
    }

    messagesContainer.innerHTML = '';
    items.forEach((msg, index) => {
        const el = createMessageElement(msg, false);
        messagesContainer.appendChild(el);

        if (showReplies.checked && msg.replies && msg.replies.length > 0) {
            const threadContainer = document.createElement('div');
            threadContainer.className = 'ml-8 md:ml-12 pl-4 border-l-2 border-border space-y-3 mt-2';
            msg.replies.forEach(reply => {
                threadContainer.appendChild(createMessageElement(reply, true));
            });
            messagesContainer.appendChild(threadContainer);
        }

        // Date divider between different days
        if (index < items.length - 1) {
            const currentDay = new Date(msg.timestamp).toDateString();
            const nextDay = new Date(items[index + 1].timestamp).toDateString();
            if (currentDay !== nextDay) {
                const divider = document.createElement('div');
                divider.className = 'relative flex items-center py-2';
                divider.innerHTML = `
                    <div class="flex-grow border-t border-border"></div>
                    <span class="mx-4 text-xs text-muted-foreground">${formatDate(items[index + 1].timestamp)}</span>
                    <div class="flex-grow border-t border-border"></div>
                `;
                messagesContainer.appendChild(divider);
            }
        }
    });
}

function createMessageElement(msg, isReply) {
    const wrapper = document.createElement('div');
    wrapper.className = isReply ? 'reply-item' : 'message-item';

    const bubble = document.createElement('div');
    bubble.className = `max-w-full rounded-lg border border-border bg-card p-4 shadow-sm ${isReply ? 'reply-bubble' : ''}`;

    const header = document.createElement('div');
    header.className = 'flex flex-wrap items-center gap-2 mb-2';

    const categoryBadge = document.createElement('span');
    categoryBadge.className = 'inline-flex items-center rounded-full border border-transparent bg-primary px-2.5 py-0.5 text-xs font-semibold text-primary-foreground transition-colors';
    categoryBadge.textContent = msg.category_name || 'Unknown';

    const time = document.createElement('span');
    time.className = 'text-xs text-muted-foreground';
    time.textContent = formatDateTime(msg.timestamp);

    const typeBadge = document.createElement('span');
    typeBadge.className = 'text-xs text-muted-foreground bg-secondary px-2 py-0.5 rounded-full';
    typeBadge.textContent = isReply ? 'reply' : (msg.context || 'main');

    header.appendChild(categoryBadge);
    header.appendChild(time);
    header.appendChild(typeBadge);

    const text = document.createElement('div');
    text.className = 'text-sm leading-relaxed message-text whitespace-pre-wrap';
    text.textContent = msg.text || '(No text)';

    bubble.appendChild(header);
    bubble.appendChild(text);

    if (msg.keywords) {
        const keywords = document.createElement('div');
        keywords.className = 'mt-3 flex flex-wrap gap-1';
        msg.keywords.split(',').forEach(k => {
            const kw = k.trim();
            if (!kw) return;
            const span = document.createElement('span');
            span.className = 'inline-flex items-center rounded-md border border-border bg-secondary px-2 py-1 text-xs font-medium text-secondary-foreground';
            span.textContent = kw;
            keywords.appendChild(span);
        });
        bubble.appendChild(keywords);
    }

    if (msg.id) {
        const footer = document.createElement('div');
        footer.className = 'mt-2 text-[10px] text-muted-foreground/60';
        footer.textContent = `ID: ${msg.id}`;
        bubble.appendChild(footer);
    }

    wrapper.appendChild(bubble);
    return wrapper;
}

function updateViewTitle(categories) {
    const count = categories.length;
    if (count === 0) {
        viewTitle.textContent = 'No categories selected';
        viewSubtitle.textContent = 'Select a category from the sidebar';
    } else if (count === allCategories.length) {
        viewTitle.textContent = 'All Categories';
        viewSubtitle.textContent = 'Combined timeline sorted by timestamp';
    } else if (count === 1) {
        viewTitle.textContent = categories[0].category_name;
        viewSubtitle.textContent = 'Single category view';
    } else {
        viewTitle.textContent = `${count} Categories`;
        viewSubtitle.textContent = 'Combined timeline sorted by timestamp';
    }
}

function updateStats(visible, parents, categories) {
    const total = allCategories.reduce((sum, c) => sum + c.messages.length, 0);
    const replyTotal = allCategories.reduce((sum, c) => sum + c.messages.reduce((r, m) => r + (m.replies || []).length, 0), 0);
    statsText.innerHTML = `Showing ${visible} messages (${parents} parents, ${visible - parents} replies) from ${categories} categories. Total dataset: ${total} parents, ${replyTotal} replies.`;
}

function resetAllFilters() {
    searchInput.value = '';
    startDate.value = '';
    endDate.value = '';
    showReplies.checked = true;
    selectedCategories = new Set(allCategories.map(c => c.category_id));
    renderCategories();
    renderMessages();
}

// Utilities
function escapeHtml(text) {
    if (text == null) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDateTime(iso) {
    try {
        return new Date(iso).toLocaleString('fa-IR', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch {
        return iso;
    }
}

function formatDate(iso) {
    try {
        return new Date(iso).toLocaleDateString('fa-IR', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    } catch {
        return iso;
    }
}

function debounce(fn, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => fn.apply(this, args), wait);
    };
}

// Start
init();
