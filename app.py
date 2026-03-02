from flask import Flask, render_template, request, jsonify, send_file
import random
import json, os
import io
from datetime import datetime

app = Flask(__name__)

# Databáze různých webových stránek pro různé dotazy
WEB_STRANKY = {
    # Technologie
    'python': [
        {'title': 'Python.org - Oficiální stránka', 'url': 'https://www.python.org', 'popis': 'Oficiální stránky programovacího jazyka Python. Stáhněte si Python, dokumentace, tutoriály.'},
        {'title': 'Python na Wikipedii', 'url': 'https://cs.wikipedia.org/wiki/Python', 'popis': 'Článek o Pythonu na otevřené encyklopedii. Historie, vlastnosti, použití.'},
        {'title': 'W3Schools Python tutoriál', 'url': 'https://www.w3schools.com/python/', 'popis': 'Naučte se Python online. Interaktivní příklady, cvičení a kvízy.'},
        {'title': 'Real Python', 'url': 'https://realpython.com', 'popis': 'Python tutoriály, články a kurzy pro začátečníky i pokročilé.'},
        {'title': 'Python pro začátečníky', 'url': 'https://python.cz', 'popis': 'Česká Python komunita. Návody, akce, materiály pro začátečníky.'},
    ],
    'javascript': [
        {'title': 'MDN Web Docs - JavaScript', 'url': 'https://developer.mozilla.org/cs/docs/Web/JavaScript', 'popis': 'Dokumentace JavaScriptu od Mozilly. Referenční příručka a tutoriály.'},
        {'title': 'W3Schools JavaScript', 'url': 'https://www.w3schools.com/js/', 'popis': 'Výukový kurz JavaScriptu pro začátečníky.'},
        {'title': 'JavaScript.info', 'url': 'https://javascript.info', 'popis': 'Moderní JavaScript tutoriál od základů po pokročilé.'},
    ],
    # Jídlo
    'pizza': [
        {'title': 'Pizza - Wikipedie', 'url': 'https://cs.wikipedia.org/wiki/Pizza', 'popis': 'Článek o pizze - historie, druhy, zajímavosti.'},
        {'title': 'Recept na pizzu', 'url': 'https://www.toprecepty.cz/recept/3222-pizza-margherita/', 'popis': 'Domácí pizza Margherita - jednoduchý recept.'},
        {'title': 'Pizza v Praze', 'url': 'https://www.pizzapraha.cz', 'popis': 'Nejlepší pizzerie v Praze. Rozvoz pizzy.'},
    ],
    # Cestování
    'pariz': [
        {'title': 'Paříž - Wikipedie', 'url': 'https://cs.wikipedia.org/wiki/Paříž', 'popis': 'Hlavní město Francie - historie, památky, kultura.'},
        {'title': 'Eiffelova věž', 'url': 'https://www.toureiffel.paris', 'popis': 'Oficiální stránky Eiffelovy věže. Vstupenky, otevírací doba.'},
        {'title': 'Louvre Museum', 'url': 'https://www.louvre.fr', 'popis': 'Oficiální stránky muzea Louvre.'},
    ],
    # Zvířata
    'kočky': [
        {'title': 'Kočka domácí - Wikipedie', 'url': 'https://cs.wikipedia.org/wiki/Kočka_domácí', 'popis': 'Informace o kočkách - historie, chování, péče.'},
        {'title': 'Kočky - Modrý kocouř', 'url': 'https://www.modrykocour.cz', 'popis': 'Portál pro milovníky koček. Rady, články, fórum.'},
        {'title': 'SOS Kočky', 'url': 'https://www.soskočky.cz', 'popis': 'Spolek na ochranu koček. Adopce, pomoc.'},
    ],
    # Hudba
    'beatles': [
        {'title': 'The Beatles - oficiální stránky', 'url': 'https://www.thebeatles.com', 'popis': 'Oficiální stránky legendární skupiny.'},
        {'title': 'The Beatles na Wikipedii', 'url': 'https://cs.wikipedia.org/wiki/The_Beatles', 'popis': 'Historie, alba, členové.'},
        {'title': 'Beatles - Spotify', 'url': 'https://open.spotify.com/artist/3WrFJ7ztbogyGnTHbHJFl2', 'popis': 'Poslouchejte Beatles na Spotify.'},
    ],
    # Sport
    'real madrid': [
        {'title': 'Real Madrid - oficiální stránky', 'url': 'https://www.realmadrid.com', 'popis': 'Oficiální stránky fotbalového klubu Real Madrid.'},
        {'title': 'Real Madrid na Wikipedii', 'url': 'https://cs.wikipedia.org/wiki/Real_Madrid', 'popis': 'Historie, úspěchy, hráči.'},
        {'title': 'Real Madrid - zprávy', 'url': 'https://www.sport.cz/fotbal/real-madrid/', 'popis': 'Aktuální zprávy o Realu Madrid.'},
    ]
}

# Obecné zdroje pro dotazy, které nemáme v databázi
OBECNE_ZDROJE = [
    {'title': 'Wikipedia - otevřená encyklopedie', 'url': 'https://cs.wikipedia.org/wiki/Hlavní_strana', 'popis': 'Vyhledejte na Wikipedii - otevřené encyklopedii.'},
    {'title': 'Google', 'url': 'https://www.google.com', 'popis': 'Vyhledávač Google - největší světový vyhledávač.'},
    {'title': 'Seznam', 'url': 'https://www.seznam.cz', 'popis': 'Český vyhledávač a portál Seznam.cz.'},
    {'title': 'YouTube', 'url': 'https://www.youtube.com', 'popis': 'Největší video portál na světě.'},
]

@app.route('/')
def index():
    """Hlavní stránka"""
    return render_template('index.html')

@app.route('/hledej')
def hledej():
    """Vyhledávání"""
    dotaz = request.args.get('q', '').strip().lower()
    
    if not dotaz:
        return jsonify({'error': 'Zadejte hledaný výraz'}), 400
    
    # Najdeme výsledky pro dotaz
    vysledky = []
    
    # Hledáme v naší databázi
    nalezeno = False
    for klic, zdroje in WEB_STRANKY.items():
        if klic in dotaz or dotaz in klic:
            vysledky = zdroje.copy()
            nalezeno = True
            break
    
    # Pokud jsme nenašli v databázi, vytvoříme obecné výsledky
    if not nalezeno:
        # Použijeme obecné zdroje
        for i, zdroj in enumerate(OBECNE_ZDROJE):
            novy_vysledek = {
                'title': zdroj['title'].replace('Wikipedia', f'Wikipedia: {dotaz}'),
                'url': zdroj['url'],
                'popis': f'{zdroj["popis"]} Hledáte "{dotaz}"?'
            }
            vysledky.append(novy_vysledek)
        
        # Přidáme pár specifických výsledků podle dotazu
        vysledky.append({
            'title': f'Informace o {dotaz}',
            'url': f'https://cs.wikipedia.org/wiki/{dotaz.replace(" ", "_")}',
            'popis': f'Článek na Wikipedii o tématu {dotaz}.'
        })
        vysledky.append({
            'title': f'Obrázky: {dotaz}',
            'url': f'https://www.google.com/search?q={dotaz}&tbm=isch',
            'popis': f'Vyhledat obrázky související s {dotaz}.'
        })
    
    # Omezíme na 5-8 výsledků
    if len(vysledky) > 8:
        vysledky = random.sample(vysledky, random.randint(5, 8))
    
    # Přidáme pozice
    for i, v in enumerate(vysledky):
        v['pozice'] = i + 1
    
    return jsonify({
        'dotaz': dotaz,
        'vysledky': vysledky,
        'pocet': len(vysledky)
    })

@app.route('/stahnout')
def stahnout():
    """Stažení výsledků jako JSON"""
    data = request.args.get('data', '')
    dotaz = request.args.get('dotaz', 'neznámý')
    
    if not data:
        return jsonify({'error': 'Žádná data ke stažení'}), 400
    
    try:
        vysledky = json.loads(data)
    except:
        return jsonify({'error': 'Neplatná data'}), 400
    
    # Vytvoříme název souboru
    cas = datetime.now().strftime('%Y%m%d_%H%M%S')
    nazev_souboru = f'vysledky_{dotaz}_{cas}.json'
    
    # Vytvoříme JSON v paměti
    output = io.BytesIO()
    output.write(json.dumps(vysledky, indent=2, ensure_ascii=False).encode('utf-8'))
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/json',
        as_attachment=True,
        download_name=nazev_souboru
    )

if __name__ == '__main__':
    # Pro Render - port z prostředí
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
#else:
    # Pro lokální vývoj
    #app.run(debug=True, port=5000)