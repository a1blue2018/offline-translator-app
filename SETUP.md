# Setup Instructions for Ordbok

This guide walks you through generating the missing `dictionary-data.js` file and building the APK locally.

## Prerequisites

Before you start, ensure you have:

- **Python 3.8+** installed
- **Java 17** or later (for Android build tools)
- **Android SDK** with platform 34 and build-tools 34.0.0
- **Gradle 8.7** (or higher)
- **Internet connection** (to download dictionary sources ~1–2 GB)

### Quick Check

```bash
python3 --version      # Should show 3.8+
java -version          # Should show 17+
gradle --version       # Should show 8.7+
```

---

## Step 1: Clone the Repository

```bash
git clone https://github.com/a1blue2018/offline-translator-app.git
cd offline-translator-app
```

---

## Step 2: Download Dictionary Sources

Create the `dict-src/` directory and download the required files. This takes **3–5 minutes**.

```bash
mkdir -p dict-src

# Download Norwegian Wiktionary (kaikki.org)
curl -L --fail -o dict-src/nb.jsonl.gz \
  "https://kaikki.org/dictionary/Norwegian%20Bokm%C3%A5l/kaikki.org-dictionary-NorwegianBokm%C3%A5l.jsonl.gz"

# Decompress
gunzip -f dict-src/nb.jsonl.gz

# Download frequency lists (for ranking words by commonality)
curl -L --fail -o dict-src/no_50k.txt \
  "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/no/no_50k.txt"

curl -L --fail -o dict-src/en_50k.txt \
  "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/en/en_50k.txt"

# Download FreeDict English-Norwegian dictionary (TEI format)
curl -L --fail -o dict-src/eng-nor.src.tar.xz \
  "https://download.freedict.org/dictionaries/eng-nor/2025.11.23/freedict-eng-nor-2025.11.23.src.tar.xz"

# Extract the archive
tar -xJf dict-src/eng-nor.src.tar.xz -C dict-src
```

**What was downloaded:**
- `nb.jsonl` (~500 MB) – Norwegian word definitions from Wiktionary
- `no_50k.txt` – 50,000 most common Norwegian words
- `en_50k.txt` – 50,000 most common English words
- `eng-nor.src.tar.xz` (extracted) – English-Norwegian dictionary in TEI XML format

---

## Step 3: Generate the Dictionary Data File

Run the Python build script to parse the sources and generate `dictionary-data.js`:

```bash
python3 scripts/build-dictionary.py
```

**What this does:**
1. Reads Norwegian words from `dict-src/nb.jsonl`
2. Reads English words from the extracted FreeDict TEI files
3. Extracts translations, parts of speech, IPA pronunciation (when available)
4. Ranks words by frequency using the `*_50k.txt` lists
5. Selects the top 35,000 words
6. Outputs a compact JSON array to `app/src/main/assets/www/dictionary-data.js`

**Expected output:**
```
entries=35000 nb=24563 en=10437
  hei: OK
  takk: OK
  hus: OK
  bok: OK
```

If you see `MISSING` for any of these test words, check that `dict-src/nb.jsonl` was downloaded correctly.

---

## Step 4: Verify the Generated File

Confirm the dictionary file was created:

```bash
ls -lh app/src/main/assets/www/dictionary-data.js
```

You should see a file around **2–3 MB** in size.

Peek at its contents:

```bash
head -c 200 app/src/main/assets/www/dictionary-data.js
```

You should see something like:
```javascript
window.__ORDBOK_DATA__=[{"w":"...","src":"nb",...},...
```

---

## Step 5: Build the Android APK

Set up Gradle and build the release APK:

```bash
gradle assembleRelease --no-daemon
```

This will:
1. Compile the Java code
2. Bundle the HTML, CSS, JavaScript, and `dictionary-data.js` into the APK
3. Optimize and sign with the debug key
4. Output the APK to `app/build/outputs/apk/release/app-release.apk`

**Build time:** 1–2 minutes on most systems.

---

## Step 6: Locate and Test the APK

The built APK is at:

```bash
ls -lh app/build/outputs/apk/release/app-release.apk
```

**To install on a connected Android device:**

```bash
adb install -r app/build/outputs/apk/release/app-release.apk
```

**Or manually:**
1. Connect your Android phone via USB
2. Transfer `app/build/outputs/apk/release/app-release.apk` to the phone
3. Open Files or Chrome on the phone
4. Tap the APK and allow installation

**Test the app:**
- Open **Ordbok** on your phone
- Search for `hei` → should show **hi**
- Search for `takk` → should show **thanks**
- Toggle between **Norsk → English** and **English → Norsk** modes

---

## Troubleshooting

### `dictionary-data.js` is empty or missing

**Cause:** The Python script didn't run successfully.

**Fix:**
```bash
# Check that dict-src/nb.jsonl exists and is not empty
ls -lh dict-src/nb.jsonl

# Re-run the build script with verbose output
python3 scripts/build-dictionary.py
```

### Build fails with "Java version mismatch"

**Cause:** You don't have Java 17+.

**Fix:**
```bash
java -version

# If < 17, install or update Java
# macOS: brew install openjdk@17
# Ubuntu/Debian: sudo apt-get install openjdk-17-jdk
# Windows: Download from https://adoptium.net/
```

### Gradle not found

**Cause:** Gradle is not installed or not in PATH.

**Fix:**
```bash
# Install via a package manager or download from https://gradle.org/releases/
# Then set GRADLE_HOME and add to PATH, or use:
./gradlew assembleRelease  # (if gradlew wrapper is in the repo)
```

### APK won't install on phone

**Cause:** Phone security or incorrect APK format.

**Fix:**
1. Ensure the file is actually an APK: `file app/build/outputs/apk/release/app-release.apk`
2. Enable "Unknown Sources" or "Install unknown apps" on your phone (Settings → Apps & notifications → Install unknown apps)
3. Try `adb install -r` flag to replace an existing version

---

## Next Steps

Once you have a working APK:

1. **Test it thoroughly** on different Android versions (API 24–34).
2. **Share it** via GitHub Releases using the workflow (or manually upload).
3. **Iterate:** Edit `app/src/main/assets/www/index.html` for UI changes, re-run steps 5–6.

---

## Automated Build (CI/CD)

If you push to the `main` branch, GitHub Actions will automatically:
1. Download dictionary sources
2. Run `build-dictionary.py`
3. Build the APK
4. Publish it to **Releases** as `Ordbok.apk`

No local build needed if CI succeeds!

See `.github/workflows/build-apk.yml` for details.
