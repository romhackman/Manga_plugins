import requests
from bs4 import BeautifulSoup
import os
import webbrowser

# URL du site
url = "https://hhentai.fr"

# Récupérer la page
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# Extraire les liens et images
liens = []
for a_tag in soup.find_all("a", href=True):
    href = a_tag['href']
    img_tag = a_tag.find("img")
    if img_tag:
        src = img_tag.get("src")
        # Filtrer liens invalides
        if href not in ['/', '#', '\\'] and src:
            liens.append({"lien": href, "image": src})

# Générer HTML
file_name = "galerie_liens.html"
html_content = """
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Galerie Sélectionnable</title>
<style>
body {
    margin: 0;
    padding: 20px;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(120deg, #2a0a3b, #1a0a2a);
    color: #f0e6f6;
    overflow-x: hidden;
}
h1 { text-align:center; color:#e0b3ff; font-size:3em; text-shadow:0 0 15px #c27eff; margin-bottom:40px; }
.gallery {
    display:grid;
    grid-template-columns:repeat(auto-fill, minmax(180px, 1fr));
    gap:20px;
}
.card {
    background:#3b1a4a; border-radius:15px; padding:10px; box-shadow:0 5px 15px rgba(0,0,0,0.4);
    display:flex; flex-direction:column; align-items:center; transition:0.4s; cursor:pointer;
}
.card:hover { transform:translateY(-10px) scale(1.05); box-shadow:0 20px 30px rgba(0,0,0,0.6); background:#4a1a6a; }
.card img { width:100%; border-radius:10px; margin-bottom:10px; object-fit:cover; border:2px solid #a356c0; }
.card label { font-size:14px; word-break:break-word; text-align:center; color:#ffe6ff; margin-top:5px; text-shadow:0 0 5px #b25eff; }
.linkCheckbox { transform: scale(1.5); margin-bottom:5px; accent-color:#c27eff; }
#saveButton { position:fixed; bottom:20px; left:20px; padding:15px 30px; background-color:#c27eff; border:none; border-radius:12px; color:white; font-size:18px; cursor:pointer; }
#saveButton:hover { background-color:#a353ff; transform:scale(1.1); }
</style>
</head>
<body>
<h1>Galerie Sélectionnable</h1>
<div class="gallery">
"""

# Ajouter les cartes en sautant le premier lien
for item in liens[1:]:
    html_content += f"""
    <div class="card">
        <input type="checkbox" class="linkCheckbox" value="{item['lien']}">
        <img src="{item['image']}" alt="image">
        <label><a href="{item['lien']}" target="_blank" style="color:#ffe6ff;text-decoration:none;">{item['lien']}</a></label>
    </div>
    """

html_content += """
</div>
<button id="saveButton">Sauvegarder mes choix</button>
<script>
document.getElementById('saveButton').addEventListener('click', function() {
    const checkboxes = document.querySelectorAll('.linkCheckbox');
    let selectedLinks = [];
    checkboxes.forEach(cb => { if(cb.checked) selectedLinks.push(cb.value); });
    const blob = new Blob([JSON.stringify(selectedLinks, null, 4)], {type: "application/json"});
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = "liens_selectionnes.json";
    a.click();
});
</script>
</body>
</html>
"""

# Écrire le fichier
with open(file_name, "w", encoding="utf-8") as f:
    f.write(html_content)

# Ouvrir le HTML après la fin du script
webbrowser.open('file://' + os.path.abspath(file_name))
