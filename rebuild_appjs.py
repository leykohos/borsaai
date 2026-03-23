import re

with open('portfolio_setup.py', 'r', encoding='utf-8') as f:
    setup_code = f.read()

pjs_match = re.search(r"portfolio_js = '''(.*?)'''", setup_code, re.DOTALL)
if pjs_match:
    portfolio_js = pjs_match.group(1)
else:
    portfolio_js = ""

with open('app.js', 'r', encoding='utf-8') as f:
    js = f.read()

if portfolio_js:
    js = re.sub(r'/\* ── Scanner Modal ── \*/.*', '', js, flags=re.DOTALL)
    js += portfolio_js

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
js = js.replace(old_trades_summary, new_trades_summary)

js = js.replace("bg: '#060b14'", "bg: '#0b0e11'")
js = js.replace("card: 'rgba(13, 22, 39, 0.8)'", "card: '#181a20'")
# Catch possible different spacng
js = re.sub(r"card:\s*'rgba\(13,\s*22,\s*39,\s*0\.8\)'", "card: '#181a20'", js)
js = re.sub(r"border:\s*'rgba\(99,\s*156,\s*255,\s*0\.12\)'", "border: '#2b3139'", js)
js = js.replace("text: '#e2e8f0'", "text: '#eaecef'")
js = js.replace("textMuted: '#64748b'", "textMuted: '#848e9c'")
js = js.replace("blue: '#00d4ff'", "blue: '#fcd535'")
js = js.replace("purple: '#a855f7'", "purple: '#fcd535'")
js = js.replace("green: '#22c55e'", "green: '#0ecb81'")
js = js.replace("red: '#f43f5e'", "red: '#f6465d'")
js = js.replace("orange: '#f59e0b'", "orange: '#f0c72c'")

emojis_to_strip = ['🔍', '📊', '💼', '📈', '🕯️', '🚥', '🚦', '🤖', '⚡', '🧠', '⭐️', '⭐', '🔄', '⏳', '⚠️', '❌', '🚀', '🔥']
for e in emojis_to_strip:
    js = js.replace(e, '')

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(js)
