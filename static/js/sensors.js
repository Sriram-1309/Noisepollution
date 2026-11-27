/* Sensor Management Page JavaScript */
let allSensorsData = [], deleteTargetId = null;

document.addEventListener('DOMContentLoaded', function() {
    loadSensors();
    loadZonesDropdown();

    document.getElementById('btnSaveSensor')?.addEventListener('click', saveSensor);
    document.getElementById('btnConfirmDelete')?.addEventListener('click', confirmDelete);
    document.getElementById('sensorSearch')?.addEventListener('input', filterSensors);
    document.getElementById('filterZone')?.addEventListener('change', filterSensors);
    document.getElementById('filterStatus')?.addEventListener('change', filterSensors);
});

function loadSensors() {
    fetch('/api/sensors')
        .then(r => r.json())
        .then(sensors => {
            allSensorsData = sensors;
            renderSensorsTable(sensors);
            updateStats(sensors);
        })
        .catch(e => { showToast('Error loading sensors', 'danger'); });
}

function renderSensorsTable(sensors) {
    const tbody = document.getElementById('sensorsTableBody');
    if (!sensors.length) {
        tbody.innerHTML = '<tr><td colspan="8" class="text-center text-muted p-4">No sensors found. Add one to get started.</td></tr>';
        return;
    }
    tbody.innerHTML = sensors.map(s => {
        const reading = s.latest_reading;
        const readingBadge = reading != null
            ? `<span class="badge" style="background:${getNoiseColor(reading)};color:#fff">${reading} dB</span>`
            : '<span class="text-muted">--</span>';
        const statusBadge = s.status === 'online'
            ? '<span class="badge bg-success">Online</span>'
            : '<span class="badge bg-danger">Offline</span>';
        return `<tr>
            <td>SEN-${String(s.id).padStart(3,'0')}</td>
            <td><strong>${s.name}</strong></td>
            <td><small>${s.latitude?.toFixed(4)}, ${s.longitude?.toFixed(4)}</small></td>
            <td><span class="badge bg-secondary">${s.zone_name || 'Unassigned'}</span></td>
            <td>${readingBadge}</td>
            <td>${statusBadge}</td>
            <td><small>${formatDateTime(s.last_updated)}</small></td>
            <td>
                <button class="btn btn-sm btn-outline-primary me-1" onclick="openEditSensorModal(${s.id})" title="Edit"><i class="fas fa-edit"></i></button>
                <button class="btn btn-sm btn-outline-info me-1" onclick="viewHistory(${s.id})" title="History"><i class="fas fa-chart-line"></i></button>
                <button class="btn btn-sm btn-outline-danger" onclick="deleteSensor(${s.id})" title="Delete"><i class="fas fa-trash"></i></button>
            </td></tr>`;
    }).join('');
}

function updateStats(sensors) {
    document.getElementById('statTotal').textContent = sensors.length;
    document.getElementById('statOnline').textContent = sensors.filter(s => s.status === 'online').length;
    document.getElementById('statOffline').textContent = sensors.filter(s => s.status !== 'online').length;
    const readings = sensors.filter(s => s.latest_reading != null).map(s => s.latest_reading);
    document.getElementById('statAvg').textContent = readings.length ? (readings.reduce((a,b)=>a+b,0)/readings.length).toFixed(1) + ' dB' : '--';
}

function loadZonesDropdown() {
    fetch('/api/zones').then(r => r.json()).then(zones => {
        const selects = [document.getElementById('sensorZone'), document.getElementById('filterZone')];
        selects.forEach(sel => {
            if (!sel) return;
            const current = sel.innerHTML;
            sel.innerHTML = '<option value="">None</option>' + zones.map(z => `<option value="${z.id}">${z.name} (${z.zone_type})</option>`).join('');
        });
    });
}

function filterSensors() {
    const search = (document.getElementById('sensorSearch')?.value || '').toLowerCase();
    const zone = document.getElementById('filterZone')?.value || '';
    const status = document.getElementById('filterStatus')?.value || '';
    let filtered = allSensorsData.filter(s => {
        if (search && !s.name.toLowerCase().includes(search)) return false;
        if (zone && s.zone_id != zone) return false;
        if (status && s.status !== status) return false;
        return true;
    });
    renderSensorsTable(filtered);
}

function openAddSensorModal() {
    document.getElementById('sensorModalTitle').textContent = 'Add New Sensor';
    document.getElementById('sensorId').value = '';
    document.getElementById('sensorName').value = '';
    document.getElementById('sensorLat').value = '';
    document.getElementById('sensorLng').value = '';
    document.getElementById('sensorZone').value = '';
    document.getElementById('sensorStatus').value = 'online';
}

function openEditSensorModal(id) {
    fetch(`/api/sensors/${id}`).then(r => r.json()).then(s => {
        document.getElementById('sensorModalTitle').textContent = 'Edit Sensor';
        document.getElementById('sensorId').value = s.id;
        document.getElementById('sensorName').value = s.name;
        document.getElementById('sensorLat').value = s.latitude;
        document.getElementById('sensorLng').value = s.longitude;
        document.getElementById('sensorZone').value = s.zone_id || '';
        document.getElementById('sensorStatus').value = s.status;
        new bootstrap.Modal(document.getElementById('sensorModal')).show();
    });
}

function saveSensor() {
    const id = document.getElementById('sensorId').value;
    const data = {
        name: document.getElementById('sensorName').value.trim(),
        latitude: parseFloat(document.getElementById('sensorLat').value),
        longitude: parseFloat(document.getElementById('sensorLng').value),
        zone_id: document.getElementById('sensorZone').value ? parseInt(document.getElementById('sensorZone').value) : null,
        status: document.getElementById('sensorStatus').value
    };

    if (!data.name) { showToast('Name is required', 'warning'); return; }
    if (isNaN(data.latitude) || isNaN(data.longitude)) { showToast('Valid coordinates required', 'warning'); return; }

    const url = id ? `/api/sensors/${id}` : '/api/sensors/';
    const method = id ? 'PUT' : 'POST';

    fetch(url, { method, headers: {'Content-Type':'application/json'}, body: JSON.stringify(data) })
        .then(r => r.json())
        .then(res => {
            if (res.error) { showToast(res.error, 'danger'); return; }
            showToast(res.message || 'Saved!', 'success');
            bootstrap.Modal.getInstance(document.getElementById('sensorModal'))?.hide();
            loadSensors();
        })
        .catch(e => showToast('Error: ' + e.message, 'danger'));
}

function deleteSensor(id) {
    deleteTargetId = id;
    new bootstrap.Modal(document.getElementById('deleteModal')).show();
}

function confirmDelete() {
    if (!deleteTargetId) return;
    fetch(`/api/sensors/${deleteTargetId}`, { method: 'DELETE' })
        .then(r => r.json())
        .then(res => {
            showToast(res.message || 'Deleted', 'success');
            bootstrap.Modal.getInstance(document.getElementById('deleteModal'))?.hide();
            loadSensors();
        })
        .catch(e => showToast('Error: ' + e.message, 'danger'));
}

let historyChart = null;
function viewHistory(id) {
    fetch(`/api/sensors/${id}/readings?limit=50`)
        .then(r => r.json())
        .then(readings => {
            new bootstrap.Modal(document.getElementById('historyModal')).show();
            setTimeout(() => {
                const ctx = document.getElementById('sensorHistoryChart');
                if (historyChart) historyChart.destroy();
                const sorted = readings.reverse();
                historyChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: sorted.map(r => formatDateTime(r.timestamp)),
                        datasets: [{
                            label: 'Noise Level (dB)',
                            data: sorted.map(r => r.noise_level_db),
                            borderColor: '#3498db', backgroundColor: 'rgba(52,152,219,0.1)',
                            fill: true, tension: 0.3, pointRadius: 2
                        }]
                    },
                    options: { responsive: true, plugins: { legend: { display: false } },
                        scales: { x: { display: false } } }
                });

                document.getElementById('historyReadings').innerHTML = `<table class="table table-sm"><thead><tr><th>Time</th><th>Level</th></tr></thead><tbody>${
                    sorted.slice(-20).reverse().map(r => `<tr><td>${formatDateTime(r.timestamp)}</td><td><span style="color:${getNoiseColor(r.noise_level_db)}">${r.noise_level_db} dB</span></td></tr>`).join('')
                }</tbody></table>`;
            }, 300);
        });
}

