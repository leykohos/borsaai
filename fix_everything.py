import codecs, subprocess, re

# 1. Bring index.html exactly back from git
subprocess.run(['git', 'checkout', 'HEAD', 'index.html'], check=True)

with codecs.open('index.html', 'r', 'utf-8') as f:
    html = f.read()

# 2. Add Dropdown and Navigation
header_info_old = '''<div class="badge badge-symbol">ALBRK.IS</div>'''
header_info_new = '''
        <nav style="display:flex; gap:0.5rem; margin-right:1rem;">
          <button class="nav-btn active" id="navAnalysisBtn" onclick="switchMainView('analysis')">📊 Piyasalar</button>
          <button class="nav-btn" id="navPortfolioBtn" onclick="switchMainView('portfolio')">💼 İşlemler</button>
        </nav>
        <select class="symbol-select" id="symbolSelect" style="background:rgba(99,156,255,0.1); color:#00d4ff; border:1px solid rgba(0,212,255,0.3); padding:0.4rem 0.8rem; border-radius:6px; outline:none; font-weight:600;">
          <option value="AKBNK.IS" selected>AKBNK.IS</option>
          <option value="ALBRK.IS">ALBRK.IS</option>
          <option value="ARCLK.IS">ARCLK.IS</option>
          <option value="ASELS.IS">ASELS.IS</option>
          <option value="ASTOR.IS">ASTOR.IS</option>
          <option value="BIMAS.IS">BIMAS.IS</option>
          <option value="BRSAN.IS">BRSAN.IS</option>
          <option value="CINFO.IS">CINFO.IS</option>
          <option value="CWENE.IS">CWENE.IS</option>
          <option value="EUPWR.IS">EUPWR.IS</option>
          <option value="ENJSA.IS">ENJSA.IS</option>
          <option value="ENKAI.IS">ENKAI.IS</option>
          <option value="EREGL.IS">EREGL.IS</option>
          <option value="FROTO.IS">FROTO.IS</option>
          <option value="GARAN.IS">GARAN.IS</option>
          <option value="HEKTS.IS">HEKTS.IS</option>
          <option value="ISCTR.IS">ISCTR.IS</option>
          <option value="KCHOL.IS">KCHOL.IS</option>
          <option value="KONTR.IS">KONTR.IS</option>
          <option value="KOZAL.IS">KOZAL.IS</option>
          <option value="KRDMD.IS">KRDMD.IS</option>
          <option value="MGROS.IS">MGROS.IS</option>
          <option value="ODAS.IS">ODAS.IS</option>
          <option value="OYAKC.IS">OYAKC.IS</option>
          <option value="PETKM.IS">PETKM.IS</option>
          <option value="PGSUS.IS">PGSUS.IS</option>
          <option value="SAHOL.IS">SAHOL.IS</option>
          <option value="SISE.IS">SISE.IS</option>
          <option value="TCELL.IS">TCELL.IS</option>
          <option value="THYAO.IS">THYAO.IS</option>
          <option value="TOASO.IS">TOASO.IS</option>
          <option value="TUPRS.IS">TUPRS.IS</option>
          <option value="YKBNK.IS">YKBNK.IS</option>
        </select>
'''
html = html.replace(header_info_old, header_info_new)

# 3. Add Top-Level Portfolio View
with codecs.open('portfolio_setup.py', 'r', 'utf-8') as f:
    setup_code = f.read()

portfolio_html = re.search(r"portfolio_html = '''(.*?)'''", setup_code, re.DOTALL).group(1)

html = html.replace('<main class="main-grid">', '<div id="analysisView">\n  <main class="main-grid">')
html = html.replace('</main>', '</main>\n</div>\n<div id="portfolioView" style="display:none; padding:1.5rem; max-width:1400px; margin:0 auto;">\n' + portfolio_html + '\n</div>')

with codecs.open('index.html', 'w', 'utf-8') as f:
    f.write(html)

# 4. Patch app.js Fetch Queries
with codecs.open('app.js', 'r', 'utf-8') as f:
    js = f.read()

js = js.replace('`${API}/api/data?interval=${currentInterval}`', '`${API}/api/data?symbol=${currentSymbol}&interval=${currentInterval}`')
js = js.replace('`${API}/api/signals`', '`${API}/api/signals?symbol=${currentSymbol}`')

# Ensure let currentSymbol exists properly
if "let currentSymbol = 'AKBNK.IS';" not in js and "let currentSymbol =" not in js:
    js = "let currentSymbol = 'AKBNK.IS';\n" + js

with codecs.open('app.js', 'w', 'utf-8') as f:
    f.write(js)

print("SUCCESS")
