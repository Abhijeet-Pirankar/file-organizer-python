const CATEGORY_COLORS = {
    "Images":   "#2979ff",
    "PDFs":     "#ff1744",
    "Videos":   "#d500f9",
    "Docs":     "#00e676",
    "Music":    "#ff9100",
    "Archives": "#ffea00",
    "Programs": "#f50057",
    "Code":     "#00e1ff",
    "Others":   "#9e9e9e",
};

const CATEGORY_ICONS = {
    "Images":   "🖼",
    "PDFs":     "📄",
    "Videos":   "🎬",
    "Docs":     "📝",
    "Music":    "🎵",
    "Archives": "🗜",
    "Programs": "⚙",
    "Code":     "💻",
    "Others":   "📦",
};

let currentFolder = null;

// Format bytes
function formatSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

// Update status indicator
function setStatus(text, type="ready") {
    const el = document.getElementById('status-indicator');
    el.textContent = text;
    el.className = `status-${type}`;
}

// Update progress bar
function setProgress(percent, text) {
    const fill = document.getElementById('progress-fill');
    const pText = document.getElementById('progress-text');
    const pPct = document.getElementById('progress-percent');
    
    fill.style.width = `${percent * 100}%`;
    pPct.textContent = `${Math.floor(percent * 100)}%`;
    if (text) pText.textContent = text;
    
    // Color transitions based on progress
    if (percent < 0.4) {
        fill.style.backgroundColor = 'var(--accent)';
        fill.style.boxShadow = '0 0 10px var(--accent)';
    } else if (percent < 0.85) {
        fill.style.backgroundColor = 'var(--warning)';
        fill.style.boxShadow = '0 0 10px var(--warning)';
    } else {
        fill.style.backgroundColor = 'var(--success)';
        fill.style.boxShadow = '0 0 10px var(--success)';
    }
}

// Update Stat Cards
function updateStats(total, moved, dups, errors, size) {
    const flash = (elId, color) => {
        const el = document.getElementById(elId);
        el.textContent = elId === 'stat-size' ? formatSize(size) : arguments[Array.from(arguments).findIndex(x => x === arguments[1])]; // hacky way to find arg
        // Just flash the text color
        const oldColor = el.style.color;
        el.style.color = color;
        setTimeout(() => el.style.color = oldColor, 300);
    };
    
    document.getElementById('stat-total').textContent = total;
    document.getElementById('stat-moved').textContent = moved;
    document.getElementById('stat-dups').textContent = dups;
    document.getElementById('stat-errors').textContent = errors;
}

// Draw Category Bars
function updateCategoryBars(counts, maxVal) {
    const container = document.getElementById('category-bars');
    container.innerHTML = '';
    
    if (Object.keys(counts).length === 0) {
        container.innerHTML = '<p class="empty-state">No data available.</p>';
        return;
    }
    
    for (const [cat, count] of Object.entries(counts)) {
        if (count === 0) continue;
        const color = CATEGORY_COLORS[cat] || CATEGORY_COLORS['Others'];
        const icon = CATEGORY_ICONS[cat] || '📦';
        const pct = maxVal > 0 ? (count / maxVal) * 100 : 0;
        
        const row = document.createElement('div');
        row.className = 'cat-bar-row';
        row.innerHTML = `
            <div class="cat-name">${icon} ${cat}</div>
            <div class="cat-bar-bg">
                <div class="cat-bar-fill" style="width: ${pct}%; background-color: ${color};"></div>
            </div>
            <div class="cat-val" style="color: ${color}">${count}</div>
        `;
        container.appendChild(row);
    }
}

// Render Preview Table
function renderPreview(files) {
    const tbody = document.getElementById('preview-body');
    const countBadge = document.getElementById('preview-count');
    tbody.innerHTML = '';
    
    if (!files || files.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="empty-state">No files to display.</td></tr>';
        countBadge.textContent = '0 files';
        return;
    }
    
    countBadge.textContent = `${files.length} files`;
    
    files.forEach(f => {
        const tr = document.createElement('tr');
        
        // Status Chip
        let statusHtml = '<span class="success-text">✔ Ready</span>';
        if (f.is_content_duplicate) {
            statusHtml = '<span class="warning-text">⊟ Content Dup</span>';
        } else if (f.is_name_conflict) {
            statusHtml = '<span class="warning-text">⚠ Name Conflict</span>';
        }
        
        const catColor = CATEGORY_COLORS[f.destination_category] || CATEGORY_COLORS['Others'];
        const catIcon = CATEGORY_ICONS[f.destination_category] || '📦';
        
        tr.innerHTML = `
            <td>${f.filename}</td>
            <td style="color: var(--text-dim)">${formatSize(f.file_size)}</td>
            <td style="color: ${catColor}">${catIcon} ${f.destination_category}</td>
            <td>${statusHtml}</td>
        `;
        tbody.appendChild(tr);
    });
}

// Event Listeners (Setup when Pywebview is ready)
window.addEventListener('pywebviewready', function() {
    
    document.getElementById('browse-btn').addEventListener('click', async () => {
        const result = await window.pywebview.api.browse_folder();
        if (result) {
            currentFolder = result;
            document.getElementById('folder-input').value = result;
            setStatus('📁 Selected: ' + result, 'ready');
        }
    });

    document.getElementById('analyze-btn').addEventListener('click', async () => {
        if (!currentFolder) return setStatus('⚠ Please select a folder first.', 'error');
        const recursive = document.getElementById('recursive-checkbox').checked;
        
        setStatus('🔍 Analyzing folder...', 'working');
        setProgress(0.3, 'Scanning...');
        
        const result = await window.pywebview.api.analyze(currentFolder, recursive);
        
        setProgress(1.0, 'Analysis complete');
        setStatus('✔ Analysis done — ' + result.total_files + ' files.', 'ready');
        
        updateStats(result.total_files, result.organizable, result.name_conflicts + result.content_duplicates, 0, result.total_size);
        updateCategoryBars(result.category_counts, result.total_files);
    });

    document.getElementById('preview-btn').addEventListener('click', async () => {
        if (!currentFolder) return setStatus('⚠ Please select a folder first.', 'error');
        const recursive = document.getElementById('recursive-checkbox').checked;
        
        setStatus('👁 Building preview...', 'working');
        setProgress(0.1, 'Building...');
        
        const result = await window.pywebview.api.preview(currentFolder, recursive);
        
        setProgress(1.0, 'Preview ready');
        setStatus('👁 Preview ready — ' + result.total_files + ' files.', 'ready');
        
        updateStats(result.total_files, result.organizable, result.name_conflicts + result.content_duplicates, 0, result.total_size);
        updateCategoryBars(result.category_counts, result.total_files);
        renderPreview(result.file_previews);
    });

    document.getElementById('organize-btn').addEventListener('click', async () => {
        if (!currentFolder) return setStatus('⚠ Please select a folder first.', 'error');
        if (!confirm('Ready to organize files in ' + currentFolder + '?')) return;
        
        const recursive = document.getElementById('recursive-checkbox').checked;
        
        setStatus('⚡ Organizing...', 'working');
        setProgress(0.0, 'Starting...');
        renderPreview([]); // Clear preview
        
        const result = await window.pywebview.api.organize(currentFolder, recursive);
        
        setProgress(1.0, 'Done');
        if (result.errors > 0) {
            setStatus(`⚠ Done: ${result.moved} moved, ${result.errors} error(s).`, 'error');
        } else {
            setStatus(`✔ Done! ${result.moved} file(s) organized.`, 'ready');
        }
        
        updateStats(result.total_files, result.moved, 0, result.errors, result.total_size);
        updateCategoryBars(result.category_stats, result.total_files);
    });

    document.getElementById('undo-btn').addEventListener('click', async () => {
        if (!confirm('Restore files from the last session?')) return;
        
        setStatus('↩ Undoing...', 'working');
        setProgress(0.3, 'Restoring...');
        
        const result = await window.pywebview.api.undo();
        
        setProgress(1.0, 'Restored');
        if (result.error) {
            setStatus('↩ ' + result.error, 'error');
        } else if (result.errors.length > 0) {
            setStatus(`↩ Restored ${result.restored}, ${result.errors.length} error(s).`, 'error');
        } else {
            setStatus(`↩ Restored ${result.restored} file(s).`, 'ready');
        }
    });

    document.getElementById('watch-btn').addEventListener('click', async () => {
        if (!currentFolder) return setStatus('⚠ Please select a folder first.', 'error');
        const btn = document.getElementById('watch-btn');
        
        const result = await window.pywebview.api.toggle_watch(currentFolder);
        if (result.status === "started") {
            btn.textContent = "● Watching";
            btn.style.color = "var(--success)";
            btn.style.borderColor = "var(--success)";
            setStatus('👁 Monitoring: ' + currentFolder, 'ready');
        } else if (result.status === "stopped") {
            btn.textContent = "◉ Watch";
            btn.style.color = "";
            btn.style.borderColor = "";
            setStatus('⏹ Monitoring stopped.', 'ready');
        } else {
            setStatus('⚠ ' + result.error, 'error');
        }
    });

    document.getElementById('activity-btn').addEventListener('click', async () => {
        const modal = document.getElementById('activity-modal');
        const list = document.getElementById('activity-list');
        list.innerHTML = 'Loading...';
        modal.classList.remove('hidden');
        
        const sessions = await window.pywebview.api.get_activity();
        list.innerHTML = '';
        
        if (sessions.length === 0) {
            list.innerHTML = '<p style="color: var(--text-dim)">No activity recorded.</p>';
            return;
        }
        
        sessions.reverse().forEach(s => {
            const div = document.createElement('div');
            div.className = 'activity-item';
            div.innerHTML = `
                <div class="activity-item-top">
                    <strong>${s.timestamp}</strong>
                    <span>ID: ${s.session_id.substring(0,8)}</span>
                </div>
                <div style="margin-bottom: 5px">${s.folder}</div>
                <div class="activity-item-bottom">
                    <span class="success-text">Moved: ${s.file_count}</span>
                    ${s.errors > 0 ? `<span class="danger-text">Errors: ${s.errors}</span>` : ''}
                </div>
            `;
            list.appendChild(div);
        });
    });

    document.getElementById('close-activity-btn').addEventListener('click', () => {
        document.getElementById('activity-modal').classList.add('hidden');
    });
});

// Global functions exposed to Python for real-time updates
window.pyUpdateProgress = function(filename, category, idx, total) {
    const pct = idx / Math.max(total, 1);
    setProgress(pct, `⚡ ${idx}/${total} ${filename} → ${category}`);
};

window.pyWatchEvent = function(filename, status) {
    setStatus(`👁 ${filename} ${status}`, 'ready');
};
