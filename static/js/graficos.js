(() => {
    const raw = window.registrosData || [];
    const records = raw.slice(-40).map((r, i) => {
        let potencia = Number(r.potencia ?? 0);
        if (potencia > 20) potencia = potencia / 1000;
        return {
            label: r.horario || `Registro ${i + 1}`,
            vazao: Number(r.vazao ?? 0),
            potencia,
            nivel: Number(r.nivel ?? 0)
        };
    });

    function drawChart(id, key, unit, lineClass) {
        const svg = document.getElementById(id);
        if (!svg || !records.length) return;
        const width = 900, height = 300, pad = {top: 24, right: 24, bottom: 46, left: 48};
        const w = width - pad.left - pad.right, h = height - pad.top - pad.bottom;
        const values = records.map(r => r[key]);
        const min = Math.min(...values), max = Math.max(...values);
        const range = (max - min) || 1;
        const x = i => pad.left + (records.length === 1 ? w / 2 : (i / (records.length - 1)) * w);
        const y = v => pad.top + h - ((v - min) / range) * h;
        const points = records.map((r, i) => `${x(i)},${y(r[key])}`).join(' ');
        const area = `${pad.left},${pad.top + h} ${points} ${x(records.length - 1)},${pad.top + h}`;
        const grid = [0, .25, .5, .75, 1].map(t => {
            const yy = pad.top + h - (t * h);
            const val = min + (t * range);
            return `<line x1="${pad.left}" y1="${yy}" x2="${pad.left + w}" y2="${yy}" class="chart-grid"/><text x="${pad.left - 10}" y="${yy + 4}" text-anchor="end" class="chart-axis">${val.toFixed(key === 'potencia' ? 2 : 1)}</text>`;
        }).join('');
        const dots = records.map((r, i) => `<circle cx="${x(i)}" cy="${y(r[key])}" r="5" class="chart-dot" data-index="${i}"><title>${r.label} — ${r[key].toFixed(key === 'potencia' ? 2 : 1)} ${unit}</title></circle>`).join('');
        svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
        svg.innerHTML = `${grid}<polygon points="${area}" class="chart-area"/><polyline points="${points}" class="${lineClass}" fill="none"/>${dots}<text x="${pad.left}" y="${height - 12}" class="chart-axis">${records[0].label}</text><text x="${pad.left + w}" y="${height - 12}" text-anchor="end" class="chart-axis">${records[records.length - 1].label}</text>`;
    }

    drawChart('vazaoChart', 'vazao', 'L/s', 'chart-line');
    drawChart('potenciaChart', 'potencia', 'kW', 'chart-line chart-line-alt');
    drawChart('nivelChart', 'nivel', '%', 'chart-line chart-line-lime');
})();
