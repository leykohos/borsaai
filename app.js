let currentSymbol = 'AKBNK.IS';
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

  const price = data.live_price || last(data.close);
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

function renderTradeResult(s) {
  if (s.type !== 'Buy') return '<span style="color:#475569">—</span>';
  const res = s.trade_result;
  if (!res) return '<span style="color:#475569">—</span>';
  
  if (res.status === 'OPEN') {
    return `<span class="badge badge-live" style="background:rgba(34,197,94,0.1); color:${C.green}; border:1px solid ${C.green}; font-size:0.65rem;">AÇIK</span>`;
  }
  
  const color = res.profit_pct >= 0 ? C.green : C.red;
  return `<div style="line-height:1.2;">
    <div style="color:${color}; font-weight:700;">${res.profit_pct >= 0 ? '+' : ''}${res.profit_pct}%</div>
    <div style="font-size:0.65rem; color:#64748b;">Kapandı: ${res.exit_date.split(' ')[0]}</div>
  </div>`;
}

function buildSignalsTable(signals) {
  const tbody = document.getElementById('signalsBody');
  if (!signals || signals.length === 0) {
    tbody.innerHTML = '<tr><td colspan="13" class="loading-row">Sinyal bulunamadı.</td></tr>';
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
      <td>${s.type === "Buy" ? '<span class="badge" style="background:rgba(34,197,94,0.1); color:#22c55e; border:1px solid #22c55e; padding:2px 6px; border-radius:4px; font-weight:700;">AL</span>' : '<span class="badge" style="background:rgba(244,63,94,0.1); color:#f43f5e; border:1px solid #f43f5e; padding:2px 6px; border-radius:4px; font-weight:700;">SAT</span>'}</td>
      <td><strong>${s.price} ₺</strong></td>
      <td style="color:${colorRsi(s.rsi)}">${s.rsi}</td>
      <td style="color:${(s.macd_h || 0) >= 0 ? C.green : C.red}">${s.macd_h || '0'}</td>
      <td style="color:${(s.stoch_k || 0) < 20 ? C.red : (s.stoch_k || 0) > 80 ? C.orange : C.green}">${s.stoch_k || '0'}</td>
      <td style="color:${s.trend === 'BOĞA' ? C.green : C.red}; font-weight:700;">${s.trend || '—'}</td>
      ${[s.ret_1w, s.ret_2w, s.ret_1m, s.ret_3m].map(r => `<td>${colorRet(r)}</td>`).join('')}
      <td>${renderTradeResult(s)}</td>
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
  document.getElementById('btnText').textContent = ' Analiz ediliyor...';
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
    result.innerHTML = `<div style="color:${C.red};font-size:.8rem;"> ${e.message}</div>`;
  } finally {
    btn.disabled = false;
    document.getElementById('btnText').textContent = ' Yenile';
  }
}

/* ── Ana Yükleme ── */
async function loadCharts() {
  try {
    document.getElementById('statusBadge').textContent = ' Yükleniyor...';

    const res  = await fetch(`${API}/api/data?symbol=${currentSymbol}&interval=${currentInterval}`);
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
    document.getElementById('statusBadge').textContent = ' Hata';
    document.getElementById('statusBadge').classList.add('badge-error');
  }
}


function buildOpenPositionsTable(positions) {
  const section = document.getElementById('openPositionsSection');
  const tbody = document.getElementById('openPositionsBody');
  
  if (!positions || positions.length === 0) {
    if (section) section.style.display = 'none';
    return;
  }

  if (section) section.style.display = 'block';
  
  tbody.innerHTML = positions.map(p => `
    <tr>
      <td><span class="reason-tag">${p.indicator}</span></td>
      <td>${p.buy_date}</td>
      <td><strong>${p.buy_price} ₺</strong></td>
      <td><strong>${p.current_price} ₺</strong></td>
      <td>${colorRet(p.profit_pct)}</td>
    </tr>
  `).join('');
}

async function loadSignals() {
  try {
    const res  = await fetch(`${API}/api/signals?symbol=${currentSymbol}`);
    const json = await res.json();
    buildSignalsTable(json.signals ?? []);
    buildOpenPositionsTable(json.open_positions ?? []);
    // Sinyal sayısını stats bar'a yaz
    document.getElementById('valSignals').textContent = json.count ?? (json.signals ? json.signals.length : 0);
  } catch(err) {
    document.getElementById('signalsBody').innerHTML =
      `<tr><td colspan="13" class="loading-row" style="color:${C.red}"> Sinyal verisi yüklenemedi.</td></tr>`;
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
  loadGlobalOpportunities();
});

/* ── Main View Switcher ── */
function switchMainView(viewType) {
  document.getElementById('navAnalysisBtn').classList.toggle('active', viewType === 'analysis');
  document.getElementById('navPortfolioBtn').classList.toggle('active', viewType === 'portfolio');
  
  document.getElementById('analysisView').style.display = viewType === 'analysis' ? 'block' : 'none';
  document.getElementById('portfolioView').style.display = viewType === 'portfolio' ? 'block' : 'none';
  
  if (viewType === 'portfolio') {
    loadPortfolio();
  }
}

/* ── Portfolio & Scanner Tracker ── */
function switchPortfolioTab(viewId, btnId) {
  document.getElementById('tabMyPortfolio').classList.remove('active');
  document.getElementById('tabAllOpportunities').classList.remove('active');
  document.getElementById('myPortfolioView').style.display = 'none';
  document.getElementById('allOpportunitiesView').style.display = 'none';
  
  document.getElementById(btnId).classList.add('active');
  document.getElementById(viewId).style.display = 'block';
}

function getStarredTrades() {
  return JSON.parse(localStorage.getItem('borsaai_portfolio') || '[]');
}

function toggleStar(tradeId) {
  let starred = getStarredTrades();
  if (starred.includes(tradeId)) {
    starred = starred.filter(id => id !== tradeId);
  } else {
    starred.push(tradeId);
  }
  localStorage.setItem('borsaai_portfolio', JSON.stringify(starred));
  // Re-render
  if (window._lastPortfolioData) {
    renderPortfolio(window._lastPortfolioData);
  }
}

function loadPortfolio() {
  document.getElementById('portCount').textContent = '...';
  document.getElementById('portTotalProfit').textContent = '...';
  document.getElementById('myPortfolioBody').innerHTML = '<tr><td colspan="7" class="loading-row"> İşlemler yükleniyor...</td></tr>';
  document.getElementById('allOppsBody').innerHTML = "<tr><td colspan='8' class='loading-row'> Tüm açık sinyaller BIST30'dan taranıyor (1-3 saniye sürebilir)...</td></tr>";
  
  fetch(`${API}/api/scanner`)
    .then(r => r.json())
    .then(data => {
      if (data.error) throw new Error(data.error);
      window._lastPortfolioData = data.opportunities || [];
      renderPortfolio(window._lastPortfolioData);
    })
    .catch(err => {
      document.getElementById('myPortfolioBody').innerHTML = `<tr><td colspan="7" class="loading-row" style="color:#f43f5e"> Hata: ${err.message}</td></tr>`;
      document.getElementById('allOppsBody').innerHTML = `<tr><td colspan="13" class="loading-row" style="color:#f43f5e"> Hata: ${err.message}</td></tr>`;
    });
}

function renderPortfolio(opps) {
  const starred = getStarredTrades();
  const myPortfolio = [];
  const allOppsHtml = [];
  
  opps.forEach(o => {
    const tradeId = `${o.symbol}_${o.indicator}_${o.buy_date}`;
    const isStarred = starred.includes(tradeId);
    
    if (isStarred) {
      myPortfolio.push(o);
    }
    
    const starBtnUrl = `<button class="star-btn ${isStarred ? 'active' : ''}" onclick="toggleStar('${tradeId}')">★</button>`;
    
    allOppsHtml.push(`
      <tr>
        <td style="text-align:center;">${starBtnUrl}</td>
        <td><strong>${o.symbol}</strong></td>
        <td><span class="reason-tag">${o.indicator}</span></td>
        <td>${o.buy_date}</td>
        <td>${o.buy_price} ₺</td>
        <td>${o.reason}</td>
        <td><strong>${o.current_price} ₺</strong></td>
        <td>${colorRet(o.profit_pct)}</td>
      </tr>
    `);
  });

  // Render My Portfolio
  let myPortHtml = '';
  let totalProfit = 0;
  
  if (myPortfolio.length === 0) {
    myPortHtml = '<tr><td colspan="7" class="loading-row">Henüz yıldızlanmış (favori) işleminiz yok.<br><br>Tüm Açık Sinyaller sekmesinden fırsatları  ile işaretleyin.</td></tr>';
  } else {
    myPortHtml = myPortfolio.map(o => {
      const tradeId = `${o.symbol}_${o.indicator}_${o.buy_date}`;
      totalProfit += o.profit_pct;
      const starBtnUrl = `<button class="star-btn active" onclick="toggleStar('${tradeId}')">★</button>`;
      return `
        <tr>
          <td style="text-align:center;">${starBtnUrl}</td>
          <td><strong>${o.symbol}</strong></td>
          <td><span class="reason-tag">${o.indicator}</span></td>
          <td>${o.buy_date}</td>
          <td>${o.buy_price} ₺</td>
          <td><strong>${o.current_price} ₺</strong></td>
          <td>${colorRet(o.profit_pct)}</td>
        </tr>
      `;
    }).join('');
  }
  
  document.getElementById('myPortfolioBody').innerHTML = myPortHtml;
  
  if (allOppsHtml.length === 0) {
    document.getElementById('allOppsBody').innerHTML = '<tr><td colspan="13" class="loading-row">Şu an piyasada bekleyen açık sinyal yok.</td></tr>';
  } else {
    document.getElementById('allOppsBody').innerHTML = allOppsHtml.join('');
  }
  
  // Dashboard Metrics
  document.getElementById('portCount').textContent = myPortfolio.length;
  
  if (myPortfolio.length > 0) {
    const avgProfit = (totalProfit / myPortfolio.length).toFixed(2);
    const color = avgProfit >= 0 ? '#22c55e' : '#f43f5e';
    const sign = avgProfit >= 0 ? '+' : '';
    document.getElementById('portTotalProfit').innerHTML = `<span style="color:${color}">${sign}${avgProfit}%</span>`;
  } else {
    document.getElementById('portTotalProfit').textContent = '%0.00';
  }
}

/* ── Main View Switcher ── */
function switchMainView(viewType) {
  document.getElementById('navAnalysisBtn').classList.toggle('active', viewType === 'analysis');
  document.getElementById('navPortfolioBtn').classList.toggle('active', viewType === 'portfolio');
  
  document.getElementById('analysisView').style.display = viewType === 'analysis' ? 'block' : 'none';
  document.getElementById('portfolioView').style.display = viewType === 'portfolio' ? 'block' : 'none';
  
  if (viewType === 'portfolio') {
    loadPortfolio();
  }
}

/* ── Portfolio & Scanner Tracker ── */
function switchPortfolioTab(viewId, btnId) {
  document.getElementById('tabMyPortfolio').classList.remove('active');
  document.getElementById('tabAllOpportunities').classList.remove('active');
  document.getElementById('myPortfolioView').style.display = 'none';
  document.getElementById('allOpportunitiesView').style.display = 'none';
  
  document.getElementById(btnId).classList.add('active');
  document.getElementById(viewId).style.display = 'block';
}

function getStarredTrades() {
  return JSON.parse(localStorage.getItem('borsaai_portfolio') || '[]');
}

function toggleStar(tradeId) {
  let starred = getStarredTrades();
  if (starred.includes(tradeId)) {
    starred = starred.filter(id => id !== tradeId);
  } else {
    starred.push(tradeId);
  }
  localStorage.setItem('borsaai_portfolio', JSON.stringify(starred));
  // Re-render
  if (window._lastPortfolioData) {
    renderPortfolio(window._lastPortfolioData);
  }
}

function loadPortfolio() {
  document.getElementById('portCount').textContent = '...';
  document.getElementById('portTotalProfit').textContent = '...';
  document.getElementById('myPortfolioBody').innerHTML = '<tr><td colspan="7" class="loading-row">⏳ İşlemler yükleniyor...</td></tr>';
  document.getElementById('allOppsBody').innerHTML = '<tr><td colspan="13" class="loading-row">⏳ Tüm açık sinyaller BIST30\'dan taranıyor (1-3 saniye sürebilir)...</td></tr>';
  
  fetch(`${API}/api/scanner`)
    .then(r => r.json())
    .then(data => {
      if (data.error) throw new Error(data.error);
      window._lastPortfolioData = data.opportunities || [];
      renderPortfolio(window._lastPortfolioData);
    })
    .catch(err => {
      document.getElementById('myPortfolioBody').innerHTML = `<tr><td colspan="7" class="loading-row" style="color:#f43f5e">⚠️ Hata: ${err.message}</td></tr>`;
      document.getElementById('allOppsBody').innerHTML = `<tr><td colspan="13" class="loading-row" style="color:#f43f5e">⚠️ Hata: ${err.message}</td></tr>`;
    });
}

function renderPortfolio(opps) {
  const starred = getStarredTrades();
  const myPortfolio = [];
  const allOppsHtml = [];
  
  opps.forEach(o => {
    const tradeId = `${o.symbol}_${o.indicator}_${o.buy_date}`;
    const isStarred = starred.includes(tradeId);
    
    if (isStarred) {
      myPortfolio.push(o);
    }
    
    const starBtnUrl = `<button class="star-btn ${isStarred ? 'active' : ''}" onclick="toggleStar('${tradeId}')">★</button>`;
    
    allOppsHtml.push(`
      <tr>
        <td style="text-align:center;">${starBtnUrl}</td>
        <td><strong>${o.symbol}</strong></td>
        <td><span class="reason-tag">${o.indicator}</span></td>
        <td>${o.buy_date}</td>
        <td>${o.buy_price} ₺</td>
        <td>${o.reason}</td>
        <td><strong>${o.current_price} ₺</strong></td>
        <td>${colorRet(o.profit_pct)}</td>
      </tr>
    `);
  });

  // Render My Portfolio
  let myPortHtml = '';
  let totalProfit = 0;
  
  if (myPortfolio.length === 0) {
    myPortHtml = '<tr><td colspan="7" class="loading-row">Henüz yıldızlanmış (favori) işleminiz yok.<br><br>Tüm Açık Sinyaller sekmesinden fırsatları ⭐ ile işaretleyin.</td></tr>';
  } else {
    myPortHtml = myPortfolio.map(o => {
      const tradeId = `${o.symbol}_${o.indicator}_${o.buy_date}`;
      totalProfit += o.profit_pct;
      const starBtnUrl = `<button class="star-btn active" onclick="toggleStar('${tradeId}')">★</button>`;
      return `
        <tr>
          <td style="text-align:center;">${starBtnUrl}</td>
          <td><strong>${o.symbol}</strong></td>
          <td><span class="reason-tag">${o.indicator}</span></td>
          <td>${o.buy_date}</td>
          <td>${o.buy_price} ₺</td>
          <td><strong>${o.current_price} ₺</strong></td>
          <td>${colorRet(o.profit_pct)}</td>
        </tr>
      `;
    }).join('');
  }
  
  document.getElementById('myPortfolioBody').innerHTML = myPortHtml;
  
  if (allOppsHtml.length === 0) {
    document.getElementById('allOppsBody').innerHTML = '<tr><td colspan="13" class="loading-row">Şu an piyasada bekleyen açık sinyal yok.</td></tr>';
  } else {
    document.getElementById('allOppsBody').innerHTML = allOppsHtml.join('');
  }
  
  // Dashboard Metrics
  document.getElementById('portCount').textContent = myPortfolio.length;
  
  if (myPortfolio.length > 0) {
    const avgProfit = (totalProfit / myPortfolio.length).toFixed(2);
    const color = avgProfit >= 0 ? '#22c55e' : '#f43f5e';
    const sign = avgProfit >= 0 ? '+' : '';
    document.getElementById('portTotalProfit').innerHTML = `<span style="color:${color}">${sign}${avgProfit}%</span>`;
  } else {
    document.getElementById('portTotalProfit').textContent = '%0.00';
  }
}


/*  UI Event Handlers  */
function setChartType(type) {
  currentChartType = type;
  const btnLine = document.getElementById('btnLine');
  const btnCandle = document.getElementById('btnCandle');
  if (btnLine) btnLine.classList.toggle('active', type === 'line');
  if (btnCandle) btnCandle.classList.toggle('active', type === 'candlestick');
  if (window._lastData) {
    if (type === 'candlestick') buildCandlestickChart(window._lastData);
    else buildLineChart(window._lastData);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const sel = document.getElementById('symbolSelect');
  if (sel) {
    sel.addEventListener('change', (e) => {
      currentSymbol = e.target.value;
      loadCharts();
      loadSignals();
  loadGlobalOpportunities();
    });
  }
});

async function loadGlobalOpportunities() {
  const container = document.getElementById('globalOppsList');
  try {
    const res = await fetch(`${API}/api/scanner`);
    const data = await res.json();
    if (data.error) throw new Error(data.error);
    renderGlobalOpportunities(data.opportunities || []);
  } catch (e) {
    if (container) container.innerHTML = `<div style="color:${C.red}; font-size:0.75rem; padding:1rem;">⚠️ Hata: ${e.message}</div>`;
  }
}

function renderGlobalOpportunities(opps) {
  const container = document.getElementById('globalOppsList');
  if (!container) return;
  
  if (opps.length === 0) {
    container.innerHTML = '<div style="color:#64748b; font-size:0.75rem; padding:1rem;">Şu an aktif sinyal yok.</div>';
    return;
  }

  container.innerHTML = opps.map(o => `
    <div style="display:flex; justify-content:space-between; align-items:center; padding:0.6rem; border-bottom:1px solid rgba(255,255,255,0.05); cursor:pointer;" onclick="selectSymbolFromWidget('${o.symbol}')">
      <div>
        <div style="font-weight:700; color:#fff; font-size:0.85rem;">${o.symbol}</div>
        <div style="font-size:0.65rem; color:#94a3b8;">${o.indicator} · ${o.buy_date.split(' ')[0]}</div>
      </div>
      <div style="text-align:right;">
        <div style="color:${o.profit_pct >= 0 ? C.green : C.red}; font-weight:700; font-size:0.85rem;">${o.profit_pct >= 0 ? '+' : ''}${o.profit_pct}%</div>
        <div style="font-size:0.65rem; color:#64748b;">${o.buy_price} ₺ → ${o.current_price} ₺</div>
      </div>
    </div>
  `).join('');
}

function selectSymbolFromWidget(sym) {
  const select = document.getElementById('symbolSelect');
  if (select) {
    select.value = sym;
    const event = new Event('change');
    select.dispatchEvent(event);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
}
