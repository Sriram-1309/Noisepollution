/* Hotspot Analysis Page JavaScript */
let hotspotRankChartInstance = null, hotspotMap = null;

document.addEventListener('DOMContentLoaded', function() {
    loadHotspots();
    loadHotspotStats();
    loadRecommendations();
});

function loadHotspots() {
    fetch('/api/hotspots?top_n=5').then(r => r.json()).then(hotspots => {
        renderHotspotCards(hotspots);
        renderHotspotMap(hotspots);
        renderHotspotChart(hotspots);
    }).catch(e => showToast('Error loading hotspots', 'danger'));
}

function renderHotspotCards(hotspots) {
    const container = document.getElementById('hotspotsContainer');
    if (!hotspots.length) {
        container.innerHTML = '<div class="col-12 text-center text-muted p-4">No hotspot data available. Generate readings first.</div>';
        return;
    }
    container.innerHTML = hotspots.map(h => {
        const medals = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣'];
        return `<div class="col-lg-4 col-md-6">
            <div class="card h-100 border-start border-danger border-3">
                <div class="card-body">
                    <div class="d-flex align-items-center mb-2">
                        <div class="hotspot-rank rank-${h.rank} me-3">${h.rank}</div>
                        <div>
                            <h6 class="mb-0">${h.zone_name}</h6>
                            <span class="badge bg-secondary">${h.zone_type}</span>
                        </div>
                    </div>
                    <div class="row text-center mt-3">
                        <div class="col-4">
                            <div class="small text-muted">Avg Noise</div>
                            <strong style="color:${getNoiseColor(h.avg_noise)}">${h.avg_noise} dB</strong>
                        </div>
                        <div class="col-4">
                            <div class="small text-muted">Max</div>
                            <strong class="text-danger">${h.max_noise} dB</strong>
                        </div>
                        <div class="col-4">
                            <div class="small text-muted">Violations</div>
                            <strong class="text-warning">${h.violation_count}</strong>
                        </div>
                    </div>
                    <div class="mt-2 text-end"><small class="text-muted">Score: ${h.score}</small></div>
                </div>
            </div>
        </div>`;
    }).join('');
}

function renderHotspotMap(hotspots) {
    const el = document.getElementById('hotspotMap');
    if (!el) return;
    if (hotspotMap) { hotspotMap.remove(); }
    hotspotMap = L.map('hotspotMap').setView([17.385, 78.4867], 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap'
    }).addTo(hotspotMap);

    hotspots.forEach(h => {
        const size = Math.max(300, h.score * 5);
        const color = getNoiseColor(h.avg_noise);
        L.circle([h.latitude, h.longitude], {
            radius: size, fillColor: color, color: color, fillOpacity: 0.3, weight: 2
        }).addTo(hotspotMap).bindPopup(`<strong>#${h.rank} ${h.zone_name}</strong><br>Avg: ${h.avg_noise} dB<br>Violations: ${h.violation_count}`);

        L.marker([h.latitude, h.longitude]).addTo(hotspotMap)
            .bindTooltip(`#${h.rank} ${h.zone_name}`, { permanent: true, direction: 'top', className: 'hotspot-label' });
    });

    setTimeout(() => hotspotMap.invalidateSize(), 300);
}

function renderHotspotChart(hotspots) {
    const ctx = document.getElementById('hotspotRankChart');
    if (!ctx) return;
    if (hotspotRankChartInstance) hotspotRankChartInstance.destroy();
    hotspotRankChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: hotspots.map(h => h.zone_name),
            datasets: [{ label: 'Hotspot Score', data: hotspots.map(h => h.score),
                backgroundColor: hotspots.map(h => getNoiseColor(h.avg_noise)), borderRadius: 6 }]
        },
        options: { responsive: true, indexAxis: 'y',
            scales: { x: { title: { display: true, text: 'Score' } } },
            plugins: { legend: { display: false } } }
    });
}

function loadHotspotStats() {
    fetch('/api/hotspots/stats').then(r => r.json()).then(data => {
        const tbody = document.getElementById('statsTableBody');
        const stats = data.zone_statistics || [];
        if (!stats.length) {
            tbody.innerHTML = '<tr><td colspan="9" class="text-center text-muted">No data</td></tr>';
            return;
        }
        tbody.innerHTML = stats.map(s => `<tr>
            <td><strong>${s.zone_name}</strong></td><td><span class="badge bg-secondary">${s.zone_type}</span></td>
            <td>${s.mean}</td><td>${s.median}</td><td>${s.min}</td><td>${s.max}</td>
            <td>${s.std_dev}</td><td>${s.reading_count}</td><td><span class="badge bg-danger">${s.violation_count}</span></td>
        </tr>`).join('');
    });
}

function loadRecommendations() {
    fetch('/api/hotspots/recommendations').then(r => r.json()).then(recs => {
        const container = document.getElementById('recommendationsContainer');
        if (!recs.length) {
            container.innerHTML = '<p class="text-muted">No recommendations at this time.</p>';
            return;
        }
        container.innerHTML = recs.map(r => {
            const icons = { high: 'fa-exclamation-circle text-danger', medium: 'fa-exclamation-triangle text-warning', low: 'fa-info-circle text-info' };
            return `<div class="recommendation-card priority-${r.priority}">
                <div class="d-flex align-items-start">
                    <i class="fas ${icons[r.priority] || icons.low} me-3 mt-1 fa-lg"></i>
                    <div>
                        <strong>${r.recommendation}</strong>
                        <span class="badge bg-${r.priority === 'high' ? 'danger' : r.priority === 'medium' ? 'warning' : 'success'} ms-2">${r.priority}</span>
                        <p class="small text-muted mb-0 mt-1">${r.details}</p>
                    </div>
                </div>
            </div>`;
        }).join('');
    });
}

