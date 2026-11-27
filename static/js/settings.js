/* Settings Page JavaScript */
let editRuleId = null;

document.addEventListener('DOMContentLoaded', function() {
    loadNoiseLimits();
    document.getElementById('btnSaveRule')?.addEventListener('click', saveRule);
    document.getElementById('btnGenerate')?.addEventListener('click', generateReadings);
    document.getElementById('btnDetectViolations')?.addEventListener('click', detectViolations);
    document.getElementById('btnResetData')?.addEventListener('click', resetData);
    document.getElementById('btnReseed')?.addEventListener('click', reseedData);
});

function loadNoiseLimits() {
    fetch('/api/settings/limits').then(r => r.json()).then(limits => {
        const tbody = document.getElementById('limitsTableBody');
        if (!limits.length) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">No rules configured</td></tr>';
            return;
        }
        tbody.innerHTML = limits.map(l => `<tr>
            <td><span class="badge bg-secondary text-capitalize">${l.zone_type}</span></td>
            <td>${l.day_limit_db} dB</td>
            <td>${l.night_limit_db} dB</td>
            <td>${l.day_start_hour}:00</td>
            <td>${l.night_start_hour}:00</td>
            <td><small>${l.description || '--'}</small></td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="openEditRuleModal(${l.id})"><i class="fas fa-edit"></i></button>
                <button class="btn btn-sm btn-outline-danger" onclick="deleteRule(${l.id})"><i class="fas fa-trash"></i></button>
            </td></tr>`).join('');
    });
}

function openAddRuleModal() {
    document.getElementById('ruleModalTitle').textContent = 'Add Noise Limit Rule';
    document.getElementById('ruleId').value = '';
    document.getElementById('ruleZoneType').value = '';
    document.getElementById('ruleDayLimit').value = '';
    document.getElementById('ruleNightLimit').value = '';
    document.getElementById('ruleDayStart').value = '6';
    document.getElementById('ruleNightStart').value = '22';
    document.getElementById('ruleDescription').value = '';
}

function openEditRuleModal(id) {
    fetch('/api/settings/limits').then(r => r.json()).then(limits => {
        const rule = limits.find(l => l.id === id);
        if (!rule) return;
        document.getElementById('ruleModalTitle').textContent = 'Edit Noise Limit Rule';
        document.getElementById('ruleId').value = rule.id;
        document.getElementById('ruleZoneType').value = rule.zone_type;
        document.getElementById('ruleDayLimit').value = rule.day_limit_db;
        document.getElementById('ruleNightLimit').value = rule.night_limit_db;
        document.getElementById('ruleDayStart').value = rule.day_start_hour;
        document.getElementById('ruleNightStart').value = rule.night_start_hour;
        document.getElementById('ruleDescription').value = rule.description || '';
        new bootstrap.Modal(document.getElementById('ruleModal')).show();
    });
}

function saveRule() {
    const id = document.getElementById('ruleId').value;
    const data = {
        zone_type: document.getElementById('ruleZoneType').value.trim().toLowerCase(),
        day_limit_db: parseFloat(document.getElementById('ruleDayLimit').value),
        night_limit_db: parseFloat(document.getElementById('ruleNightLimit').value),
        day_start_hour: parseInt(document.getElementById('ruleDayStart').value) || 6,
        night_start_hour: parseInt(document.getElementById('ruleNightStart').value) || 22,
        description: document.getElementById('ruleDescription').value.trim()
    };

    if (!data.zone_type) { showToast('Zone type is required', 'warning'); return; }
    if (isNaN(data.day_limit_db) || isNaN(data.night_limit_db)) { showToast('Valid limits are required', 'warning'); return; }

    const url = id ? `/api/settings/limits/${id}` : '/api/settings/limits';
    const method = id ? 'PUT' : 'POST';

    fetch(url, { method, headers: {'Content-Type':'application/json'}, body: JSON.stringify(data) })
        .then(r => r.json()).then(res => {
            if (res.error) { showToast(res.error, 'danger'); return; }
            showToast(res.message || 'Saved!', 'success');
            bootstrap.Modal.getInstance(document.getElementById('ruleModal'))?.hide();
            loadNoiseLimits();
        }).catch(e => showToast('Error: ' + e.message, 'danger'));
}

function deleteRule(id) {
    if (!confirm('Delete this noise limit rule?')) return;
    fetch(`/api/settings/limits/${id}`, { method: 'DELETE' })
        .then(r => r.json()).then(res => {
            showToast(res.message || 'Deleted', 'success');
            loadNoiseLimits();
        }).catch(e => showToast('Error: ' + e.message, 'danger'));
}

function generateReadings() {
    const count = parseInt(document.getElementById('readingCount')?.value) || 500;
    const hours = parseInt(document.getElementById('hoursBack')?.value) || 48;
    showToast('Generating readings...', 'info');
    fetch('/api/simulate/generate', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ num_readings: count, hours_back: hours })
    }).then(r => r.json()).then(data => {
        showToast(data.message, 'success');
    }).catch(e => showToast('Error: ' + e.message, 'danger'));
}

function detectViolations() {
    showToast('Detecting violations...', 'info');
    fetch('/api/violations/detect', { method: 'POST' })
        .then(r => r.json()).then(data => showToast(data.message, 'success'))
        .catch(e => showToast('Error: ' + e.message, 'danger'));
}

function resetData() {
    if (!confirm('This will delete ALL readings and violations. Are you sure?')) return;
    fetch('/api/simulate/reset', { method: 'POST' })
        .then(r => r.json()).then(data => showToast(data.message, 'success'))
        .catch(e => showToast('Error: ' + e.message, 'danger'));
}

function reseedData() {
    if (!confirm('This will DELETE ALL DATA and re-create demo data from scratch. Continue?')) return;
    showToast('Re-seeding demo data...', 'info');
    fetch('/api/simulate/seed', { method: 'POST' })
        .then(r => r.json()).then(data => {
            showToast(data.message, 'success');
            setTimeout(() => location.reload(), 1500);
        }).catch(e => showToast('Error: ' + e.message, 'danger'));
}

