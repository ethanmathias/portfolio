#!/usr/bin/env python3
"""Encrypt src/index.html into a password-gated index.html.

The page body is encrypted with AES-256-GCM using a key derived from the
password (PBKDF2-SHA256), so the published HTML and the public repo contain
only ciphertext. Visitors unlock with the form, or with ?key=<password>.

Password source, in order: $PORTFOLIO_PASSWORD, .portfolio-password, prompt.
Images and video in assets/ are NOT encrypted; they are reachable by direct URL.

    python3 build.py
"""
import base64, getpass, json, os, re, sys
from pathlib import Path
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src" / "index.html"
OUT = ROOT / "index.html"
PW_FILE = ROOT / ".portfolio-password"
ITERATIONS = 300_000


def get_password():
    pw = os.environ.get("PORTFOLIO_PASSWORD")
    if not pw and PW_FILE.exists():
        pw = PW_FILE.read_text().strip()
    if not pw:
        pw = getpass.getpass("Portfolio password: ")
    if not pw:
        sys.exit("No password given.")
    return pw


def encrypt(plaintext, password):
    salt, iv = os.urandom(16), os.urandom(12)
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITERATIONS)
    key = kdf.derive(password.encode())
    ct = AESGCM(key).encrypt(iv, plaintext.encode(), None)
    b64 = lambda b: base64.b64encode(b).decode()
    return {"salt": b64(salt), "iv": b64(iv), "ct": b64(ct), "iter": ITERATIONS}


def main():
    src = SRC.read_text()
    head = re.search(r"<head>(.*?)</head>", src, re.S).group(1)
    body = re.search(r"<body>(.*?)</body>", src, re.S).group(1)
    body = re.sub(r"<script>.*?</script>", "", body, flags=re.S).strip()

    payload = json.dumps(encrypt(body, get_password()))
    OUT.write_text(TEMPLATE.replace("%%HEAD%%", head.strip()).replace("%%PAYLOAD%%", payload))
    print(f"Wrote {OUT.relative_to(ROOT)} ({len(payload) // 1024} KB payload)")


TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  %%HEAD%%
</head>
<body>
  <main class="gate" id="gate" hidden>
    <form class="gate-box" id="gate-form">
      <p class="mono muted gate-label">Private portfolio</p>
      <h1 class="gate-title">Enter password</h1>
      <div class="gate-row">
        <input id="gate-pw" type="password" autocomplete="current-password" aria-label="Password" autofocus>
        <button type="submit">Open</button>
      </div>
      <p class="gate-error" id="gate-error" role="alert"></p>
    </form>
  </main>

  <script>
    const PAYLOAD = %%PAYLOAD%%;
    const STORE = 'portfolio-key';
    const b64 = (s) => Uint8Array.from(atob(s), (c) => c.charCodeAt(0));

    async function decrypt(password) {
      const base = await crypto.subtle.importKey('raw', new TextEncoder().encode(password), 'PBKDF2', false, ['deriveKey']);
      const key = await crypto.subtle.deriveKey(
        { name: 'PBKDF2', salt: b64(PAYLOAD.salt), iterations: PAYLOAD.iter, hash: 'SHA-256' },
        base, { name: 'AES-GCM', length: 256 }, false, ['decrypt']);
      const pt = await crypto.subtle.decrypt({ name: 'AES-GCM', iv: b64(PAYLOAD.iv) }, key, b64(PAYLOAD.ct));
      return new TextDecoder().decode(pt);
    }

    function reveal() {
      const io = new IntersectionObserver((entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
        });
      }, { threshold: 0.12 });
      document.querySelectorAll('.reveal').forEach((el) => io.observe(el));
    }

    async function unlock(password, remember) {
      try {
        const html = await decrypt(password);
        document.body.innerHTML = html;
        if (remember) { try { localStorage.setItem(STORE, password); } catch (e) {} }
        reveal();
        if (location.hash) document.querySelector(location.hash)?.scrollIntoView();
        return true;
      } catch (e) {
        return false;
      }
    }

    (async () => {
      const fromUrl = new URLSearchParams(location.search).get('key');
      let saved = null;
      try { saved = localStorage.getItem(STORE); } catch (e) {}
      for (const pw of [fromUrl, saved]) {
        if (pw && await unlock(pw, true)) return;
      }
      const gate = document.getElementById('gate');
      gate.hidden = false;
      document.getElementById('gate-form').addEventListener('submit', async (ev) => {
        ev.preventDefault();
        const err = document.getElementById('gate-error');
        err.textContent = '';
        const ok = await unlock(document.getElementById('gate-pw').value, true);
        if (!ok) err.textContent = 'Incorrect password.';
      });
    })();
  </script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
