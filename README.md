# Ordbok — offline Norsk ↔ English dictionary

Word translator for Android. About **35,000 words**, no internet after install.
Not a sentence translator.

**Do not install the APK from the Grok live preview.** That download is wrapped
in a zip / sandbox link, so Android either refuses it or the word list never
loads. Get the app from **GitHub Releases** on this repo.

## Install on your Poco X3 (or any Android phone)

1. On the phone, open  
   **https://github.com/a1blue2018/offline-translator-app/releases**
2. Open the latest release (**Ordbok 1.1**).
3. Tap **`Ordbok.apk`**.  
   If the file is named `Ordbok.apk.zip`, rename it and delete `.zip`.
4. Allow **Chrome** or **Files** to install unknown apps when MIUI asks.
5. If Security / Play Protect warns, tap **Install anyway**.
6. Open **Ordbok** and search `hei` — you should see **hi**.

First open can take a couple of seconds while the word list is read from the phone.

## If GitHub has no release yet

1. Open this repo → **Actions**.
2. Open the latest **Build APK** run (or **Run workflow** → **Build APK**).
3. Wait until it is green.
4. Open **https://github.com/a1blue2018/offline-translator-app/releases** and
   download `Ordbok.apk`.

## Recreate this repo from scratch

1. On GitHub: **New repository** → name `offline-translator-app` → Public → Create.
2. Copy every file from this project into that repo (same folders).
3. GitHub Actions will build the APK on every push to `main` and attach it to a
   release named `v1.1`.

## What this app is

- Norwegian Bokmål ↔ English **words** (not full sentences)
- Fully offline WebView app (`app.ordbok`)
- Words are packed into the APK (`dictionary-data.js`), not fetched from the web

Dictionary sources: Wiktionary (kaikki.org) + FreeDict/WikDict, CC BY-SA 3.0/4.0.
