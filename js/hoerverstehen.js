function mische(array) {
  return [...array].sort(() => Math.random() - 0.5);
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
    container.querySelectorAll("[data-i]").forEach((btn, i) => {
      btn.addEventListener("click", () => {
        const richtig = optionen[i] === ziel;
        container.querySelector("#ergebnis").textContent = richtig
          ? "Richtig! ✓"
          : `Falsch — richtig: ${ziel.de}`;
        setTimeout(() => {
          index += 1;
          zeigeFrage();
        }, 1200);
      });
    });
  }

  zeigeFrage();
}
