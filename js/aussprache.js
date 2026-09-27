function aehnlichkeit(a, b) {
  const laenge = Math.max(a.length, b.length);
  if (laenge === 0) return 1;
  let treffer = 0;
  for (let i = 0; i < Math.min(a.length, b.length); i++) {
    if (a[i] === b[i]) treffer += 1;
  }
  return treffer / laenge;
}

export function bewerteAussprache(erkannterText, zielText) {
  const score = aehnlichkeit(erkannterText.trim(), zielText.trim());
  if (score > 0.8) return { label: "Sehr gut!", score };
  if (score > 0.5) return { label: "Geht in die richtige Richtung.", score };
  return { label: "Nochmal versuchen.", score };
}

export function rendereAussprache(dialogZeilen, container) {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const zeilen = dialogZeilen.filter((z) => z.zh);
  let index = 0;

  function zeigeSatz() {
    if (index >= zeilen.length) {
      container.innerHTML = "<p>Ausspracheübung beendet!</p>";
      return;
    }
    const ziel = zeilen[index];
    container.innerHTML = `
      <p class="zh">${ziel.zh}</p>
      ${ziel.audio ? `<audio controls src="${ziel.audio}"></audio>` : ""}
      <button id="aufnehmen" ${SpeechRecognition ? "" : "disabled"}>🎤 Sprechen</button>
      ${SpeechRecognition ? "" : `<p class="hinweis">Aussprache-Erkennung wird von diesem
        Browser nicht unterstützt — funktioniert zuverlässig nur in Chrome oder Edge.</p>`}
      <p id="ergebnis"></p>
      <button id="weiter">Nächster Satz</button>
    `;
    if (SpeechRecognition) {
      const aufnehmenBtn = container.querySelector("#aufnehmen");
      aufnehmenBtn.addEventListener("click", () => {
        // Button sofort sperren, damit kein zweiter Erkennungsversuch startet,
        // solange der erste noch läuft.
        aufnehmenBtn.disabled = true;
        const erkennung = new SpeechRecognition();
        erkennung.lang = "zh-TW";
        erkennung.onresult = (event) => {
          // Wenn der Nutzer inzwischen zu einer anderen Übung gewechselt hat, wurde
          // dieser Button (und der ganze Inhalt von container) bereits durch die neue
          // Übung ersetzt — dann nicht mehr in das alte #ergebnis schreiben.
          if (!aufnehmenBtn.isConnected) return;
          const erkannterText = event.results[0][0].transcript;
          const bewertung = bewerteAussprache(erkannterText, ziel.zh);
          container.querySelector("#ergebnis").textContent =
            `Erkannt: "${erkannterText}" — ${bewertung.label}`;
          aufnehmenBtn.disabled = false;
        };
        erkennung.onerror = () => {
          if (!aufnehmenBtn.isConnected) return;
          container.querySelector("#ergebnis").textContent =
            "Aufnahme fehlgeschlagen — Mikrofon-Zugriff erlaubt?";
          aufnehmenBtn.disabled = false;
        };
        erkennung.start();
      });
    }
    container.querySelector("#weiter").addEventListener("click", () => {
      index += 1;
      zeigeSatz();
    });
  }

  zeigeSatz();
}
