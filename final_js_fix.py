import codecs, re

with codecs.open('app.js', 'r', 'utf-8') as f:
    js = f.read()

with codecs.open('portfolio_setup.py', 'r', 'utf-8') as f:
    setup_code = f.read()

portfolio_js = re.search(r"portfolio_js = '''(.*?)'''", setup_code, re.DOTALL).group(1)

# 1. Inject portfolio logic
if "switchMainView" not in js:
    if "/* ── Scanner Modal ── */" in js:
        js = re.sub(r'/\* ── Scanner Modal ── \*/.*?(?=\/\* ── Başlangıç ── \*/)', portfolio_js + '\n', js, flags=re.DOTALL)
    else:
        js += "\n\n" + portfolio_js

# 2. Inject indicator stats logic
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
      const ind = t.entry_indicator || "Bilinmeyen";
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
else:
    print("WARNING: Exact match failed. Using RegExp.")
    js = re.sub(r"document\.getElementById\('tradesSummary'\)\.innerHTML = `.*?`;", new_trades_summary, js, flags=re.DOTALL)

with codecs.open('app.js', 'w', 'utf-8') as f:
    f.write(js)

print("JS Patch Applied")
