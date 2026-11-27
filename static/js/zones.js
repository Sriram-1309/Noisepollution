/* Zone Management Page JavaScript */
let allZonesData = [], noiseLimits = {}, deleteZoneId = null;

document.addEventListener('DOMContentLoaded', function() {
    loadZones();
    loadNoiseLimits();
    document.getElementById('btnSaveZone')?.addEventListener('click', saveZone);
    document.getElementById('btnConfirmDeleteZone')?.addEventListener('click', confirmDeleteZone);
});

function loadNoiseLimits() {
    fetch('/api/settings/limits').then(r => r.json()).then(limits => {
        limits.forEach(l => { noiseLimits[l.zone_type] = l; });
    });
}

function loadZones() {
    fetch('/api/zones').then(r => r.json()).then(zones => {
        allZonesData = zones;
        const container = document.getElementById('zonesContainer');
        if (!zones.length) {
            container.innerHTML = '<div class="col-12 text-center text-muted p-4">No zones found.</div>';
            return;
        }
        container.innerHTML = zones.map(z => {
            const typeColors = { residential:'primary', commercial:'warning', industrial:'secondary',
                silence:'info', school:'success', hospital:'danger', traffic:'dark' };
            const limit = noiseLimits[z.zone_type];
            return `<div class="col-lg-4 col-md-6">
                <div class="card h-100">
                    <div class="card-body">
                        <div class="d-flex justify-content-between mb-2">
                            <h6 class="mb-0">${z.name}</h6>
                            <span class="badge bg-${typeColors[z.zone_type]||'secondary'}">${z.zone_type}</span>
                        </div>
                        <div class="small text-muted mb-2">
                            <i class="fas fa-map-pin me-1"></i>${z.latitude?.toFixed(4)}, ${z.longitude?.toFixed(4)}<br>
                            <i class="fas fa-circle me-1"></i>Radius: ${z.radius}m &bull; <i class="fas fa-satellite-dish me-1"></i>${z.sensor_count || 0} sensors
                        </div>
                        ${limit ? `<div class="small"><i class="fas fa-volume-down me-1"></i>Day: ${limit.day_limit_db} dB | Night: ${limit.night_limit_db} dB</div>` : ''}
                        ${z.description ? `<p class="small text-muted mt-1 mb-0">${z.description}</p>` : ''}
                    </div>
                    <div class="card-footer bg-white border-0">
                        <button class="btn btn-sm btn-outline-primary" onclick="openEditZoneModal(${z.id})"><i class="fas fa-edit"></i> Edit</button>
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteZone(${z.id})"><i class="fas fa-trash"></i> Delete</button>
                    </div>
                </div>
            </div>`;
        }).join('');
    }).catch(e => showToast('Error loading zones', 'danger'));
}

function openAddZoneModal() {
    document.getElementById('zoneModalTitle').textContent = 'Add New Zone';
    document.getElementById('zoneId').value = '';
    document.getElementById('zoneName').value = '';
    document.getElementById('zoneType').value = 'residential';
    document.getElementById('zoneLat').value = '';
    document.getElementById('zoneLng').value = '';
    document.getElementById('zoneRadius').value = '500';
    document.getElementById('zoneDesc').value = '';
}

function openEditZoneModal(id) {
    fetch(`/api/zones/${id}`).then(r => r.json()).then(z => {
        document.getElementById('zoneModalTitle').textContent = 'Edit Zone';
        document.getElementById('zoneId').value = z.id;
        document.getElementById('zoneName').value = z.name;
        document.getElementById('zoneType').value = z.zone_type;
        document.getElementById('zoneLat').value = z.latitude;
        document.getElementById('zoneLng').value = z.longitude;
        document.getElementById('zoneRadius').value = z.radius;
        document.getElementById('zoneDesc').value = z.description || '';
        new bootstrap.Modal(document.getElementById('zoneModal')).show();
    });
}

function saveZone() {
    const id = document.getElementById('zoneId').value;
    const data = {
        name: document.getElementById('zoneName').value.trim(),
        zone_type: document.getElementById('zoneType').value,
        latitude: parseFloat(document.getElementById('zoneLat').value),
        longitude: parseFloat(document.getElementById('zoneLng').value),
        radius: parseFloat(document.getElementById('zoneRadius').value) || 500,
        description: document.getElementById('zoneDesc').value.trim()
    };
    if (!data.name) { showToast('Name is required', 'warning'); return; }

    const url = id ? `/api/zones/${id}` : '/api/zones/';
    const method = id ? 'PUT' : 'POST';
    fetch(url, { method, headers: {'Content-Type':'application/json'}, body: JSON.stringify(data) })
        .then(r => r.json()).then(res => {
            if (res.error) { showToast(res.error, 'danger'); return; }
            showToast(res.message || 'Saved!', 'success');
            bootstrap.Modal.getInstance(document.getElementById('zoneModal'))?.hide();
            loadZones();
        }).catch(e => showToast('Error: ' + e.message, 'danger'));
}

function deleteZone(id) {
    deleteZoneId = id;
    new bootstrap.Modal(document.getElementById('deleteZoneModal')).show();
}

function confirmDeleteZone() {
    if (!deleteZoneId) return;
    fetch(`/api/zones/${deleteZoneId}`, { method: 'DELETE' })
        .then(r => r.json()).then(res => {
            showToast(res.message || 'Deleted', 'success');
            bootstrap.Modal.getInstance(document.getElementById('deleteZoneModal'))?.hide();
            loadZones();
        }).catch(e => showToast('Error: ' + e.message, 'danger'));
}

