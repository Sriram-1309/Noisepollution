/* Violation Monitoring Page JavaScript */
document.addEventListener('DOMContentLoaded', function() {
    loadViolations();
    document.getElementById('btnDetectViolations')?.addEventListener('click', detectViolations);
    document.getElementById('btnApplyVFilters')?.addEventListener('click', applyViolationFilters);
    document.getElementById('btnClearVFilters')?.addEventListener('click', clearViolationFilters);
});

function loadViolations(filters = {}) {
    let params = new URLSearchParams();
    Object.keys(filters).forEach(k => { if (filters[k]) params.append(k, filters[k]); });

    fetch('/api/violations?' + params.toString())
        .then(r => r.json())
        .then(violations => {
            renderViolationsTable(violations);
            updateViolationStats(violations);
        })
        .catch(e => showToast('Error loading violations', 'danger'));
}

function renderViolationsTable(violations) {
    const tbody = document.getElementById('violationsTableBody');
    if (!violations.length) {
        tbody.innerHTML = '<tr><td colspan="10" class="text-center text-muted p-4">No violations found. Run detection from Settings page.</td></tr>';
        return;
    }
    tbody.innerHTML = violations.map(v => {
        const sevColors = { low: 'success', medium: 'warning', high: 'orange', critical: 'danger' };
        const isSensitive = v.zone_type === 'school' || v.zone_type === 'hospital';
        return `<tr class="${isSensitive ? 'table-warning' : ''}">
            <td>${v.id}</td>
            <td>${v.sensor_name || 'N/A'} ${isSensitive ? '<i class="fas fa-exclamation-circle text-danger"></i>' : ''}</td>
            <td><small>${v.location_name || 'N/A'}</small></td>
            <td><span class="badge bg-secondary">${v.zone_type}</span></td>
            <td><strong style="color:${getNoiseColor(v.noise_level_db)}">${v.noise_level_db} dB</strong></td>
            <td>${v.applicable_limit_db} dB</td>
            <td><span class="text-danger">+${v.exceedance_db} dB</span></td>
            <td><span class="badge bg-${sevColors[v.severity] || 'secondary'}">${v.severity}</span></td>
            <td><small>${formatDateTime(v.timestamp)}</small></td>
            <td><button class="btn btn-sm btn-outline-info" onclick="viewViolationDetail(${v.id})"><i class="fas fa-eye"></i></button></td>
        </tr>`;
    }).join('');
}

function updateViolationStats(violations) {
    document.getElementById('totalViolations').textContent = violations.length;
    document.getElementById('criticalCount').textContent = violations.filter(v => v.severity === 'critical').length;
    document.getElementById('highCount').textContent = violations.filter(v => v.severity === 'high').length;
    document.getElementById('mediumCount').textContent = violations.filter(v => v.severity === 'medium').length;
    document.getElementById('lowCount').textContent = violations.filter(v => v.severity === 'low').length;
}

function applyViolationFilters() {
    loadViolations({
        start_date: document.getElementById('vStartDate')?.value || '',
        end_date: document.getElementById('vEndDate')?.value ? document.getElementById('vEndDate').value + 'T23:59:59' : '',
        zone_type: document.getElementById('vZoneType')?.value || '',
        severity: document.getElementById('vSeverity')?.value || ''
    });
}

function clearViolationFilters() {
    document.getElementById('vStartDate').value = '';
    document.getElementById('vEndDate').value = '';
    document.getElementById('vZoneType').value = '';
    document.getElementById('vSeverity').value = '';
    loadViolations();
}

function detectViolations() {
    showToast('Detecting violations...', 'info');
    fetch('/api/violations/detect', { method: 'POST' })
        .then(r => r.json())
        .then(data => { showToast(data.message, 'success'); loadViolations(); })
        .catch(e => showToast('Error: ' + e.message, 'danger'));
}

function viewViolationDetail(id) {
    fetch(`/api/violations/${id}`).then(r => r.json()).then(v => {
        const body = document.getElementById('violationDetailBody');
        body.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <table class="table table-sm">
                        <tr><td><strong>Violation ID</strong></td><td>#${v.id}</td></tr>
                        <tr><td><strong>Sensor</strong></td><td>${v.sensor_name || 'N/A'}</td></tr>
                        <tr><td><strong>Location</strong></td><td>${v.location_name || v.zone_name || 'N/A'}</td></tr>
                        <tr><td><strong>Zone Type</strong></td><td><span class="badge bg-secondary">${v.zone_type}</span></td></tr>
                        <tr><td><strong>Timestamp</strong></td><td>${formatDateTime(v.timestamp)}</td></tr>
                    </table>
                </div>
                <div class="col-md-6">
                    <table class="table table-sm">
                        <tr><td><strong>Noise Level</strong></td><td><span style="color:${getNoiseColor(v.noise_level_db)};font-size:1.2rem;font-weight:700">${v.noise_level_db} dB</span></td></tr>
                        <tr><td><strong>Applicable Limit</strong></td><td>${v.applicable_limit_db} dB</td></tr>
                        <tr><td><strong>Exceedance</strong></td><td class="text-danger">+${v.exceedance_db} dB</td></tr>
                        <tr><td><strong>Severity</strong></td><td>${getSeverityBadge(v.severity)}</td></tr>
                        <tr><td><strong>Coordinates</strong></td><td>${v.latitude?.toFixed(4)}, ${v.longitude?.toFixed(4)}</td></tr>
                    </table>
                </div>
            </div>`;
        new bootstrap.Modal(document.getElementById('violationDetailModal')).show();
    });
}

