import os
import time
import threading
import queue
import requests
import pyperclip
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from bs4 import BeautifulSoup

# ================= CONFIG =================
FOND_PRINCIPAL = "#d5c0c1"
BOUTON_BG = "#805d65"
BOUTON_FG = "#d5c0c1"
BOUTON_HOVER = "#ab495e"
TEXT_COLOR = "#241d1f"
ACCENT_COLOR = "#241d1f"

MAX_BOTS = 5
DOSSIER_BASE = "images_telechargees"
DELAY = 0.05
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}
# =========================================

lock = threading.Lock()
total_images = 0
images_finies = 0
surveillance_active = False

# ---------------- Fonctions ----------------
def telecharger_image(url, dossier, num):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        ext = os.path.splitext(url)[1] or ".png"
        nom_fichier = f"page_{num}{ext}"
        with open(os.path.join(dossier, nom_fichier), "wb") as f:
            f.write(response.content)
        return True
    except:
        return False

def bot_worker(q):
    global images_finies
    while True:
        try:
            url, dossier, num, lbl = q.get_nowait()
        except queue.Empty:
            break
        lbl.config(text=f"Image {num} : ⏳ Téléchargement", fg=ACCENT_COLOR)
        telecharger_image(url, dossier, num)
        lbl.config(text=f"Image {num} : ✔ Terminé", fg=TEXT_COLOR)
        with lock:
            images_finies += 1
            progress_var.set(int(images_finies / total_images * 100))
        q.task_done()

def lancer_telechargement():
    global total_images, images_finies
    base_url = entry_url.get().strip()
    if not base_url.startswith("https://fr.3hentai.net/d/"):
        messagebox.showerror("Erreur", "Le lien n'est pas valide.")
        return

    try:
        start_page = int(entry_start.get())
        end_page = int(entry_end.get())
        if start_page > end_page or start_page < 1:
            raise ValueError
    except:
        messagebox.showerror("Erreur", "Intervalle de pages invalide.")
        return

    for w in frame_images.winfo_children():
        w.destroy()

    dossier = DOSSIER_BASE
    os.makedirs(dossier, exist_ok=True)

    # Récupération des images depuis la page principale
    try:
        base_html = requests.get(base_url, headers=HEADERS).text
        soup = BeautifulSoup(base_html, "html.parser")
        images_tags = soup.find_all("img", class_="lazy")
        urls_images = [img.get("data-src") or img.get("src") for img in images_tags if img.get("data-src") or img.get("src")]
    except:
        messagebox.showerror("Erreur", "Impossible de récupérer les images depuis la page.")
        return

    # Sélection de l’intervalle
    urls_images = urls_images[start_page-1:end_page]

    total_images = len(urls_images)
    if total_images == 0:
        messagebox.showinfo("Info", "Aucune image à télécharger.")
        return

    q = queue.Queue()
    images_finies = 0

    for i, url in enumerate(urls_images, start=start_page):
        lbl = tk.Label(frame_images, text=f"Image {i} : ⏳ En attente", bg=FOND_PRINCIPAL, fg=TEXT_COLOR, anchor="w")
        lbl.pack(fill="x", pady=2)
        q.put((url, dossier, i, lbl))

    threads = []
    for _ in range(min(MAX_BOTS, total_images)):
        t = threading.Thread(target=bot_worker, args=(q,))
        t.start()
        threads.append(t)

    def attendre():
        for t in threads:
            t.join()
        messagebox.showinfo("Terminé", f"Toutes les images ({total_images}) ont été téléchargées dans {dossier}.")

    threading.Thread(target=attendre).start()

# ---------------- Trouver nombre de pages ----------------
def trouver_nb_pages():
    url = entry_url.get().strip()
    if not url.startswith("https://fr.3hentai.net/d/"):
        messagebox.showerror("Erreur", "Lien invalide.")
        return
    try:
        html = requests.get(url, headers=HEADERS).text
        soup = BeautifulSoup(html, "html.parser")
        images_tags = soup.find_all("img", class_="lazy")
        nb_pages = len(images_tags)
        entry_start.delete(0, tk.END)
        entry_start.insert(0, "1")
        entry_end.delete(0, tk.END)
        entry_end.insert(0, str(nb_pages))
        messagebox.showinfo("Info", f"{nb_pages} pages détectées.")
    except:
        messagebox.showerror("Erreur", "Impossible de récupérer le nombre de pages.")

# ---- Effet survol bouton ----
def on_enter(e):
    e.widget['background'] = BOUTON_HOVER

def on_leave(e):
    e.widget['background'] = BOUTON_BG

# ---------------- Tkinter ----------------
root = tk.Tk()
root.title("Téléchargeur 3Hentai")
root.geometry("1100x600")
root.config(bg=FOND_PRINCIPAL)

# ---- Logo ----
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(BASE_DIR, "logo.png")
try:
    root.iconphoto(False, tk.PhotoImage(file=logo_path))
except Exception as e:
    print("Erreur chargement icône :", e)

# ---- Frame gauche ----
frame_gauche = tk.Frame(root, bg=FOND_PRINCIPAL)
frame_gauche.pack(side="left", fill="both", expand=True, padx=10, pady=10)

tk.Label(frame_gauche, text="Téléchargeur 3Hentai", bg=FOND_PRINCIPAL, fg=TEXT_COLOR, font=("Arial", 16, "bold")).pack(pady=10)

tk.Label(frame_gauche, text="Lien :", bg=FOND_PRINCIPAL, fg=TEXT_COLOR).pack(pady=5)
entry_url = tk.Entry(frame_gauche, width=50, bg="#f0e8e9", fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
entry_url.pack(pady=5)

tk.Label(frame_gauche, text="Page de début :", bg=FOND_PRINCIPAL, fg=TEXT_COLOR).pack(pady=5)
entry_start = tk.Entry(frame_gauche, width=10, bg="#f0e8e9", fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
entry_start.pack(pady=5)

tk.Label(frame_gauche, text="Page de fin :", bg=FOND_PRINCIPAL, fg=TEXT_COLOR).pack(pady=5)
entry_end = tk.Entry(frame_gauche, width=10, bg="#f0e8e9", fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
entry_end.pack(pady=5)

# ---- Boutons ----

btn_trouver_pages = tk.Button(frame_gauche, text="Trouver nombre de pages",
                              bg=BOUTON_BG, fg=BOUTON_FG, width=30, command=trouver_nb_pages)
btn_trouver_pages.pack(pady=5)
btn_trouver_pages.bind("<Enter>", on_enter)
btn_trouver_pages.bind("<Leave>", on_leave)

btn_lancer = tk.Button(frame_gauche, text="Télécharger", command=lancer_telechargement,
                       bg=BOUTON_BG, fg=BOUTON_FG, width=25)
btn_lancer.pack(pady=10)
btn_lancer.bind("<Enter>", on_enter)
btn_lancer.bind("<Leave>", on_leave)

progress_var = tk.IntVar()
ttk.Progressbar(frame_gauche, variable=progress_var, maximum=100).pack(fill="x", padx=20, pady=10)

frame_images = tk.Frame(frame_gauche, bg=FOND_PRINCIPAL)
frame_images.pack(fill="both", expand=True, padx=10, pady=10)

# ---- Frame droite image ----
frame_droite = tk.Frame(root, bg=FOND_PRINCIPAL)
frame_droite.pack(side="right", fill="y", padx=10, pady=10)

image_path = os.path.join(BASE_DIR, "image.png")
try:
    image = Image.open(image_path)
    hauteur_fenetre = 600
    ratio = image.width / image.height
    nouvelle_hauteur = hauteur_fenetre
    nouvelle_largeur = int(ratio * nouvelle_hauteur)
    image = image.resize((nouvelle_largeur, nouvelle_hauteur), Image.Resampling.LANCZOS)
    photo = ImageTk.PhotoImage(image)
    lbl_image = tk.Label(frame_droite, image=photo, bg=FOND_PRINCIPAL, bd=0, highlightthickness=0)
    lbl_image.image = photo
    lbl_image.pack()
except Exception as e:
    print("Erreur chargement image :", e)

root.mainloop()
