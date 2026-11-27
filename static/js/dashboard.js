/* Dashboard Page JavaScript */
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardStats();
    loadHourlyChart();
    loadZoneChart();
    initDashboardMap();

    document.getElementById('btnGenerate')?.addEventListener('click', () => {
        showToast('Generating new readings...', 'info');
        fetch('/api/simulate/generate', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({num_readings: 500, hours_back: 48}) })
            .then(r => r.json()).then(data => { showToast(data.message, 'success'); setTimeout(() => location.reload(), 1000); })
            .catch(e => showToast('Error: ' + e.message, 'danger'));
    });

    document.getElementById('btnDetect')?.addEventListener('click', () => {
        fetch('/api/violations/detect', { method: 'POST' })
            .then(r => r.json()).then(data => { showToast(data.message, 'success'); loadDashboardStats(); })
            .catch(e => showToast('Error: ' + e.message, 'danger'));
    });
});

function loadDashboardStats() {
    fetch('/api/dashboard/stats')
        .then(r => r.json())
        .then(data => {
            document.getElementById('totalSensors').textContent = data.active_sensors || 0;
            document.getElementById('avgNoise').textContent = data.avg_noise_level || 0;
            document.getElementById('violationCount').textContent = data.violation_count || 0;
            document.getElementById('monitoredSensitive').textContent = data.monitored_sensitive || 0;
            document.getElementById('maxNoise').textContent = data.max_noise ? data.max_noise.level : 0;
            document.getElementById('riskLevel').textContent = data.risk_level || 'N/A';
            document.getElementById('lastUpdated').textContent = new Date().toLocaleString('en-IN');

            // Color the risk level
            const riskEl = document.getElementById('riskLevel');
            const riskColors = { Low: 'text-success', Moderate: 'text-warning', High: 'text-orange', Critical: 'text-danger' };
            riskEl.className = 'mb-0 ' + (riskColors[data.risk_level] || '');

            // Color avg noise
            const avgEl = document.getElementById('avgNoise');
            avgEl.style.color = getNoiseColor(data.avg_noise_level);

            // Recent activity
            const actDiv = document.getElementById('recentActivity');
            if (data.recent_activity && data.recent_activity.length > 0) {
                actDiv.innerHTML = data.recent_activity.map(a => {
                    const sevColors = { low: 'success', medium: 'warning', high: 'warning', critical: 'danger' };
                    return `<div class="activity-item d-flex justify-content-between align-items-center">
                        <div><span class="badge bg-${sevColors[a.severity] || 'secondary'} me-2">${a.severity || 'info'}</span>${a.message}</div>
                        <small class="text-muted">${formatDateTime(a.timestamp)}</small></div>`;
                }).join('');
            } else {
                actDiv.innerHTML = '<p class="text-muted text-center">No recent activity. Generate readings to see data.</p>';
            }
        })
        .catch(e => console.error('Dashboard stats error:', e));
}

let hourlyChartInstance = null;
function loadHourlyChart() {
    fetch('/api/analytics/hourly')
        .then(r => r.json())
        .then(data => {
            const ctx = document.getElementById('hourlyChart');
            if (!ctx) return;
            if (hourlyChartInstance) hourlyChartInstance.destroy();
            hourlyChartInstance = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels || [],
                    datasets: [{
                        label: 'Avg Noise Level (dB)',
                        data: data.data || [],
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52,152,219,0.1)',
                        fill: true,
                        tension: 0.4,
                        pointRadius: 3,
                        pointBackgroundColor: '#3498db'
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { beginAtZero: false, title: { display: true, text: 'dB' } },
                        x: { title: { display: true, text: 'Hour' } }
                    }
                }
            });
        })
        .catch(e => console.error('Hourly chart error:', e));
}

let zoneChartInstance = null;
function loadZoneChart() {
    fetch('/api/analytics/zones')
        .then(r => r.json())
        .then(data => {
            const ctx = document.getElementById('zoneChart');
            if (!ctx) return;
            if (zoneChartInstance) zoneChartInstance.destroy();
            const colors = data.map(z => getNoiseColor(z.avg_noise));
            zoneChartInstance = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: data.map(z => z.zone_name),
                    datasets: [{ data: data.map(z => z.avg_noise), backgroundColor: colors, borderWidth: 2 }]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { position: 'bottom', labels: { font: { size: 10 }, boxWidth: 12 } } }
                }
            });
        })
        .catch(e => console.error('Zone chart error:', e));
}

let dashMap = null;
function initDashboardMap() {
    const el = document.getElementById('dashboardMap');
    if (!el) return;
    dashMap = L.map('dashboardMap').setView([17.385, 78.4867], 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(dashMap);

    fetch('/api/sensors')
        .then(r => r.json())
        .then(sensors => {
            sensors.forEach(s => {
                if (!s.latitude || !s.longitude) return;
                const reading = s.latest_reading || 0;
                const color = getNoiseColor(reading);
                L.circleMarker([s.latitude, s.longitude], {
                    radius: 7, fillColor: color, color: '#fff', weight: 1, fillOpacity: 0.8
                }).addTo(dashMap).bindTooltip(`${s.name}: ${reading || '--'} dB`);
            });
        })
        .catch(e => console.error('Map error:', e));

    setTimeout(() => dashMap.invalidateSize(), 300);
}

