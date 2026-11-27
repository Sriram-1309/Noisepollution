/* Reports Page JavaScript */
let peakPeriodsChartInstance = null;

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('btnGenerateReport')?.addEventListener('click', generateReport);
    document.getElementById('btnExportReadings')?.addEventListener('click', exportReadingsCSV);
    document.getElementById('btnExportViolations')?.addEventListener('click', exportViolationsCSV);
    document.getElementById('btnPrint')?.addEventListener('click', () => window.print());
    generateReport(); // Auto-load on page open
});

function getReportFilters() {
    return {
        start_date: document.getElementById('reportStartDate')?.value || '',
        end_date: document.getElementById('reportEndDate')?.value || '',
        zone_type: document.getElementById('reportZoneType')?.value || ''
    };
}

function generateReport() {
    const f = getReportFilters();
    let params = new URLSearchParams();
    if (f.start_date) params.append('start_date', f.start_date);
    if (f.end_date) params.append('end_date', f.end_date + 'T23:59:59');
    if (f.zone_type) params.append('zone_type', f.zone_type);

    fetch('/api/reports/summary?' + params.toString())
        .then(r => r.json())
        .then(data => {
            // Summary cards
            document.getElementById('rptTotalReadings').textContent = data.total_readings || 0;
            document.getElementById('rptTotalViolations').textContent = data.total_violations || 0;

            const topZone = data.most_affected_zones?.[0];
            document.getElementById('rptMostAffected').textContent = topZone ? topZone.zone_name : 'N/A';

            const peakHour = data.peak_periods?.[0];
            document.getElementById('rptPeakHour').textContent = peakHour ? `${String(peakHour.hour).padStart(2,'0')}:00 (${peakHour.avg_noise} dB)` : 'N/A';

            // Most affected zones
            const azContainer = document.getElementById('affectedZonesContainer');
            if (data.most_affected_zones?.length) {
                azContainer.innerHTML = `<table class="table table-sm"><thead><tr><th>Zone</th><th>Type</th><th>Avg (dB)</th><th>Max (dB)</th><th>Violations</th></tr></thead><tbody>${
                    data.most_affected_zones.map(z => `<tr><td>${z.zone_name}</td><td><span class="badge bg-secondary">${z.zone_type}</span></td><td style="color:${getNoiseColor(z.mean)}">${z.mean}</td><td>${z.max}</td><td>${z.violation_count}</td></tr>`).join('')
                }</tbody></table>`;
            } else { azContainer.innerHTML = '<p class="text-muted">No data</p>'; }

            // Peak periods chart
            if (data.peak_periods?.length) {
                const ctx = document.getElementById('peakPeriodsChart');
                if (peakPeriodsChartInstance) peakPeriodsChartInstance.destroy();
                peakPeriodsChartInstance = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: data.peak_periods.map(p => `${String(p.hour).padStart(2,'0')}:00`),
                        datasets: [{ label: 'Avg Noise (dB)', data: data.peak_periods.map(p => p.avg_noise),
                            backgroundColor: data.peak_periods.map(p => getNoiseColor(p.avg_noise)), borderRadius: 5 }]
                    },
                    options: { responsive: true, plugins: { legend: { display: false } } }
                });
            }

            // Sensitive risk
            const srContainer = document.getElementById('sensitiveRiskContainer');
            if (data.sensitive_locations_risk?.length) {
                srContainer.innerHTML = data.sensitive_locations_risk.map(s => {
                    const statusColors = { Safe: 'success', 'At Risk': 'warning', Critical: 'danger' };
                    return `<div class="d-flex justify-content-between align-items-center p-2 border-bottom">
                        <div><strong>${s.zone_name}</strong> <span class="badge bg-secondary">${s.zone_type}</span></div>
                        <div>Avg: <strong style="color:${getNoiseColor(s.avg_noise)}">${s.avg_noise} dB</strong> / Limit: ${s.limit} dB
                        <span class="badge bg-${statusColors[s.status]||'secondary'} ms-2">${s.status}</span></div></div>`;
                }).join('');
            } else { srContainer.innerHTML = '<p class="text-muted">No sensitive locations data</p>'; }

            // Top hotspots
            const thContainer = document.getElementById('topHotspotsContainer');
            if (data.top_hotspots?.length) {
                thContainer.innerHTML = `<ol class="mb-0">${data.top_hotspots.map(h =>
                    `<li><strong>${h.zone_name}</strong> - Avg: ${h.avg_noise} dB, Violations: ${h.violation_count}</li>`
                ).join('')}</ol>`;
            } else { thContainer.innerHTML = '<p class="text-muted">No hotspot data</p>'; }

            // Recommendations
            const recContainer = document.getElementById('reportRecommendations');
            if (data.recommendations?.length) {
                recContainer.innerHTML = data.recommendations.map(r =>
                    `<div class="recommendation-card priority-${r.priority}"><strong>${r.recommendation}</strong>
                    <span class="badge bg-${r.priority==='high'?'danger':r.priority==='medium'?'warning':'success'}">${r.priority}</span>
                    <p class="small text-muted mb-0 mt-1">${r.details}</p></div>`
                ).join('');
            } else { recContainer.innerHTML = '<p class="text-muted">No recommendations</p>'; }

            // Summary text
            document.getElementById('reportSummaryText').innerHTML = `<p>${data.summary_text || 'No summary available.'}</p>`;
        })
        .catch(e => showToast('Error generating report: ' + e.message, 'danger'));
}

function exportReadingsCSV() {
    const f = getReportFilters();
    let params = new URLSearchParams();
    if (f.start_date) params.append('start_date', f.start_date);
    if (f.end_date) params.append('end_date', f.end_date);
    if (f.zone_type) params.append('zone_type', f.zone_type);
    window.location.href = '/api/reports/export/readings?' + params.toString();
}

function exportViolationsCSV() {
    const f = getReportFilters();
    let params = new URLSearchParams();
    if (f.start_date) params.append('start_date', f.start_date);
    if (f.end_date) params.append('end_date', f.end_date);
    if (f.zone_type) params.append('zone_type', f.zone_type);
    window.location.href = '/api/reports/export/violations?' + params.toString();
}

