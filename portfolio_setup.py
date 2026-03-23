import os

# 1. Update style.css
with open('style.css', 'r', encoding='utf-8') as f:
    css = f.read()

if '.nav-btn' not in css:
    css += """
/* Portfolio & Nav Styles */
.nav-btn {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(99,156,255,0.1);
  color: #94a3b8;
  padding: 0.8rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  text-align: left;
  font-weight: 500;
  transition: all 0.2s;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.nav-btn:hover {
  background: rgba(0,212,255,0.05);
  color: #fff;
}
.nav-btn.active {
  background: rgba(0,212,255,0.1);
  border-color: rgba(0,212,255,0.3);
  color: #00d4ff;
  box-shadow: 0 0 15px rgba(0,212,255,0.1);
}

.star-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #475569;
  transition: all 0.2s;
}
.star-btn:hover {
  transform: scale(1.2);
}
.star-btn.active {
  color: #f59e0b;
  text-shadow: 0 0 10px rgba(245, 158, 11, 0.5);
}

.portfolio-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}
"""
    with open('style.css', 'w', encoding='utf-8') as f:
        f.write(css)


# 2. Update index.html
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace sidebar button
old_sidebar_btn = '''<!-- Right Header Actions (previously in header) -->
    <button class="action-btn" onclick="openScanner()">
      🔍 BIST30 Tarama
    </button>'''

new_nav = '''
    <nav class="side-nav" style="margin-bottom:1.5rem; display:flex; flex-direction:column; gap:0.5rem;">
      <button class="nav-btn active" id="navAnalysisBtn" onclick="switchMainView('analysis')">📊 Analiz & Yapay Zeka</button>
      <button class="nav-btn" id="navPortfolioBtn" onclick="switchMainView('portfolio')">💼 Portföy & İşlemler</button>
    </nav>
'''
html = html.replace(old_sidebar_btn, new_nav)

# Add id to main-content
html = html.replace('<div class="main-content">', '<div class="main-content" id="analysisView">')

# Add portfolioView right after analysisView ends (before Scanner Modal)
portfolio_html = '''
  <!-- PORTFOLIO VIEW -->
  <div class="main-content" id="portfolioView" style="display:none; overflow-y:auto; max-height:100vh;">
    <!-- Top Header -->
    <header class="top-header">
      <div class="header-left">
        <h1 class="stock-title" style="font-size:1.8rem; margin:0;">💼 Portföy & BIST30 Tarama</h1>
        <div class="stock-sub">Gerçek hayatta işleme girdiğiniz fırsatları yıldızlayın (⭐) ve kâr/zararınızı takip edin.</div>
      </div>
      <div>
        <button class="action-btn" onclick="loadPortfolio()">🔄 Yenile</button>
      </div>
    </header>

    <div class="portfolio-cards">
      <div class="signals-card">
        <div class="signals-sub">Yıldızlanmış Açık İşlem</div>
        <div class="signals-title" id="portCount" style="font-size:2rem; margin-top:0.5rem; color:#fff;">0</div>
      </div>
      <div class="signals-card">
        <div class="signals-sub">Toplam Portföy Kâr/Zarar Ortalaması</div>
        <div class="signals-title" id="portTotalProfit" style="font-size:2rem; margin-top:0.5rem;">%0.00</div>
      </div>
    </div>

    <!-- Portfolio Tabs -->
    <div class="signals-card" style="margin-bottom:2rem;">
      <div class="signal-tabs" style="margin-bottom:1rem;">
        <button class="signal-tab active" id="tabMyPortfolio" onclick="switchPortfolioTab('myPortfolioView', 'tabMyPortfolio')">⭐️ İşleme Girilenler (Favoriler)</button>
        <button class="signal-tab" id="tabAllOpportunities" onclick="switchPortfolioTab('allOpportunitiesView', 'tabAllOpportunities')">🔍 Tüm Açık Sinyaller (Tarama)</button>
      </div>
      
      <div id="myPortfolioView" class="tab-content active">
        <div class="table-wrap">
          <table class="signals-table">
            <thead>
              <tr>
                <th style="width:40px;">İşlem</th>
                <th>Sembol</th>
                <th>İndikatör</th>
                <th>Giriş Tarihi</th>
                <th>Giriş Fiyatı</th>
                <th>Güncel Fiyat</th>
                <th>Anlık Kâr/Zarar</th>
              </tr>
            </thead>
            <tbody id="myPortfolioBody">
              <tr><td colspan="7" class="loading-row">Henüz yıldızlanmış (favori) işleminiz yok.</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <div id="allOpportunitiesView" class="tab-content" style="display:none;">
        <div class="table-wrap">
          <table class="signals-table">
            <thead>
              <tr>
                <th style="width:40px;">İşlem</th>
                <th>Sembol</th>
                <th>İndikatör</th>
                <th>Giriş Tarihi</th>
                <th>Giriş Fiyatı</th>
                <th>Neden</th>
                <th>Güncel Fiyat</th>
                <th>Anlık Kâr/Zarar</th>
              </tr>
            </thead>
            <tbody id="allOppsBody">
              <tr><td colspan="8" class="loading-row">Açık fırsatlar yükleniyor...</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
'''

# The scanner modal logic is at the bottom, so insert portfolioView right before scannerModal
html = html.replace('<!-- Scanner Modal (Overlay) -->', portfolio_html + '\n  <!-- Scanner Modal (Overlay) -->')

# Hide scannerModal completely by default removing openScanner button logic
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)


# 3. Update app.js
with open('app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Add portfolio logic at the end, replacing the old scanner modal functions
portfolio_js = '''
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
  document.getElementById('allOppsBody').innerHTML = '<tr><td colspan="8" class="loading-row">⏳ Tüm açık sinyaller BIST30\\'dan taranıyor (1-3 saniye sürebilir)...</td></tr>';
  
  fetch(`${API}/api/scanner`)
    .then(r => r.json())
    .then(data => {
      if (data.error) throw new Error(data.error);
      window._lastPortfolioData = data.opportunities || [];
      renderPortfolio(window._lastPortfolioData);
    })
    .catch(err => {
      document.getElementById('myPortfolioBody').innerHTML = `<tr><td colspan="7" class="loading-row" style="color:#f43f5e">⚠️ Hata: ${err.message}</td></tr>`;
      document.getElementById('allOppsBody').innerHTML = `<tr><td colspan="8" class="loading-row" style="color:#f43f5e">⚠️ Hata: ${err.message}</td></tr>`;
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
    document.getElementById('allOppsBody').innerHTML = '<tr><td colspan="8" class="loading-row">Şu an piyasada bekleyen açık sinyal yok.</td></tr>';
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
'''

# We will just append this to app.js, and hopefully remove the `openScanner` and `closeScanner` old functions.
import re
js = re.sub(r'/\* ── Scanner Modal ── \*/.*', '', js, flags=re.DOTALL)
js += portfolio_js

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(js)
