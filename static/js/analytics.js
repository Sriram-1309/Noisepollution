/* Time-Series Analytics Page JavaScript */
let hourlyTrendChart, dailyAvgChart, zoneCompareChart, peakHoursChart, sensitiveChart;

document.addEventListener('DOMContentLoaded', function() {
    loadDropdowns();
    loadAllCharts();
    document.getElementById('btnApplyAnalytics')?.addEventListener('click', loadAllCharts);
});

function loadDropdowns() {
    fetch('/api/sensors').then(r => r.json()).then(sensors => {
        const sel = document.getElementById('analyticsSensor');
        if (sel) sel.innerHTML = '<option value="">All Sensors</option>' + sensors.map(s => `<option value="${s.id}">${s.name}</option>`).join('');
    });
    fetch('/api/zones').then(r => r.json()).then(zones => {
        const sel = document.getElementById('analyticsZone');
        if (sel) sel.innerHTML = '<option value="">All Zones</option>' + zones.map(z => `<option value="${z.id}">${z.name}</option>`).join('');
    });
}

function getFilters() {
    return {
        sensor_id: document.getElementById('analyticsSensor')?.value || '',
        zone_id: document.getElementById('analyticsZone')?.value || '',
        start_date: document.getElementById('analyticsStart')?.value || '',
        end_date: document.getElementById('analyticsEnd')?.value || '',
        interval: document.getElementById('analyticsInterval')?.value || 'hour'
    };
}

function loadAllCharts() {
    loadHourlyTrends();
    loadDailyAverages();
    loadZoneComparison();
    loadPeakHours();
    loadSensitiveComparison();
}

function loadHourlyTrends() {
    const f = getFilters();
    let params = new URLSearchParams();
    if (f.sensor_id) params.append('sensor_id', f.sensor_id);
    if (f.zone_id) params.append('zone_id', f.zone_id);

    fetch('/api/analytics/hourly?' + params.toString()).then(r => r.json()).then(data => {
        const ctx = document.getElementById('hourlyTrendChart');
        if (!ctx) return;
        if (hourlyTrendChart) hourlyTrendChart.destroy();
        hourlyTrendChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels || [],
                datasets: [{ label: 'Avg Noise (dB)', data: data.data || [],
                    borderColor: '#3498db', backgroundColor: 'rgba(52,152,219,0.1)',
                    fill: true, tension: 0.4, pointRadius: 3 }]
            },
            options: { responsive: true, scales: { y: { beginAtZero: false, title: { display: true, text: 'dB' } } } }
        });
    });
}

function loadDailyAverages() {
    const f = getFilters();
    let params = new URLSearchParams();
    if (f.sensor_id) params.append('sensor_id', f.sensor_id);
    if (f.zone_id) params.append('zone_id', f.zone_id);

    fetch('/api/analytics/daily?' + params.toString()).then(r => r.json()).then(data => {
        const ctx = document.getElementById('dailyAvgChart');
        if (!ctx) return;
        if (dailyAvgChart) dailyAvgChart.destroy();
        const colors = (data.data || []).map(v => getNoiseColor(v));
        dailyAvgChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels || [],
                datasets: [{ label: 'Daily Avg (dB)', data: data.data || [],
                    backgroundColor: colors, borderRadius: 5 }]
            },
            options: { responsive: true, scales: { y: { beginAtZero: false, title: { display: true, text: 'dB' } } } }
        });
    });
}

function loadZoneComparison() {
    fetch('/api/analytics/zones').then(r => r.json()).then(data => {
        const ctx = document.getElementById('zoneCompareChart');
        if (!ctx) return;
        if (zoneCompareChart) zoneCompareChart.destroy();
        const colors = data.map(z => getNoiseColor(z.avg_noise));
        zoneCompareChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(z => z.zone_name),
                datasets: [
                    { label: 'Avg', data: data.map(z => z.avg_noise), backgroundColor: colors, borderRadius: 4 },
                    { label: 'Max', data: data.map(z => z.max_noise), backgroundColor: 'rgba(220,53,69,0.3)', borderRadius: 4 }
                ]
            },
            options: { responsive: true, indexAxis: 'y', scales: { x: { title: { display: true, text: 'dB' } } },
                plugins: { legend: { position: 'top' } } }
        });
    });
}

function loadPeakHours() {
    const f = getFilters();
    let params = new URLSearchParams();
    if (f.sensor_id) params.append('sensor_id', f.sensor_id);
    if (f.zone_id) params.append('zone_id', f.zone_id);

    fetch('/api/analytics/peak-hours?' + params.toString()).then(r => r.json()).then(data => {
        const ctx = document.getElementById('peakHoursChart');
        if (!ctx) return;
        if (peakHoursChart) peakHoursChart.destroy();
        const sorted = data.sort((a,b) => a.hour - b.hour);
        const colors = sorted.map(h => getNoiseColor(h.avg_noise));
        peakHoursChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: sorted.map(h => `${String(h.hour).padStart(2,'0')}:00`),
                datasets: [{ label: 'Avg Noise (dB)', data: sorted.map(h => h.avg_noise),
                    backgroundColor: colors, borderRadius: 4 }]
            },
            options: { responsive: true, scales: { y: { title: { display: true, text: 'dB' } } },
                plugins: { legend: { display: false } } }
        });
    });
}

function loadSensitiveComparison() {
    fetch('/api/analytics/zones').then(r => r.json()).then(zones => {
        const sensitive = zones.filter(z => z.zone_type === 'school' || z.zone_type === 'hospital');
        if (!sensitive.length) return;

        fetch('/api/settings/limits').then(r => r.json()).then(limits => {
            const limitMap = {};
            limits.forEach(l => { limitMap[l.zone_type] = l.day_limit_db; });

            const ctx = document.getElementById('sensitiveChart');
            if (!ctx) return;
            if (sensitiveChart) sensitiveChart.destroy();

            sensitiveChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: sensitive.map(z => z.zone_name),
                    datasets: [
                        { label: 'Actual Avg (dB)', data: sensitive.map(z => z.avg_noise),
                            backgroundColor: sensitive.map(z => z.avg_noise > (limitMap[z.zone_type]||50) ? '#dc3545' : '#28a745'), borderRadius: 4 },
                        { label: 'Limit (dB)', data: sensitive.map(z => limitMap[z.zone_type] || 50),
                            backgroundColor: 'rgba(52,152,219,0.3)', borderRadius: 4 }
                    ]
                },
                options: { responsive: true, scales: { y: { title: { display: true, text: 'dB' } } } }
            });
        });
    });
}

