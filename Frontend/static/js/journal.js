requireAuth();

let selectedMood = 'okay';
let editingEntryId = null;

// Check if we're editing an existing entry
const urlParams = new URLSearchParams(window.location.search);
const editId = urlParams.get('edit_id');

// Set today's date
const dateEl = document.getElementById('today-date');
if (dateEl) {
    dateEl.textContent = new Date().toLocaleDateString('en-IN', {
        weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
    });
}

// Show username in sidebar
const userInfoEl = document.getElementById('user-info');
if (userInfoEl) {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    userInfoEl.textContent = `👤 ${user.username || 'User'}`;
}

// If editing — load existing entry data
async function loadEntryForEdit(id) {
    const res = await api.get(`/journal/entries/${id}/`);
    if (!res || res.status !== 200) return;

    const entry = res.data;
    editingEntryId = id;

    // Fill form with existing data
    const titleEl = document.getElementById('entry-title');
    const contentEl = document.getElementById('entry-content');

    if (titleEl) titleEl.value = entry.title;
    if (contentEl) {
        contentEl.value = entry.content;
        updateCharCount();
    }

    // Set mood
    if (entry.mood) {
        selectedMood = entry.mood;
        document.querySelectorAll('.mood-btn').forEach(btn => {
            if (btn.getAttribute('onclick').includes(entry.mood)) {
                btn.classList.add('selected');
            }
        });
    }

    // Update page title
    const pageTitle = document.querySelector('h2');
    if (pageTitle) pageTitle.textContent = 'Edit Your Entry ✏️';

    // Update save button
    const saveBtn = document.getElementById('save-btn');
    if (saveBtn) saveBtn.textContent = '💾 Update Entry';
}

// Load entries on dashboard
async function loadEntries() {
    const res = await api.get('/journal/entries/');
    if (!res) return;

    const container = document.getElementById('entries-container');
    const totalEl = document.getElementById('total-entries');
    const analyzedEl = document.getElementById('analyzed-entries');
    const latestEl = document.getElementById('latest-emotion');

    const entries = res.data.entries || [];
    if (totalEl) totalEl.textContent = entries.length;

    const analyzed = entries.filter(e => e.is_analyzed).length;
    if (analyzedEl) analyzedEl.textContent = analyzed;

    if (!container) return;

    if (entries.length === 0) {
        container.innerHTML = `
            <div class="text-center py-12 text-gray-400">
                <p class="text-5xl mb-4">📔</p>
                <p class="text-lg">No entries yet</p>
                <a href="journal_editor.html">
                    <button class="btn-primary mt-4">Write First Entry</button>
                </a>
            </div>`;
        return;
    }

    // Get latest emotion
    const analyzedEntries = entries.filter(e => e.is_analyzed);
    if (analyzedEntries.length > 0 && latestEl) {
        const latestId = analyzedEntries[0].id;
        const emotionRes = await api.get(`/nlp/analysis/${latestId}/`);
        if (emotionRes && emotionRes.data.dominant_emotion) {
            latestEl.textContent = emotionRes.data.dominant_emotion;
        }
    }

    container.innerHTML = entries.map(entry => `
        <div class="entry-card mb-4">
            <div class="flex justify-between items-start">
                <div class="flex-1 cursor-pointer" onclick="openEntry(${entry.id})">
                    <h4 class="font-semibold text-gray-800">${entry.title}</h4>
                    <p class="text-gray-500 text-sm mt-1">${entry.content.substring(0, 120)}...</p>
                    <div class="flex items-center gap-3 mt-3">
                        <span class="text-xs text-gray-400">
                            ${new Date(entry.created_at).toLocaleDateString('en-IN')}
                        </span>
                        ${entry.mood ? `<span class="emotion-badge neutral">${entry.mood}</span>` : ''}
                        ${entry.is_analyzed
                            ? '<span class="emotion-badge" style="background:#d1fae5;color:#065f46">✅ Analyzed</span>'
                            : '<span class="emotion-badge neutral">⏳ Not analyzed</span>'
                        }
                    </div>
                </div>
                <div class="flex gap-2 ml-4">
                    <button onclick="editEntry(${entry.id})"
                        class="px-3 py-1 bg-blue-50 text-blue-600 border border-blue-200 rounded-lg text-xs font-semibold hover:bg-blue-100 transition-all">
                        ✏️ Edit
                    </button>
                    <button onclick="deleteEntry(${entry.id})"
                        class="btn-danger">
                        🗑️ Delete
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

function openEntry(id) {
    window.location.href = `emotion_result.html?entry_id=${id}`;
}

function editEntry(id) {
    window.location.href = `journal_editor.html?edit_id=${id}`;
}

async function deleteEntry(id) {
    if (!confirm('Delete this entry? This cannot be undone.')) return;
    const res = await api.delete(`/journal/entries/${id}/`);
    if (res) loadEntries();
}

// Mood selection
function selectMood(mood, btn) {
    selectedMood = mood;
    document.querySelectorAll('.mood-btn').forEach(b => b.classList.remove('selected'));
    btn.classList.add('selected');
}

// Character count
function updateCharCount() {
    const content = document.getElementById('entry-content');
    const counter = document.getElementById('char-count');
    if (content && counter) {
        counter.textContent = `${content.value.length} characters`;
    }
}

// Save entry (create or update)
async function saveEntry() {
    const title = document.getElementById('entry-title')?.value;
    const content = document.getElementById('entry-content')?.value;

    if (!title || !content) {
        showAlert('Please fill in both title and content.', 'error');
        return;
    }

    const btn = document.getElementById('save-btn');
    btn.textContent = 'Saving...';
    btn.disabled = true;

    let res;

    if (editingEntryId) {
        // UPDATE existing entry
        res = await api.put(`/journal/entries/${editingEntryId}/`, {
            title, content, mood: selectedMood
        });
        if (res && res.status === 200) {
            showAlert('Entry updated successfully! ✅', 'success');
            setTimeout(() => window.location.href = 'dashboard.html', 1500);
        } else {
            showAlert('Failed to update entry.', 'error');
        }
    } else {
        // CREATE new entry
        res = await api.post('/journal/entries/', {
            title, content, mood: selectedMood
        });
        if (res && res.status === 201) {
            showAlert('Entry saved successfully! 🎉', 'success');
        } else {
            showAlert('Failed to save entry.', 'error');
        }
    }

    btn.textContent = editingEntryId ? '💾 Update Entry' : '💾 Save Entry';
    btn.disabled = false;
}

// Save and analyze
async function saveAndAnalyze() {
    const title = document.getElementById('entry-title')?.value;
    const content = document.getElementById('entry-content')?.value;

    if (!title || !content) {
        showAlert('Please fill in both title and content.', 'error');
        return;
    }

    const btn = document.getElementById('analyze-btn');
    btn.textContent = '🧠 Analyzing...';
    btn.disabled = true;

    let entryId = editingEntryId;

    if (editingEntryId) {
        // Update first then analyze
        const updateRes = await api.put(`/journal/entries/${editingEntryId}/`, {
            title, content, mood: selectedMood
        });
        if (!updateRes || updateRes.status !== 200) {
            showAlert('Failed to update entry.', 'error');
            btn.textContent = '🧠 Save & Analyze Emotions';
            btn.disabled = false;
            return;
        }
    } else {
        // Create new entry
        const saveRes = await api.post('/journal/entries/', {
            title, content, mood: selectedMood
        });
        if (!saveRes || saveRes.status !== 201) {
            showAlert('Failed to save entry.', 'error');
            btn.textContent = '🧠 Save & Analyze Emotions';
            btn.disabled = false;
            return;
        }
        entryId = saveRes.data.entry.id;
    }

    // Analyze emotions
    const analyzeRes = await api.post(`/nlp/analyze/${entryId}/`, {});
    if (analyzeRes && analyzeRes.status === 200) {
        showAlert('Analysis complete! Redirecting... 🧠', 'success');
        setTimeout(() => {
            window.location.href = `emotion_result.html?entry_id=${entryId}`;
        }, 1500);
    } else {
        showAlert('Saved but analysis failed. Try again.', 'error');
    }

    btn.textContent = '🧠 Save & Analyze Emotions';
    btn.disabled = false;
}

function clearForm() {
    const title = document.getElementById('entry-title');
    const content = document.getElementById('entry-content');
    if (title) title.value = '';
    if (content) content.value = '';
    updateCharCount();
    document.querySelectorAll('.mood-btn').forEach(b => b.classList.remove('selected'));
    editingEntryId = null;
}

function showAlert(msg, type) {
    const div = document.getElementById('alert-msg');
    if (!div) return;
    div.className = type === 'success'
        ? 'mb-4 p-3 bg-green-50 border border-green-200 text-green-700 rounded-lg'
        : 'mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg';
    div.textContent = msg;
    div.classList.remove('hidden');
    setTimeout(() => div.classList.add('hidden'), 4000);
}

// Initialize page
if (document.getElementById('entries-container')) {
    loadEntries();
}

// Load entry for editing if edit_id in URL
if (editId) {
    loadEntryForEdit(editId);
}