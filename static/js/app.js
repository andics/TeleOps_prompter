/**
 * Main Application JavaScript
 * Handles UI interactions, theme toggling, and API communication
 */

// ==================== State Management ====================
const state = {
    theme: localStorage.getItem('theme') || 'light',
    filters: [],
    latestFrame: null,
    updateInterval: null
};

// ==================== Theme Management ====================
function initTheme() {
    document.documentElement.setAttribute('data-theme', state.theme);
    
    const themeToggle = document.getElementById('themeToggle');
    themeToggle.addEventListener('click', () => {
        state.theme = state.theme === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', state.theme);
        localStorage.setItem('theme', state.theme);
    });
}

// ==================== Frame Updates ====================
async function updateLatestFrame() {
    try {
        const response = await fetch('/api/latest-frame');
        const data = await response.json();
        
        if (data.success && data.image) {
            const frameImg = document.getElementById('latestFrame');
            const framePlaceholder = document.querySelector('.frame-placeholder');
            const frameStatus = document.getElementById('frameStatus');
            
            // Force image reload by adding timestamp to prevent caching
            frameImg.src = data.image;
            frameImg.classList.add('loaded');
            framePlaceholder.style.display = 'none';
            frameStatus.classList.add('active');
            
            state.latestFrame = data.path;
            
            // Debug: log frame updates
            if (data.timestamp) {
                const frameTime = new Date(data.timestamp * 1000);
                console.log(`Frame updated: ${data.path} (${frameTime.toLocaleTimeString()})`);
            }
        } else {
            console.warn('No frame available:', data.error);
        }
    } catch (error) {
        console.error('Error fetching latest frame:', error);
    }
}

// ==================== Filter Management ====================
async function loadFilters() {
    try {
        const response = await fetch('/api/filters');
        const data = await response.json();
        
        if (data.success) {
            state.filters = data.filters;
            renderFilters();
        }
    } catch (error) {
        console.error('Error loading filters:', error);
    }
}

function renderFilters() {
    const filtersList = document.getElementById('filtersList');
    
    if (state.filters.length === 0) {
        filtersList.innerHTML = `
            <div class="filter-placeholder" style="text-align: center; padding: 2rem; color: var(--text-muted);">
                <p>No filters yet. Add a filter above to get started!</p>
            </div>
        `;
        return;
    }
    
    filtersList.innerHTML = state.filters.map(filter => createFilterHTML(filter)).join('');
    
    // Add event listeners
    attachFilterEventListeners();
}

function createFilterHTML(filter) {
    const activeClass = filter.is_active ? 'active' : '';
    
    // Determine result display and styling
    let resultText = 'Waiting...';
    let resultClass = '';
    
    if (filter.result !== null && filter.result !== undefined) {
        resultText = filter.result;
        
        // Check if result indicates true/false for styling
        const resultLower = String(filter.result).toLowerCase();
        if (resultLower.includes('true') || resultLower.includes('yes')) {
            resultClass = 'result-true';
        } else if (resultLower.includes('false') || resultLower.includes('no')) {
            resultClass = 'result-false';
        }
    }
    
    // Format timestamp if available
    let timestampDisplay = '';
    if (filter.timestamp) {
        timestampDisplay = filter.timestamp;
    }
    
    return `
        <div class="filter-block" data-filter-id="${filter.id}">
            <div class="filter-header">
                <div class="filter-prompt">${escapeHtml(filter.prompt)}</div>
                <div class="filter-status-switch ${activeClass}" 
                     data-action="toggle" 
                     data-filter-id="${filter.id}">
                </div>
            </div>
            
            <!-- GPT Response Box -->
            <div class="filter-response-box ${resultClass}">
                <div class="response-label">GPT Response:</div>
                <div class="response-text">${escapeHtml(resultText)}</div>
                ${timestampDisplay ? `<div class="response-timestamp">${escapeHtml(timestampDisplay)}</div>` : ''}
            </div>
            
            <div class="filter-controls">
                <button class="filter-btn move-up" 
                        data-action="move-up" 
                        data-filter-id="${filter.id}"
                        title="Move Up">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="18 15 12 9 6 15"></polyline>
                    </svg>
                </button>
                <button class="filter-btn move-down" 
                        data-action="move-down" 
                        data-filter-id="${filter.id}"
                        title="Move Down">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="6 9 12 15 18 9"></polyline>
                    </svg>
                </button>
                <button class="filter-btn remove" 
                        data-action="remove" 
                        data-filter-id="${filter.id}"
                        title="Remove">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            </div>
        </div>
    `;
}

function attachFilterEventListeners() {
    // Toggle switches
    document.querySelectorAll('[data-action="toggle"]').forEach(el => {
        el.addEventListener('click', async (e) => {
            const filterId = e.currentTarget.dataset.filterId;
            await toggleFilter(filterId);
        });
    });
    
    // Move up buttons
    document.querySelectorAll('[data-action="move-up"]').forEach(el => {
        el.addEventListener('click', async (e) => {
            const filterId = e.currentTarget.dataset.filterId;
            await moveFilter(filterId, -1);
        });
    });
    
    // Move down buttons
    document.querySelectorAll('[data-action="move-down"]').forEach(el => {
        el.addEventListener('click', async (e) => {
            const filterId = e.currentTarget.dataset.filterId;
            await moveFilter(filterId, 1);
        });
    });
    
    // Remove buttons
    document.querySelectorAll('[data-action="remove"]').forEach(el => {
        el.addEventListener('click', async (e) => {
            const filterId = e.currentTarget.dataset.filterId;
            await removeFilter(filterId);
        });
    });
}

async function addFilter() {
    const promptInput = document.getElementById('newFilterPrompt');
    const prompt = promptInput.value.trim();
    
    if (!prompt) {
        alert('Please enter a filter prompt');
        return;
    }
    
    try {
        const response = await fetch('/api/filters', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ prompt })
        });
        
        const data = await response.json();
        
        if (data.success) {
            promptInput.value = '';
            await loadFilters();
            addChatMessage(`Filter added: "${prompt.substring(0, 50)}${prompt.length > 50 ? '...' : ''}"`, 'system');
        }
    } catch (error) {
        console.error('Error adding filter:', error);
        alert('Failed to add filter');
    }
}

async function removeFilter(filterId) {
    try {
        const response = await fetch(`/api/filters/${filterId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            await loadFilters();
            addChatMessage('Filter removed', 'system');
        }
    } catch (error) {
        console.error('Error removing filter:', error);
    }
}

async function moveFilter(filterId, direction) {
    try {
        const response = await fetch(`/api/filters/${filterId}/move`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ direction })
        });
        
        if (response.ok) {
            await loadFilters();
        }
    } catch (error) {
        console.error('Error moving filter:', error);
    }
}

async function toggleFilter(filterId) {
    try {
        const response = await fetch(`/api/filters/${filterId}/toggle`, {
            method: 'POST'
        });
        
        if (response.ok) {
            await loadFilters();
        }
    } catch (error) {
        console.error('Error toggling filter:', error);
    }
}

// ==================== Chat Management ====================
function addChatMessage(message, type = 'user') {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${type}-message`;
    
    const p = document.createElement('p');
    p.textContent = message;
    messageDiv.appendChild(p);
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function sendChatMessage() {
    const chatInput = document.getElementById('chatInput');
    const message = chatInput.value.trim();
    
    if (!message) {
        return;
    }
    
    addChatMessage(message, 'user');
    chatInput.value = '';
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });
        
        const data = await response.json();
        
        if (data.success && data.response) {
            addChatMessage(data.response, 'system');
        }
    } catch (error) {
        console.error('Error sending chat message:', error);
        addChatMessage('Error sending message', 'system');
    }
}

// ==================== Utility Functions ====================
function escapeHtml(text) {
    if (text === null || text === undefined) {
        return '';
    }
    const div = document.createElement('div');
    div.textContent = String(text);
    return div.innerHTML;
}

// ==================== Auto-Update Loop ====================
function startAutoUpdate() {
    // Update frame every 2 seconds
    updateLatestFrame();
    setInterval(updateLatestFrame, 2000);
    
    // Update filters every 3 seconds (matches backend evaluation interval)
    loadFilters();
    setInterval(loadFilters, 3000);
}

// ==================== Initialization ====================
document.addEventListener('DOMContentLoaded', () => {
    // Initialize theme
    initTheme();
    
    // Set up event listeners
    document.getElementById('addFilterBtn').addEventListener('click', addFilter);
    document.getElementById('sendChatBtn').addEventListener('click', sendChatMessage);
    
    // Enter key to add filter
    document.getElementById('newFilterPrompt').addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'Enter') {
            addFilter();
        }
    });
    
    // Enter key to send chat message
    document.getElementById('chatInput').addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'Enter') {
            sendChatMessage();
        }
    });
    
    // Start auto-update
    startAutoUpdate();
    
    // Welcome message
    addChatMessage('System initialized. Camera feed monitoring started. GPT-4o will evaluate filters every 3 seconds.', 'system');
});
