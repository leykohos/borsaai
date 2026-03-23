import os, subprocess, re

# 1. Restore the files completely using Git (wipes new CSS, removes bad scripts/colors)
subprocess.run(['git', 'checkout', 'HEAD', 'style.css', 'index.html', 'app.js'], check=True)

# 2. Extract Portfolio Code from setup file
with open('portfolio_setup.py', 'r', encoding='utf-8') as f:
    setup_code = f.read()

portfolio_html = re.search(r"portfolio_html = '''(.*?)'''", setup_code, re.DOTALL).group(1)
portfolio_js = re.search(r"portfolio_js = '''(.*?)'''", setup_code, re.DOTALL).group(1)

# 3. Patch index.html
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

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
html = html.replace('<div class="main-content">', '<div class="main-content" id="analysisView">')
html = html.replace('<!-- Scanner Modal (Overlay) -->', portfolio_html + '\n  <!-- Scanner Modal (Overlay) -->')

# Update AI Button Text for new capabilities
html = html.replace('⚡ AI Analizi Başlat', '⚡ Yapay Zeka Analizi')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

# 4. Patch style.css (Inject custom portfolio classes)
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

# 5. Patch app.js
with open('app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Replace Scanner Modal block safely using the exact old header and footer
js = re.sub(r'/\* ── Scanner Modal ── \*/.*?(?=\/\* ── Başlangıç ── \*/)', portfolio_js + '\n', js, flags=re.DOTALL)

# Apply indStats block
old_trades_summary = """  document.getElementById('tradesSummary').innerHTML = `
    <div class="sum-box">
      <div class="sum-val accent">${trades.length}</div>
      <div class="sum-lbl">Tamamlanan İşlem</div>
    </div>
    <div class="sum-box">
      <div class="sum-val" style="color:${avgRet >= 0 ? '+' : ''}${avgRet}%">Ortalama Kâr/Zarar</div>
      <div class="sum-lbl">Ortalama Kâr/Zarar</div>
    </div>
    <div class="sum-box">
      <div class="sum-val" style="color:${C.blue}">${winRate}%</div>
      <div class="sum-lbl">Başarı Oranı</div>
    </div>
  `;"""

new_trades_summary = """
  const indStats = {};
  trades.forEach(t => {
      const ind = t.entry_indicator;
      if (!indStats[ind]) indStats[ind] = { count: 0, wins: 0, profit: 0 };
      indStats[ind].count++;
      if (t.profit_pct > 0) indStats[ind].wins++;
      indStats[ind].profit += t.profit_pct;
  });

  let indHtml = '<div style="display:flex; gap:0.5rem; flex-wrap:wrap; margin-top:1rem; margin-bottom:1rem;">';
  for (const [ind, s] of Object.entries(indStats)) {
      const rate = ((s.wins / s.count) * 100).toFixed(0);
      const avgP = (s.profit / s.count).toFixed(2);
      const color = rate >= 50 ? C.green : C.red;
      indHtml += `
      <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.08); padding:0.8rem; border-radius:8px; flex:1; min-width:140px; text-align:center;">
          <div style="font-size:0.75rem; color:#94a3b8; margin-bottom:0.4rem;">${ind}</div>
          <div style="font-size:1.1rem; font-weight:600; color:${color};">${rate}% Başarı</div>
          <div style="font-size:0.8rem; color:${avgP>=0?C.green:C.red}; margin-top:0.3rem;">Ort. ${avgP>=0?'+':''}${avgP}%</div>
          <div style="font-size:0.7rem; color:#475569; margin-top:0.3rem;">(${s.count} İşlem)</div>
      </div>
      `;
  }
  indHtml += '</div>';

  document.getElementById('tradesSummary').innerHTML = `
    <div style="display:flex; gap:1rem; margin-bottom:1rem;">
      <div class="sum-box">
        <div class="sum-val accent">${trades.length}</div>
        <div class="sum-lbl">Tamamlanan İşlem</div>
      </div>
      <div class="sum-box">
        <div class="sum-val" style="color:${avgRet >= 0 ? '+' : ''}${avgRet}%">Ortalama Kâr/Zarar</div>
        <div class="sum-lbl">Ortalama Kâr/Zarar</div>
      </div>
      <div class="sum-box">
        <div class="sum-val" style="color:${C.blue}">${winRate}%</div>
        <div class="sum-lbl">Genel Başarı Oranı</div>
      </div>
    </div>
    <div style="font-size:0.9rem; color:#fff; font-weight:500;">İndikatör Bazlı Başarı Oranları</div>
    ${indHtml}
  `;
"""
if old_trades_summary in js:
    js = js.replace(old_trades_summary, new_trades_summary)

# Update Live price usage in JS header
js = js.replace('const price = Number(last.close).toFixed(2);', 'const price = Number(data.live_price || last.close).toFixed(2);')
js = js.replace('const prevClose = Number(prev.close);\n  document.getElementById(\'headerPrice\').textContent = `${price} ₺`;', 
"""const prevClose = Number(prev.close);
  if (data.live_price) {
    const livePct = ((data.live_price / prevClose) - 1) * 100;
    const color = livePct >= 0 ? C.green : C.red;
    document.getElementById('headerPrice').innerHTML = `${price} ₺ <span style="font-size:0.75rem; color:${color}">(${livePct >= 0 ? '+' : ''}${livePct.toFixed(2)}%)</span>`;
  } else {
    document.getElementById('headerPrice').textContent = `${price} ₺`;
  }""")

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(js)
