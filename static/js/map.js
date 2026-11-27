/* Interactive Noise Pollution Map - Most Important JS File */
let map, markersLayer, heatLayer, allSensors = [];

document.addEventListener('DOMContentLoaded', function() {
    initMap();
    loadSensorsOnMap();

    document.getElementById('filterZoneType')?.addEventListener('change', applyFilters);
    document.getElementById('filterNoiseLevel')?.addEventListener('change', applyFilters);
    document.getElementById('toggleMarkers')?.addEventListener('change', toggleLayers);
    document.getElementById('toggleHeatmap')?.addEventListener('change', toggleLayers);
    document.getElementById('btnRefresh')?.addEventListener('click', loadSensorsOnMap);
    document.getElementById('btnResetFilters')?.addEventListener('click', resetFilters);
});

function initMap() {
    map = L.map('noiseMap').setView([17.385, 78.4867], 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://openstreetmap.org">OpenStreetMap</a> contributors',
        maxZoom: 18
    }).addTo(map);
    markersLayer = L.layerGroup().addTo(map);
    setTimeout(() => map.invalidateSize(), 300);
}

function loadSensorsOnMap() {
    fetch('/api/sensors')
        .then(r => r.json())
        .then(sensors => {
            allSensors = sensors;
            renderSensors(sensors);
        })
        .catch(e => { console.error('Map load error:', e); showToast('Failed to load sensors', 'danger'); });
}

function renderSensors(sensors) {
    markersLayer.clearLayers();
    if (heatLayer) { map.removeLayer(heatLayer); heatLayer = null; }

    let heatData = [];
    let violationCount = 0;
    let totalNoise = 0, count = 0;

    sensors.forEach(s => {
        if (!s.latitude || !s.longitude) return;
        const reading = s.latest_reading || 0;
        const color = getNoiseColor(reading);
        const category = getNoiseCategory(reading);

        // Determine if this is a violation
        let isViolation = false;
        if (s.zone_type === 'hospital' || s.zone_type === 'school') {
            isViolation = reading > 50;
        } else if (s.zone_type === 'residential') {
            isViolation = reading > 55;
        } else if (s.zone_type === 'commercial') {
            isViolation = reading > 65;
        } else if (s.zone_type === 'industrial') {
            isViolation = reading > 75;
        } else if (s.zone_type === 'traffic') {
            isViolation = reading > 70;
        } else if (s.zone_type === 'silence') {
            isViolation = reading > 50;
        }

        if (isViolation) violationCount++;
        totalNoise += reading;
        count++;

        // Marker size - bigger for sensitive zones
        let radius = 10;
        let weight = 2;
        if (s.zone_type === 'school' || s.zone_type === 'hospital') {
            radius = 13;
            weight = 3;
        }

        const marker = L.circleMarker([s.latitude, s.longitude], {
            radius: radius,
            fillColor: color,
            color: isViolation ? '#dc3545' : '#fff',
            weight: weight,
            fillOpacity: 0.85
        });

        // Popup content
        const popupContent = `
            <div style="min-width:200px;">
                <h6 class="mb-1">${s.name}</h6>
                <table class="table table-sm table-borderless mb-1" style="font-size:0.8rem;">
                    <tr><td><strong>Sensor ID:</strong></td><td>SEN-${String(s.id).padStart(3,'0')}</td></tr>
                    <tr><td><strong>Noise Level:</strong></td><td><span style="color:${color};font-weight:700;">${reading} dB</span> (${category})</td></tr>
                    <tr><td><strong>Zone:</strong></td><td><span class="badge bg-secondary">${s.zone_type || 'N/A'}</span></td></tr>
                    <tr><td><strong>Status:</strong></td><td>${s.status === 'online' ? '<span class="text-success">● Online</span>' : '<span class="text-danger">● Offline</span>'}</td></tr>
                    <tr><td><strong>Location:</strong></td><td>${s.latitude.toFixed(4)}, ${s.longitude.toFixed(4)}</td></tr>
                    <tr><td><strong>Updated:</strong></td><td>${formatDateTime(s.last_updated)}</td></tr>
                </table>
                ${isViolation ? '<span class="badge bg-danger"><i class="fas fa-exclamation-triangle"></i> VIOLATION</span>' : '<span class="badge bg-success">Normal</span>'}
            </div>`;

        marker.bindPopup(popupContent);
        marker.bindTooltip(`${s.name}: ${reading} dB`, { direction: 'top' });

        // Store metadata for filtering
        marker._sensorData = s;
        markersLayer.addLayer(marker);

        // Heat data: [lat, lng, intensity]
        const intensity = Math.min(reading / 100, 1.0);
        heatData.push([s.latitude, s.longitude, intensity]);
    });

    // Create heatmap layer
    if (heatData.length > 0) {
        heatLayer = L.heatLayer(heatData, {
            radius: 30,
            blur: 20,
            maxZoom: 16,
            max: 1.0,
            gradient: { 0.2: 'blue', 0.4: 'lime', 0.6: 'yellow', 0.8: 'orange', 1.0: 'red' }
        });
        if (document.getElementById('toggleHeatmap')?.checked) {
            heatLayer.addTo(map);
        }
    }

    // Toggle visibility based on checkboxes
    toggleLayers();

    // Update summary
    document.getElementById('sensorCount').textContent = count;
    document.getElementById('violationMapCount').textContent = violationCount;
    document.getElementById('avgMapNoise').textContent = count > 0 ? (totalNoise / count).toFixed(1) : '--';
}

function applyFilters() {
    const zoneType = document.getElementById('filterZoneType')?.value || '';
    const noiseLevel = document.getElementById('filterNoiseLevel')?.value || '';

    let filtered = allSensors.filter(s => {
        if (zoneType && s.zone_type !== zoneType) return false;
        if (noiseLevel) {
            const r = s.latest_reading || 0;
            if (noiseLevel === 'low' && r >= 55) return false;
            if (noiseLevel === 'moderate' && (r < 55 || r >= 65)) return false;
            if (noiseLevel === 'high' && (r < 65 || r >= 75)) return false;
            if (noiseLevel === 'very_high' && r < 75) return false;
        }
        return true;
    });

    renderSensors(filtered);
}

function toggleLayers() {
    const showMarkers = document.getElementById('toggleMarkers')?.checked;
    const showHeat = document.getElementById('toggleHeatmap')?.checked;

    if (showMarkers) { map.addLayer(markersLayer); } else { map.removeLayer(markersLayer); }
    if (heatLayer) {
        if (showHeat) { map.addLayer(heatLayer); } else { map.removeLayer(heatLayer); }
    }
}

function resetFilters() {
    document.getElementById('filterZoneType').value = '';
    document.getElementById('filterNoiseLevel').value = '';
    document.getElementById('toggleMarkers').checked = true;
    document.getElementById('toggleHeatmap').checked = true;
    renderSensors(allSensors);
}

