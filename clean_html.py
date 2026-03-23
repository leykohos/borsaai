with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

emojis = ['🔍', '📊', '💼', '📈', '🕯️', '🚥', '🚦', '🤖', '⚡', '🧠', '⭐️', '⭐', '🔄', '⏳', '⚠️', '❌', '🚀', '🔥']
for e in emojis:
    html = html.replace(e, '')
    html = html.replace(e + ' ', '')

html = html.replace('AI Analizi Başlat', 'Yapay Zeka Analizi')
html = html.replace(' Portföy & BIST30 Tarama', 'İşlemler')
html = html.replace('Analiz & Yapay Zeka', 'Piyasalar')
html = html.replace('Portföy & İşlemler', 'İşlemler')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
