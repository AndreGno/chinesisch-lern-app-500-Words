function mische(array) {
  const kopie = [...array];
  for (let i = kopie.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [kopie[i], kopie[j]] = [kopie[j], kopie[i]];
  }
  return kopie;
}

export function zerlegeInZeichen(satz) {
  return satz.replace(/[，。？！]/g, "").split("");
}

export function rendereSatzbau(dialogZeilen, container) {
  const satzListe = dialogZeilen.filter((z) => z.zh.length >= 3);
  let index = 0;

  function zeigeAufgabe() {
    if (index >= satzListe.length) {
      container.innerHTML = "<p>Alle Sätze geschafft! 做得好!</p>";
      return;
    }
    const zielSatz = satzListe[index];
    const teile = mische(zerlegeInZeichen(zielSatz.zh));
    container.innerHTML = `
      <p class="de">${zielSatz.de ?? ""}</p>
      <div id="ziel" class="satzbau-ziel"></div>
      <div id="bausteine" class="satzbau-bausteine"></div>
      <button id="pruefen">Prüfen</button>
      <p id="ergebnis"></p>
      <button id="ergebnis-weiter">Nächster Satz</button>
    `;
    const zielEl = container.querySelector("#ziel");
    const bausteineEl = container.querySelector("#bausteine");
    teile.forEach((zeichen) => {
      const btn = document.createElement("button");
      btn.textContent = zeichen;
      btn.addEventListener("click", () => {
        zielEl.append(zeichen);
        btn.disabled = true;
      });
      bausteineEl.appendChild(btn);
    });
    container.querySelector("#pruefen").addEventListener("click", () => {
      const eingabe = zielEl.textContent;
      const korrekt = zerlegeInZeichen(zielSatz.zh).join("");
      container.querySelector("#ergebnis").textContent =
        eingabe === korrekt ? "Richtig! ✓" : `Nicht ganz — richtig wäre: ${zielSatz.zh}`;
    });
  }

  zeigeAufgabe();
  container.addEventListener("click", (e) => {
    if (e.target.id === "ergebnis-weiter") {
      index += 1;
      zeigeAufgabe();
    }
  });
}
