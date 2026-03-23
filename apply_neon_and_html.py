import os, subprocess, re

with open('app.js', 'r', encoding='utf-8') as f:
    js = f.read()

js = js.replace("bg: '#0b0e11'", "bg: '#060b14'")
js = js.replace("card: '#181a20'", "card: 'rgba(13,22,39,0.8)'")
js = js.replace("border: '#2b3139'", "border: 'rgba(99,156,255,0.12)'")
js = js.replace("text: '#eaecef'", "text: '#e2e8f0'")
js = js.replace("textMuted: '#848e9c'", "textMuted: '#64748b'")
js = js.replace("blue: '#fcd535'", "blue: '#00d4ff'")
js = js.replace("purple: '#fcd535'", "purple: '#a855f7'")
js = js.replace("green: '#0ecb81'", "green: '#22c55e'")
js = js.replace("red: '#f6465d'", "red: '#f43f5e'")
js = js.replace("orange: '#f0c72c'", "orange: '#f59e0b'")

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(js)

subprocess.run(['git', 'checkout', 'HEAD', 'index.html'], check=True)

with open('portfolio_setup.py', 'r', encoding='utf-8') as f:
    setup_code = f.read()

portfolio_html = re.search(r"portfolio_html = '''(.*?)'''", setup_code, re.DOTALL).group(1)

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
html = html.replace('⚡ AI Analizi Başlat', '⚡ Yapay Zeka Analizi')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("SUCCESS!")
