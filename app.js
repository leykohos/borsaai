/* ───────────────────────────────────────────
   BorsaAI – app.js  (Candlestick + Periyot Seçici)
─────────────────────────────────────────── */

const API = '';

/* ── Renk Paleti ── */
const C = {
  blue:    '#00d4ff',
  purple:  '#a855f7',
  green:   '#22c55e',
  red:     '#f43f5e',
  orange:  '#f59e0b',
  indigo:  '#6366f1',
  gridLine:'rgba(99,156,255,0.06)',
  gridText:'#475569',
};

Chart.defaults.color       = C.gridText;
Chart.defaults.borderColor = C.gridLine;
Chart.defaults.font.family = "'Inter', system-ui, sans-serif";

/* ── Durum ── */
let currentInterval = '1d';
let currentChartType = 'line';  // 'line' | 'candlestick'
let charts = {};

/* ── Yardımcılar ── */
function rgba(hex, a) {
  const r = parseInt(hex.slice(1,3),16);
  const g = parseInt(hex.slice(3,5),16);
  const b = parseInt(hex.slice(5,7),16);
  return `rgba(${r},${g},${b},${a})`;
}

function colorRet(val) {
  if (val === null || val === undefined) return `<span class="ret-na">—</span>`;
  const cls = val >= 0 ? 'ret-pos' : 'ret-neg';
  return `<span class="${cls}">${val >= 0 ? '+' : ''}${val}%</span>`;
}

function colorRsi(rsi) {
  if (rsi < 35) return C.red;
  if (rsi > 65) return C.orange;
  return C.green;
}

const PERIOD_LABELS = {
  '1h':  'Son 5 Gün · Saatlik',
  '1d':  'Son 3 Yıl · Günlük',
  '1wk': 'Son 5 Yıl · Haftalık',
  '1mo': 'Son 10 Yıl · Aylık',
};

const TIME_UNITS = {
  '1h':  'hour',
  '1d':  'day',
  '1wk': 'week',
  '1mo': 'month',
};

/* ── Ortak Chart Options ── */
function baseOpts(interval = '1d') {
  return {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 400, easing: 'easeInOutQuart' },
    interaction: { mode: 'index', intersect: false },
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: 'rgba(13,22,39,0.95)',
        borderColor: 'rgba(99,156,255,0.2)',
        borderWidth: 1,
        padding: 10,
        titleFont: { size: 11 },
        bodyFont: { size: 11 },
      },
    },
    scales: {
      x: {
        type: 'time',
        time: {
          unit: TIME_UNITS[interval] || 'day',
          tooltipFormat: interval === '1h' ? 'dd MMM HH:mm' : 'dd MMM yyyy',
          displayFormats: {
            hour:  'dd MMM HH:mm',
            day:   'dd MMM yy',
            week:  'dd MMM yy',
            month: 'MMM yyyy',
          },
        },
        grid: { color: C.gridLine },
        ticks: { font: { size: 10 }, maxTicksLimit: 14 },
      },
      y: {
        grid: { color: C.gridLine },
        ticks: { font: { size: 10 } },
      },
    },
  };
}

/* ── Mum Grafiği (Candlestick) ── */
function buildCandlestickChart(data) {
  const ctx = document.getElementById('priceChart').getContext('2d');
  if (charts.price) charts.price.destroy();

  // chartjs-chart-financial OHLC formatı: {x, o, h, l, c}
  const ohlc = data.dates.map((d, i) => ({
    x: new Date(d).getTime(),
    o: data.open[i],
    h: data.high[i],
    l: data.low[i],
    c: data.close[i],
  })).filter(p => p.o && p.h && p.l && p.c);

  const bbUpper = data.dates.map((d, i) => ({ x: new Date(d).getTime(), y: data.bb_upper[i] }));
  const bbMid   = data.dates.map((d, i) => ({ x: new Date(d).getTime(), y: data.bb_middle[i] }));
  const bbLower = data.dates.map((d, i) => ({ x: new Date(d).getTime(), y: data.bb_lower[i] }));

  const opts = baseOpts(currentInterval);
  opts.scales.x.type = 'time';

  charts.price = new Chart(ctx, {
    type: 'candlestick',
    data: {
      datasets: [
        {
          label: 'Üst Band',
          type: 'line',
          data: bbUpper,
          borderColor: rgba(C.purple, 0.55),
          borderWidth: 1,
          borderDash: [4,3],
          pointRadius: 0,
          fill: false,
          order: 1,
        },
        {
          label: 'SMA20',
          type: 'line',
          data: bbMid,
          borderColor: rgba(C.indigo, 0.65),
          borderWidth: 1,
          borderDash: [2,4],
          pointRadius: 0,
          fill: false,
          order: 1,
        },
        {
          label: 'Alt Band',
          type: 'line',
          data: bbLower,
          borderColor: rgba(C.red, 0.55),
          borderWidth: 1,
          borderDash: [4,3],
          pointRadius: 0,
          fill: false,
          order: 1,
        },
        {
          label: 'ALBRK',
          type: 'candlestick',
          data: ohlc,
          color: {
            up: C.green,
            down: C.red,
            unchanged: C.gridText,
          },
          borderColor: {
            up: C.green,
            down: C.red,
            unchanged: C.gridText,
          },
          order: 0,
        },
      ],
    },
    options: {
      ...opts,
      plugins: {
        ...opts.plugins,
        tooltip: {
          ...opts.plugins.tooltip,
          callbacks: {
            label: ctx => {
              if (ctx.dataset.type === 'candlestick' || ctx.dataset.label === 'ALBRK') {
                const p = ctx.raw;
                return [
                  ` A: ${p.o?.toFixed(2)} ₺`,
                  ` Y: ${p.h?.toFixed(2)} ₺`,
                  ` D: ${p.l?.toFixed(2)} ₺`,
                  ` K: ${p.c?.toFixed(2)} ₺`,
                ];
              }
              return ` ${ctx.dataset.label}: ${ctx.parsed?.y?.toFixed(2)} ₺`;
            },
          },
        },
      },
    },
  });

  // Update legend
  document.getElementById('priceLegend').innerHTML = `
    <span class="legend-item"><span class="legend-dot" style="background:${C.green}"></span>Yükseliş</span>
    <span class="legend-item"><span class="legend-dot" style="background:${C.red}"></span>Düşüş</span>
    <span class="legend-item"><span class="legend-dot" style="background:${C.purple};opacity:.6"></span>Üst Band</span>
    <span class="legend-item"><span class="legend-dot" style="background:${C.red};opacity:.6"></span>Alt Band</span>
  `;
  document.getElementById('priceChartTitle').textContent = 'Mum Grafiği & Bollinger Bantları';
}

/* ── Çizgi Grafiği (Line + Bollinger) ── */
function buildLineChart(data) {
  const ctx = document.getElementById('priceChart').getContext('2d');
  if (charts.price) charts.price.destroy();

  const grad = ctx.createLinearGradient(0, 0, 0, 280);
  grad.addColorStop(0, rgba(C.blue, 0.25));
  grad.addColorStop(1, rgba(C.blue, 0.0));

  const toXY = (arr) => data.dates.map((d,i) => ({ x: new Date(d).getTime(), y: arr[i] }));

  const opts = baseOpts(currentInterval);
  charts.price = new Chart(ctx, {
    type: 'line',
    data: {
      datasets: [
        {
          label: 'Üst Band',
          data: toXY(data.bb_upper),
          borderColor: rgba(C.purple, 0.6),
          borderWidth: 1,
          borderDash: [4,3],
          pointRadius: 0,
          fill: false,
          tension: 0.3,
        },
        {
          label: 'SMA20',
          data: toXY(data.bb_middle),
          borderColor: rgba(C.indigo, 0.7),
          borderWidth: 1,
          borderDash: [2,4],
          pointRadius: 0,
          fill: false,
          tension: 0.3,
        },
        {
          label: 'Alt Band',
          data: toXY(data.bb_lower),
          borderColor: rgba(C.red, 0.6),
          borderWidth: 1,
          borderDash: [4,3],
          pointRadius: 0,
          fill: false,
          tension: 0.3,
        },
        {
          label: 'Kapanış',
          data: toXY(data.close),
          borderColor: C.blue,
          borderWidth: 2,
          backgroundColor: grad,
          pointRadius: 0,
          fill: true,
          tension: 0.3,
          order: 0,
        },
      ],
    },
    options: {
      ...opts,
      plugins: {
        ...opts.plugins,
        tooltip: {
          ...opts.plugins.tooltip,
          callbacks: {
            label: ctx => ` ${ctx.dataset.label}: ${ctx.parsed.y?.toFixed(2)} ₺`,
          },
        },
      },
    },
  });

  document.getElementById('priceLegend').innerHTML = `
    <span class="legend-item"><span class="legend-dot" style="background:${C.blue}"></span>Kapanış</span>
    <span class="legend-item"><span class="legend-dot" style="background:${C.purple}"></span>Üst Band</span>
    <span class="legend-item"><span class="legend-dot" style="background:${C.indigo}"></span>SMA20</span>
    <span class="legend-item"><span class="legend-dot" style="background:${C.red}"></span>Alt Band</span>
  `;
  document.getElementById('priceChartTitle').textContent = 'Fiyat & Bollinger Bantları';
}

/* ── MACD Chart ── */
function buildMacdChart(data) {
  const ctx = document.getElementById('macdChart').getContext('2d');
  if (charts.macd) charts.macd.destroy();

  const toXY = (arr) => data.dates.map((d,i) => ({ x: new Date(d).getTime(), y: arr[i] }));
  const histColors = data.macd_hist.map(v => v >= 0 ? rgba(C.green, 0.7) : rgba(C.red, 0.7));

  charts.macd = new Chart(ctx, {
    type: 'bar',
    data: {
      datasets: [
        {
          label: 'Histogram',
          data: toXY(data.macd_hist),
          backgroundColor: histColors,
          borderRadius: 2,
          type: 'bar',
          order: 2,
        },
        {
          label: 'MACD',
          data: toXY(data.macd),
          borderColor: C.blue,
          borderWidth: 1.5,
          pointRadius: 0,
          fill: false,
          tension: 0.2,
          type: 'line',
          order: 0,
        },
        {
          label: 'Signal',
          data: toXY(data.macd_signal),
          borderColor: C.orange,
          borderWidth: 1.5,
          pointRadius: 0,
          fill: false,
          tension: 0.2,
          type: 'line',
          order: 1,
        },
      ],
    },
    options: baseOpts(currentInterval),
  });
}

/* ── RSI Chart ── */
function buildRsiChart(data) {
  const ctx = document.getElementById('rsiChart').getContext('2d');
  if (charts.rsi) charts.rsi.destroy();

  const toXY = (arr) => data.dates.map((d,i) => ({ x: new Date(d).getTime(), y: arr[i] }));
  const opts = baseOpts(currentInterval);
  opts.scales.y = { ...opts.scales.y, min: 0, max: 100, ticks: { font: { size: 10 }, stepSize: 20 } };

  charts.rsi = new Chart(ctx, {
    type: 'line',
    data: {
      datasets: [{
        label: 'RSI',
        data: toXY(data.rsi),
        borderColor: C.green,
        borderWidth: 1.5,
        segment: {
          borderColor: ctx => {
            const v = ctx.p1.parsed.y;
            return v < 35 ? C.red : v > 65 ? C.orange : C.green;
          },
        },
        pointRadius: 0,
        fill: false,
        tension: 0.2,
      }],
    },
    options: opts,
  });
}

/* ── Stochastic RSI Chart ── */
function buildStochChart(data) {
  const ctx = document.getElementById('stochChart').getContext('2d');
  if (charts.stoch) charts.stoch.destroy();

  const toXY = (arr) => data.dates.map((d,i) => ({ x: new Date(d).getTime(), y: arr[i] }));
  const opts = baseOpts(currentInterval);
  opts.scales.y = { ...opts.scales.y, min: 0, max: 100, ticks: { font: { size: 10 }, stepSize: 20 } };

  charts.stoch = new Chart(ctx, {
    type: 'line',
    data: {
      datasets: [
        {
          label: '%K',
          data: toXY(data.stoch_k),
          borderColor: C.blue,
          borderWidth: 1.5,
          pointRadius: 0,
          fill: false,
          tension: 0.2,
        },
        {
          label: '%D',
          data: toXY(data.stoch_d),
          borderColor: C.orange,
          borderWidth: 1,
          borderDash: [3,3],
          pointRadius: 0,
          fill: false,
          tension: 0.2,
        },
      ],
    },
    options: opts,
  });
}

/* ── Chart Type Switcher ── */
function setChartType(type) {
  currentChartType = type;
  document.getElementById('btnLine').classList.toggle('active', type === 'line');
  document.getElementById('btnCandle').classList.toggle('active', type === 'candlestick');
  // Sadece fiyat grafiğini yeniden çiz (data zaten var)
  if (window._lastData) {
    if (type === 'candlestick') buildCandlestickChart(window._lastData);
    else buildLineChart(window._lastData);
  }
}

/* ── Stats Bar ── */
function updateStats(data, signalCount) {
  const last = arr => {
    for (let j = arr.length - 1; j >= 0; j--) if (arr[j] !== null) return arr[j];
    return null;
  };

  const price = last(data.close);
  const rsi   = last(data.rsi);
  const macd  = last(data.macd);
  const macdH = last(data.macd_hist);
  const sk    = last(data.stoch_k);
  const bbU   = last(data.bb_upper);
  const bbL   = last(data.bb_lower);

  document.getElementById('valPrice').textContent    = price ? `${price.toFixed(2)} ₺` : '—';
  document.getElementById('headerPrice').textContent = price ? `${price.toFixed(2)} ₺` : '—';

  if (rsi !== null) {
    document.getElementById('valRsi').textContent = rsi.toFixed(1);
    document.getElementById('valRsi').style.color = colorRsi(rsi);
    document.getElementById('noteRsi').textContent = rsi < 35 ? '🔴 Aşırı Satım' : rsi > 65 ? '🟠 Aşırı Alım' : '🟢 Normal';
  }
  if (macd !== null) {
    document.getElementById('valMacd').textContent = macd.toFixed(4);
    document.getElementById('valMacd').style.color = macd >= 0 ? C.green : C.red;
    document.getElementById('noteMacd').textContent = macdH >= 0 ? '↑ Pozitif Momentum' : '↓ Negatif Momentum';
  }
  if (sk !== null) {
    document.getElementById('valStoch').textContent = sk.toFixed(1);
    document.getElementById('valStoch').style.color = sk < 20 ? C.red : sk > 80 ? C.orange : C.green;
  }
  if (price !== null && bbU !== null && bbL !== null) {
    let pos = 'Bantlar Arası', col = '#94a3b8';
    if (price > bbU) { pos = '↑ Üst Band Üstü'; col = C.orange; }
    else if (price < bbL) { pos = '↓ Alt Band Altı'; col = C.red; }
    document.getElementById('valBoll').textContent = pos;
    document.getElementById('valBoll').style.color = col;
  }
  document.getElementById('valSignals').textContent = signalCount ?? '—';
  document.getElementById('statusBadge').textContent = '✅ Veri Yüklendi';
  document.getElementById('statusBadge').classList.remove('badge-error');
}

/* ── Signal Table ── */
function buildSignalsTable(signals) {
  const tbody = document.getElementById('signalsBody');
  if (!signals || signals.length === 0) {
    tbody.innerHTML = '<tr><td colspan="8" class="loading-row">Sinyal bulunamadı.</td></tr>';
    return;
  }

  const withRet = signals.filter(s => s.ret_1m !== null);
  const avgRet1m = withRet.length ? (withRet.reduce((a,b) => a+b.ret_1m, 0)/withRet.length).toFixed(1) : null;
  const posCount = withRet.filter(s => s.ret_1m > 0).length;
  const successRate = withRet.length ? ((posCount/withRet.length)*100).toFixed(0) : null;

  document.getElementById('signalsSummary').innerHTML = `
    <div class="sum-box">
      <div class="sum-val accent">${signals.length}</div>
      <div class="sum-lbl">Toplam Sinyal</div>
    </div>
    <div class="sum-box">
      <div class="sum-val" style="color:${(avgRet1m ?? 0) >= 0 ? C.green : C.red}">${avgRet1m !== null ? (avgRet1m >= 0 ? '+' : '') + avgRet1m + '%' : '—'}</div>
      <div class="sum-lbl">Ort. 1A Getiri</div>
    </div>
    <div class="sum-box">
      <div class="sum-val" style="color:${C.blue}">${successRate !== null ? successRate + '%' : '—'}</div>
      <div class="sum-lbl">Başarı Oranı</div>
    </div>
  `;

  tbody.innerHTML = [...signals].reverse().map(s => `
    <tr>
      <td>${s.date}</td>
      <td><strong>${s.price} ₺</strong></td>
      <td style="color:${colorRsi(s.rsi)}">${s.rsi}</td>
      ${[s.ret_1w, s.ret_2w, s.ret_1m, s.ret_3m].map(r => `<td>${colorRet(r)}</td>`).join('')}
      <td><span class="reason-tag">${s.reason.split(' + ')[0]}</span></td>
    </tr>
  `).join('');
}

/* ── Period Switcher ── */
function switchPeriod(interval) {
  currentInterval = interval;

  // Buton aktifliklerini güncelle
  document.querySelectorAll('.period-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.interval === interval);
  });

  document.getElementById('periodInfo').textContent = PERIOD_LABELS[interval] || '';

  // Yeni veriyi yükle
  loadCharts();
}

/* ── AI Analysis ── */
async function runAnalysis() {
  const btn = document.getElementById('analyzeBtn');
  const result = document.getElementById('aiResult');
  btn.disabled = true;
  document.getElementById('btnText').textContent = '⏳ Analiz ediliyor...';
  result.innerHTML = '<div class="loader-dots"><span></span><span></span><span></span></div>';
  try {
    const res  = await fetch(`${API}/api/analyze`);
    const json = await res.json();
    if (json.error) throw new Error(json.error);
    result.innerHTML = `
      <div style="font-size:.65rem;color:#475569;margin-bottom:.5rem;">${json.date} tarihli analiz</div>
      <div class="ai-text-content">${json.analysis.replace(/\*\*/g,'').replace(/\*/g,'')}</div>
    `;
  } catch(e) {
    result.innerHTML = `<div style="color:${C.red};font-size:.8rem;">❌ ${e.message}</div>`;
  } finally {
    btn.disabled = false;
    document.getElementById('btnText').textContent = '⚡ Yenile';
  }
}

/* ── Ana Yükleme ── */
async function loadCharts() {
  try {
    document.getElementById('statusBadge').textContent = '⏳ Yükleniyor...';

    const res  = await fetch(`${API}/api/data?interval=${currentInterval}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    if (data.error) throw new Error(data.error);

    window._lastData = data;   // Chart type switch için sakla

    // Grafikleri çiz
    if (currentChartType === 'candlestick') buildCandlestickChart(data);
    else buildLineChart(data);
    buildMacdChart(data);
    buildRsiChart(data);
    buildStochChart(data);

    updateStats(data, null);

  } catch(err) {
    console.error(err);
    document.getElementById('statusBadge').textContent = '❌ Hata';
    document.getElementById('statusBadge').classList.add('badge-error');
  }
}

async function loadSignals() {
  try {
    const res  = await fetch(`${API}/api/signals`);
    const json = await res.json();
    buildSignalsTable(json.signals ?? []);
    // Sinyal sayısını stats bar'a yaz
    document.getElementById('valSignals').textContent = json.count ?? 0;
  } catch(err) {
    document.getElementById('signalsBody').innerHTML =
      `<tr><td colspan="8" class="loading-row" style="color:${C.red}">⚠️ Sinyal verisi yüklenemedi.</td></tr>`;
  }
}

/* ── Init ── */
document.addEventListener('DOMContentLoaded', () => {
  // Period butonlarına tıklama
  document.querySelectorAll('.period-btn').forEach(btn => {
    btn.addEventListener('click', () => switchPeriod(btn.dataset.interval));
  });

  // Paralel yükleme: grafikler + sinyal tablosu
  loadCharts();
  loadSignals();
});
