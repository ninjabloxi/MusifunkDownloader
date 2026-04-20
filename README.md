# 🎵 Musifunk Download Bot

Bot Discord pour télécharger des MP3 avec `/mdownload {lien}`.

## Sources supportées

| Source | Exemple |
|---|---|
| YouTube | `https://youtube.com/watch?v=...` |
| YouTube Shorts | `https://youtube.com/shorts/...` |
| Spotify (piste) | `https://open.spotify.com/track/...` |
| GitHub Raw | `https://raw.githubusercontent.com/.../file.mp3` |
| Lien direct MP3 | `https://example.com/son.mp3` |
| SoundCloud, Deezer preview... | via yt-dlp générique |

---

## Installation

### 1. Prérequis

- Python 3.10+
- [FFmpeg](https://ffmpeg.org/download.html) installé et dans le PATH

```bash
# Windows (avec winget)
winget install ffmpeg

# macOS
brew install ffmpeg

# Linux
sudo apt install ffmpeg
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Créer le bot Discord

1. Va sur https://discord.com/developers/applications
2. **New Application** → donne un nom
3. Onglet **Bot** → **Add Bot** → copie le token
4. Onglet **OAuth2 > URL Generator** → coche `bot` + `applications.commands`
5. Permissions : `Send Messages`, `Attach Files`, `Use Slash Commands`
6. Copie l'URL générée et invite le bot sur ton serveur

### 4. Configurer le bot

Dans `bot.py`, remplace la ligne :
```python
BOT_TOKEN = "TON_TOKEN_ICI"
```
par ton vrai token.

### 5. Lancer

```bash
python bot.py
```

---

## Utilisation

```
/mdownload https://youtube.com/watch?v=dQw4w9WgXcQ
/mdownload https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT
/mdownload https://raw.githubusercontent.com/user/repo/main/son.mp3
```

---

## Notes

- Limite Discord : **25 Mo** par fichier (8 Mo sans Nitro)
- Les fichiers temporaires sont supprimés automatiquement après l'envoi
- Spotify nécessite une connexion internet active pour chercher sur YouTube Music
