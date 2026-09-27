function mische(array) {
  const kopie = [...array];
  for (let i = kopie.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [kopie[i], kopie[j]] = [kopie[j], kopie[i]];
  }
  return kopie;
}

export function erzeugeOptionen(zielZeile, alleZeilen, anzahl = 4) {
  const andere = alleZeilen.filter((z) => z !== zielZeile);
  const ablenkerAnzahl = Math.min(anzahl - 1, andere.length);
  const ablenker = mische(andere).slice(0, ablenkerAnzahl);
  return mische([zielZeile, ...ablenker]);
}

export function rendereHoerverstehen(dialogZeilen, container) {
  const zeilen = dialogZeilen.filter((z) => z.audio && z.de);
  let index = 0;

  function zeigeFrage() {
    if (index >= zeilen.length) {
      container.innerHTML = "<p>Quiz beendet!</p>";
      return;
    }
    const ziel = zeilen[index];
    const optionen = erzeugeOptionen(ziel, zeilen);
    container.innerHTML = `
      <audio controls autoplay src="${ziel.audio}"></audio>
      <p>Welche Übersetzung passt?</p>
      <ul class="quiz-optionen">
        ${optionen.map((o, i) => `<li><button data-i="${i}">${o.de}</button></li>`).join("")}
      </ul>
      <p id="ergebnis"></p>
    `;
    const optionsButtons = container.querySelectorAll("[data-i]");
    optionsButtons.forEach((btn, i) => {
      btn.addEventListener("click", () => {
        // Buttons sofort sperren, damit ein zweiter Klick innerhalb der 1,2s keinen
        // weiteren Timeout auslöst (sonst würde eine Frage übersprungen).
        optionsButtons.forEach((b) => (b.disabled = true));
        const richtig = optionen[i] === ziel;
        container.querySelector("#ergebnis").textContent = richtig
          ? "Richtig! ✓"
          : `Falsch — richtig: ${ziel.de}`;
        setTimeout(() => {
          // Wenn der Nutzer inzwischen zu einer anderen Übung gewechselt hat, wurde
          // dieser Button (und der ganze Inhalt von container) bereits durch die neue
          // Übung ersetzt — dann nicht mehr die alte zeigeFrage() nachschieben.
          if (!btn.isConnected) return;
          index += 1;
          zeigeFrage();
        }, 1200);
      });
    });
  }

  zeigeFrage();
}
