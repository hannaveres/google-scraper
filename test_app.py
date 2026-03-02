import unittest
import json
from app import app

class TestVyhledavac(unittest.TestCase):
    
    def setUp(self):
        """Nastavení před každým testem"""
        self.app = app.test_client()
        self.app.testing = True
    
    def test_hlavni_stranka(self):
        """Test, že hlavní stránka se načte"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        # Oprava: použijeme normální string a decode
        self.assertIn('Vyhledávač', response.data.decode('utf-8'))
    
    def test_hledej_bez_dotazu(self):
        """Test vyhledávání bez dotazu"""
        response = self.app.get('/hledej')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)
    
    def test_hledej_python(self):
        """Test vyhledávání 'python'"""
        response = self.app.get('/hledej?q=python')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['dotaz'], 'python')
        self.assertTrue(data['pocet'] > 0)
        self.assertTrue(len(data['vysledky']) > 0)
        
        # Kontrola struktury prvního výsledku
        prvni = data['vysledky'][0]
        self.assertIn('title', prvni)
        self.assertIn('url', prvni)
        self.assertIn('popis', prvni)
        self.assertIn('pozice', prvni)
        self.assertEqual(prvni['pozice'], 1)
    
    def test_hledej_javascript(self):
        """Test vyhledávání 'javascript'"""
        response = self.app.get('/hledej?q=javascript')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['dotaz'], 'javascript')
        self.assertTrue(data['pocet'] > 0)
        
        # Kontrola že výsledky obsahují JavaScript
        obsahuje_js = any('JavaScript' in v['title'] for v in data['vysledky'])
        self.assertTrue(obsahuje_js)
    
    def test_hledej_neznamy_dotaz(self):
        """Test vyhledávání neznámého dotazu"""
        response = self.app.get('/hledej?q=neznámýdotaz123')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['dotaz'], 'neznámýdotaz123')
        self.assertTrue(data['pocet'] > 0)
        
        # Kontrola že máme obecné výsledky
        prvni = data['vysledky'][0]
        self.assertIn('Wikipedia', prvni['title'])
    
    def test_pocet_vysledku(self):
        """Test že počet výsledků je mezi 5-8"""
        response = self.app.get('/hledej?q=test')
        data = json.loads(response.data)
        
        pocet = data['pocet']
        self.assertTrue(5 <= pocet <= 8, f"Počet výsledků je {pocet}, měl by být 5-8")
    
    def test_vysledky_maji_spravne_url(self):
        """Test že URL začínají http nebo https"""
        response = self.app.get('/hledej?q=python')
        data = json.loads(response.data)
        
        for v in data['vysledky']:
            url = v['url']
            self.assertTrue(url.startswith('http'), f"URL {url} nezačíná http")
    
    def test_download_json(self):
        """Test stažení JSON"""
        # Nejdříve vyhledáme
        response = self.app.get('/hledej?q=python')
        data = json.loads(response.data)
        
        # Pak stáhneme
        data_str = json.dumps(data['vysledky'])
        response = self.app.get(f'/stahnout?data={data_str}&dotaz=python')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'application/json')
        self.assertTrue('attachment' in response.headers['Content-Disposition'])
    
    def test_download_bez_dat(self):
        """Test stažení bez dat"""
        response = self.app.get('/stahnout')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)

if __name__ == '__main__':
    unittest.main()