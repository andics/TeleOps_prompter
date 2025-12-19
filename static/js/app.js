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
        A: { lastTimestamp: null, enabled: true },
        B: { lastTimestamp: null, enabled: true },
        C: { lastTimestamp: null, enabled: true }
    },
    cameraOrder: ['A', 'B', 'C'],
    vlmCamera: 'C',
    frameUpdateInterval: null,
    filterUpdateInterval: null,
    logUpdateInterval: null,
    captureInterval: 3000,
    filterInterval: 5000,
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
        
        if (data.success) {
            if (data.capture_interval) {
                state.captureInterval = data.capture_interval * 1000;
            }
            if (data.filter_interval) {
                state.filterInterval = data.filter_interval * 1000;
            }
            
            // Load camera enabled states
            if (data.cameras_enabled) {
                for (const [camId, enabled] of Object.entries(data.cameras_enabled)) {
                    if (state.cameras[camId]) {
                        state.cameras[camId].enabled = enabled;
                        updateCameraToggleUI(camId, enabled);
                    }
                }
            }
            
            // Load camera order
            if (data.cameras_order) {
                state.cameraOrder = data.cameras_order;
                reorderCamerasInDOM(data.cameras_order);
            }
            
            // Load VLM camera selection
            if (data.vlm_camera) {
                state.vlmCamera = data.vlm_camera;
                updateVlmCameraUI(data.vlm_camera);
            }
            
            const updateInfo = document.getElementById('updateInfo');
            if (updateInfo) {
                updateInfo.textContent = `Frame: ${data.capture_interval}s | Filter: ${data.filter_interval}s`;
            }
        }
    } catch (error) {
        console.error('[TeleOps] Error loading config:', error);
    }
    
    return state.captureInterval;
}

// ==================== Frame Updates ====================
async function updateCameraFrame(cameraId) {
    // Skip if camera is disabled
    if (!state.cameras[cameraId]?.enabled) {
        return;
    }
    
    try {
        const response = await fetch(`/api/latest-frame/${cameraId}`);
        const data = await response.json();
        
        if (data.success && data.image) {
            const frameImg = document.getElementById(`frame${cameraId}`);
            const placeholder = frameImg?.parentElement?.querySelector('.frame-placeholder-small');
            const overlay = frameImg?.parentElement?.querySelector('.camera-disabled-overlay');
            
            if (frameImg && data.timestamp !== state.cameras[cameraId].lastTimestamp) {
                frameImg.src = data.image;
                frameImg.classList.add('loaded');
                if (placeholder) placeholder.style.display = 'none';
                if (overlay) overlay.style.display = 'none';
                
                state.cameras[cameraId].lastTimestamp = data.timestamp;
            }
        } else if (data.disabled) {
            // Camera is disabled on server side
            state.cameras[cameraId].enabled = false;
            updateCameraToggleUI(cameraId, false);
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

// ==================== Camera Toggle ====================
function updateCameraToggleUI(cameraId, enabled) {
    const toggleBtn = document.querySelector(`.camera-toggle[data-camera="${cameraId}"]`);
    const cameraFeed = document.getElementById(`camera${cameraId}`);
    const overlay = cameraFeed?.querySelector('.camera-disabled-overlay');
    const frameImg = document.getElementById(`frame${cameraId}`);
    
    if (toggleBtn) {
        toggleBtn.classList.toggle('active', enabled);
    }
    
    if (cameraFeed) {
        cameraFeed.classList.toggle('disabled', !enabled);
    }
    
    if (overlay) {
        overlay.style.display = enabled ? 'none' : 'flex';
    }
    
    if (frameImg && !enabled) {
        frameImg.classList.remove('loaded');
    }
    
    state.cameras[cameraId].enabled = enabled;
}

async function toggleCamera(cameraId) {
    try {
        const response = await fetch(`/api/camera/${cameraId}/toggle`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            updateCameraToggleUI(cameraId, data.enabled);
        }
    } catch (error) {
        console.error(`[TeleOps] Error toggling Camera ${cameraId}:`, error);
    }
}

function initCameraToggles() {
    document.querySelectorAll('.camera-toggle').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const cameraId = btn.dataset.camera;
            toggleCamera(cameraId);
        });
    });
}

// ==================== Camera Reordering ====================
async function moveCamera(cameraId, direction) {
    try {
        const response = await fetch(`/api/camera/${cameraId}/move`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ direction })
        });
        const data = await response.json();
        
        if (data.success && data.order) {
            state.cameraOrder = data.order;
            reorderCamerasInDOM(data.order);
        }
    } catch (error) {
        console.error(`[TeleOps] Error moving Camera ${cameraId}:`, error);
    }
}

function reorderCamerasInDOM(order) {
    const container = document.getElementById('camerasContainer');
    if (!container) return;
    
    // Get all camera elements
    const cameras = {};
    order.forEach(camId => {
        const el = document.getElementById(`camera${camId}`);
        if (el) cameras[camId] = el;
    });
    
    // Reorder by appending in correct order
    order.forEach(camId => {
        if (cameras[camId]) {
            container.appendChild(cameras[camId]);
        }
    });
}

function initCameraMoveButtons() {
    document.querySelectorAll('.camera-move-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const cameraId = btn.dataset.camera;
            const direction = parseInt(btn.dataset.direction, 10);
            moveCamera(cameraId, direction);
        });
    });
}

// ==================== VLM Camera Selection ====================
function updateVlmCameraUI(selectedCamera) {
    // Update checkboxes
    document.querySelectorAll('.vlm-select').forEach(checkbox => {
        checkbox.checked = (checkbox.value === selectedCamera);
    });
    
    // Update camera feed styling
    document.querySelectorAll('.camera-feed').forEach(feed => {
        const camId = feed.dataset.cameraId;
        feed.classList.toggle('vlm-active', camId === selectedCamera);
        
        // Update or add/remove VLM badge
        const badge = feed.querySelector('.camera-badge');
        if (camId === selectedCamera) {
            if (!badge) {
                const label = feed.querySelector('.camera-label');
                if (label) {
                    const newBadge = document.createElement('span');
                    newBadge.className = 'camera-badge';
                    newBadge.textContent = 'VLM';
                    label.after(newBadge);
                }
            }
        } else {
            if (badge) {
                badge.remove();
            }
        }
    });
    
    state.vlmCamera = selectedCamera;
}

async function setVlmCamera(cameraId) {
    try {
        const response = await fetch('/api/vlm-camera', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ camera: cameraId })
        });
        const data = await response.json();
        
        if (data.success) {
            updateVlmCameraUI(data.vlm_camera);
        }
    } catch (error) {
        console.error(`[TeleOps] Error setting VLM camera:`, error);
    }
}

function initVlmCameraSelection() {
    document.querySelectorAll('.vlm-select').forEach(checkbox => {
        checkbox.addEventListener('change', (e) => {
            if (e.target.checked) {
                setVlmCamera(e.target.value);
            } else {
                // Prevent unchecking - at least one must be selected
                e.target.checked = true;
            }
        });
    });
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
    
    console.log(`[TeleOps] Starting with capture: ${state.captureInterval}ms, filter: ${state.filterInterval}ms`);
    
    // Initial loads
    updateAllCameras();
    loadFilters();
    loadLogs();
    
    // Start intervals - frame updates use CAPTURE_INTERVAL, filter updates use FILTER_INTERVAL
    state.frameUpdateInterval = setInterval(updateAllCameras, state.captureInterval);
    state.filterUpdateInterval = setInterval(loadFilters, state.filterInterval);
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
    initCameraToggles();
    initCameraMoveButtons();
    initVlmCameraSelection();
    
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
