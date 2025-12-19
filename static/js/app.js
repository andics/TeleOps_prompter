/**
 * TeleOps - AI Vision Monitor
 * Real-time camera feeds with AI filter evaluation
 */

// ==================== State Management ====================
const state = {
    theme: localStorage.getItem('theme') || 'dark',
    filters: [],
    logs: [],
    cameras: {
        A: { lastTimestamp: null },
        B: { lastTimestamp: null },
        C: { lastTimestamp: null }
    },
    frameUpdateInterval: null,
    filterUpdateInterval: null,
    logUpdateInterval: null,
    captureInterval: 3000,
    lastFiltersJSON: null,
    lastLogsLength: 0
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

// ==================== Config Loading ====================
async function loadConfig() {
    try {
        const response = await fetch('/api/config');
        const data = await response.json();
        
        if (data.success && data.capture_interval) {
            state.captureInterval = data.capture_interval * 1000;
            
            const updateInfo = document.getElementById('updateInfo');
            if (updateInfo) {
                updateInfo.textContent = `Updating every ${data.capture_interval}s`;
            }
        }
    } catch (error) {
        console.error('[TeleOps] Error loading config:', error);
    }
    
    return state.captureInterval;
}

// ==================== Frame Updates ====================
async function updateCameraFrame(cameraId) {
    try {
        const response = await fetch(`/api/latest-frame/${cameraId}`);
        const data = await response.json();
        
        if (data.success && data.image) {
            const frameImg = document.getElementById(`frame${cameraId}`);
            const placeholder = frameImg?.parentElement?.querySelector('.frame-placeholder-small');
            
            if (frameImg && data.timestamp !== state.cameras[cameraId].lastTimestamp) {
                frameImg.src = data.image;
                frameImg.classList.add('loaded');
                if (placeholder) placeholder.style.display = 'none';
                
                state.cameras[cameraId].lastTimestamp = data.timestamp;
            }
        }
    } catch (error) {
        console.error(`[TeleOps] Error fetching Camera ${cameraId}:`, error);
    }
}

async function updateAllCameras() {
    // Update all three cameras in parallel
    await Promise.all([
        updateCameraFrame('A'),
        updateCameraFrame('B'),
        updateCameraFrame('C')
    ]);
}

// ==================== Log Management ====================
async function loadLogs() {
    try {
        const response = await fetch('/api/logs');
        const data = await response.json();
        
        if (data.success && data.logs) {
            if (data.logs.length !== state.lastLogsLength) {
                state.logs = data.logs;
                state.lastLogsLength = data.logs.length;
                renderLogs();
            }
        }
    } catch (error) {
        console.error('[TeleOps] Error loading logs:', error);
    }
}

function renderLogs() {
    const logContainer = document.getElementById('logContainer');
    
    if (state.logs.length === 0) {
        logContainer.innerHTML = `
            <div style="text-align: center; padding: 2rem; color: var(--text-muted);">
                <p>No activity yet...</p>
            </div>
        `;
        return;
    }
    
    const reversedLogs = [...state.logs].reverse();
    logContainer.innerHTML = reversedLogs.map(log => createLogEntryHTML(log)).join('');
    logContainer.scrollTop = 0;
}

function createLogEntryHTML(log) {
    const typeLabels = {
        info: 'INFO',
        success: 'OK',
        error: 'ERR',
        warning: 'WARN',
        vlm: 'VLM',
        camera: 'CAM',
        filter: 'FILTER'
    };
    
    const label = typeLabels[log.type] || 'LOG';
    
    return `
        <div class="log-entry ${log.type}">
            <span class="log-timestamp">${log.timestamp}</span>
            <span class="log-badge">${label}</span>
            <span class="log-message">${escapeHtml(log.message)}</span>
        </div>
    `;
}

function clearLogs() {
    state.logs = [];
    state.lastLogsLength = 0;
    renderLogs();
}

// ==================== Filter Management ====================
async function loadFilters() {
    try {
        const response = await fetch('/api/filters');
        const data = await response.json();
        
        if (data.success) {
            const newFiltersJSON = JSON.stringify(data.filters);
            if (newFiltersJSON !== state.lastFiltersJSON) {
                state.filters = data.filters;
                state.lastFiltersJSON = newFiltersJSON;
                renderFilters();
                updateFilterCount();
            }
        }
    } catch (error) {
        console.error('[TeleOps] Error loading filters:', error);
    }
}

function updateFilterCount() {
    const activeCount = state.filters.filter(f => f.is_active).length;
    const countEl = document.getElementById('filterCount');
    if (countEl) {
        countEl.textContent = `${activeCount} active`;
    }
}

function renderFilters() {
    const filtersList = document.getElementById('filtersList');
    
    if (state.filters.length === 0) {
        filtersList.innerHTML = `
            <div class="empty-state" style="text-align: center; padding: 2rem;">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="color: var(--text-muted); margin-bottom: 0.75rem;">
                    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
                </svg>
                <p style="color: var(--text-muted); font-size: 0.85rem;">
                    No filters yet.<br>Add one above to start analyzing!
                </p>
            </div>
        `;
        return;
    }
    
    filtersList.innerHTML = state.filters.map(filter => createFilterHTML(filter)).join('');
    attachFilterEventListeners();
}

function createFilterHTML(filter) {
    const activeClass = filter.is_active ? 'active' : '';
    
    let resultText = 'Waiting for analysis...';
    let resultClass = '';
    let resultIcon = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>`;
    
    if (filter.status === 'evaluating') {
        resultText = 'Analyzing...';
        resultClass = 'evaluating';
        resultIcon = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>`;
    } else if (filter.result !== null && filter.result !== undefined) {
        resultText = filter.result;
        const resultLower = String(filter.result).toLowerCase();
        
        if (resultLower === 'true' || resultLower.includes('yes')) {
            resultClass = 'success';
            resultIcon = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>`;
        } else if (resultLower === 'false' || resultLower.includes('no')) {
            resultClass = 'error';
            resultIcon = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>`;
        } else {
            resultClass = 'success';
            resultIcon = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>`;
        }
    }
    
    let timestampDisplay = '';
    if (filter.timestamp) {
        timestampDisplay = filter.timestamp;
    }
    
    return `
        <div class="filter-block" data-filter-id="${filter.id}">
            <div class="filter-header">
                <div class="filter-prompt">${escapeHtml(filter.prompt)}</div>
                <div class="filter-toggle ${activeClass}" 
                     data-action="toggle" 
                     data-filter-id="${filter.id}">
                </div>
            </div>
            
            <div class="result-box ${resultClass}">
                <div class="result-label">
                    ${resultIcon}
                    <span>Result</span>
                </div>
                <div class="result-text">${escapeHtml(resultText)}</div>
                ${timestampDisplay ? `<div class="result-timestamp">${escapeHtml(timestampDisplay)}</div>` : ''}
            </div>
            
            <div class="filter-controls">
                <button class="filter-btn" data-action="move-up" data-filter-id="${filter.id}" title="Move Up">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="18 15 12 9 6 15"></polyline>
                    </svg>
                </button>
                <button class="filter-btn" data-action="move-down" data-filter-id="${filter.id}" title="Move Down">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="6 9 12 15 18 9"></polyline>
                    </svg>
                </button>
                <button class="filter-btn remove" data-action="remove" data-filter-id="${filter.id}" title="Remove">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            </div>
        </div>
    `;
}

function attachFilterEventListeners() {
    document.querySelectorAll('[data-action="toggle"]').forEach(el => {
        el.addEventListener('click', async (e) => {
            const filterId = e.currentTarget.dataset.filterId;
            await toggleFilter(filterId);
        });
    });
    
    document.querySelectorAll('[data-action="move-up"]').forEach(el => {
        el.addEventListener('click', async (e) => {
            const filterId = e.currentTarget.dataset.filterId;
            await moveFilter(filterId, -1);
        });
    });
    
    document.querySelectorAll('[data-action="move-down"]').forEach(el => {
        el.addEventListener('click', async (e) => {
            const filterId = e.currentTarget.dataset.filterId;
            await moveFilter(filterId, 1);
        });
    });
    
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
        promptInput.focus();
        return;
    }
    
    try {
        const response = await fetch('/api/filters', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt })
        });
        
        const data = await response.json();
        
        if (data.success) {
            promptInput.value = '';
            state.lastFiltersJSON = null;
            await loadFilters();
        }
    } catch (error) {
        console.error('[TeleOps] Error adding filter:', error);
    }
}

async function removeFilter(filterId) {
    try {
        await fetch(`/api/filters/${filterId}`, { method: 'DELETE' });
        state.lastFiltersJSON = null;
        await loadFilters();
    } catch (error) {
        console.error('[TeleOps] Error removing filter:', error);
    }
}

async function moveFilter(filterId, direction) {
    try {
        await fetch(`/api/filters/${filterId}/move`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ direction })
        });
        state.lastFiltersJSON = null;
        await loadFilters();
    } catch (error) {
        console.error('[TeleOps] Error moving filter:', error);
    }
}

async function toggleFilter(filterId) {
    try {
        await fetch(`/api/filters/${filterId}/toggle`, { method: 'POST' });
        state.lastFiltersJSON = null;
        await loadFilters();
    } catch (error) {
        console.error('[TeleOps] Error toggling filter:', error);
    }
}

// ==================== Utility Functions ====================
function escapeHtml(text) {
    if (text === null || text === undefined) return '';
    const div = document.createElement('div');
    div.textContent = String(text);
    return div.innerHTML;
}

// ==================== Auto-Update Loop ====================
async function startAutoUpdate() {
    await loadConfig();
    
    console.log(`[TeleOps] Starting with ${state.captureInterval}ms interval`);
    
    // Initial loads
    updateAllCameras();
    loadFilters();
    loadLogs();
    
    // Start intervals
    state.frameUpdateInterval = setInterval(updateAllCameras, state.captureInterval);
    state.filterUpdateInterval = setInterval(loadFilters, state.captureInterval);
    state.logUpdateInterval = setInterval(loadLogs, 1000);
}

function stopAutoUpdate() {
    if (state.frameUpdateInterval) {
        clearInterval(state.frameUpdateInterval);
        state.frameUpdateInterval = null;
    }
    if (state.filterUpdateInterval) {
        clearInterval(state.filterUpdateInterval);
        state.filterUpdateInterval = null;
    }
    if (state.logUpdateInterval) {
        clearInterval(state.logUpdateInterval);
        state.logUpdateInterval = null;
    }
}

// ==================== Initialization ====================
document.addEventListener('DOMContentLoaded', () => {
    console.log('[TeleOps] Initializing...');
    
    initTheme();
    
    document.getElementById('addFilterBtn').addEventListener('click', addFilter);
    
    const clearLogBtn = document.getElementById('clearLogBtn');
    if (clearLogBtn) {
        clearLogBtn.addEventListener('click', clearLogs);
    }
    
    document.getElementById('newFilterPrompt').addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'Enter') addFilter();
    });
    
    startAutoUpdate();
    
    console.log('[TeleOps] Ready!');
});

document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        stopAutoUpdate();
    } else {
        startAutoUpdate();
    }
});
