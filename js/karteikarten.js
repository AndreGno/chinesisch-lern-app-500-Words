import { reviewCard, istFaellig } from "./srs.js";

const SPEICHER_SCHLUESSEL = "karteikarten-status";

// Der Status wird bewusst global nach `zh` (nicht pro Lektion) indiziert, damit ein
// Wort, das in mehreren Lektionen auftaucht, einen gemeinsamen Lernfortschritt hat.
// Bekannte, akzeptierte Einschränkung: 2 von 321 Vokabeln im Korpus (毛, 分) haben in
// unterschiedlichen Lektionen unterschiedliche Bedeutungen bei identischem Zeichen UND
// identischem Pinyin (毛 = "Haar" vs. "0,10 NT$", 分 = "Minute" vs. "0,01-0,09 NT$") —
// dort teilen sich beide Bedeutungen denselben Karteikarten-Status. Eine echte Behebung
// bräuchte ein separates Bedeutungs-Unterscheidungsfeld in den Lektionsdaten, was für
// 2 von 321 Wörtern nicht gerechtfertigt ist (YAGNI).

function ladeStatus() {
  try {
    return JSON.parse(localStorage.getItem(SPEICHER_SCHLUESSEL) || "{}");
  } catch {
    return {};
  }
}

function speichereStatus(status) {
  localStorage.setItem(SPEICHER_SCHLUESSEL, JSON.stringify(status));
}

export function faelligeVokabeln(vokabular, status) {
  return vokabular.filter((v) => {
    const karte = status[v.zh] ?? {};
    return istFaellig(karte);
  });
}

export function rendereKarteikarten(vokabular, container) {
  const status = ladeStatus();
  const faellig = faelligeVokabeln(vokabular, status);
  let index = 0;

  function zeigeKarte() {
    if (index >= faellig.length) {
      container.innerHTML = "<p>Für heute keine fälligen Karten mehr. 太好了!</p>";
      return;
    }
    const wort = faellig[index];
    container.innerHTML = `
      <div class="karteikarte">
        <p class="zh">${wort.zh}</p>
        <button id="aufdecken">Aufdecken</button>
        <div id="rueckseite" hidden>
          <p class="pinyin">${wort.zhuyin} · ${wort.pinyin}</p>
          <p class="de">${wort.de}</p>
          <div class="bewertung">
            <button data-q="0">Nochmal</button>
            <button data-q="1">Schwer</button>
            <button data-q="2">Gut</button>
            <button data-q="3">Leicht</button>
          </div>
        </div>
      </div>`;
    container.querySelector("#aufdecken").addEventListener("click", () => {
      container.querySelector("#rueckseite").hidden = false;
    });
    container.querySelectorAll(".bewertung button").forEach((btn) => {
      btn.addEventListener("click", () => {
        const qualitaet = Number(btn.dataset.q);
        const alteKarte = status[wort.zh] ?? { interval: 0, repetitions: 0, easeFactor: 2.5 };
        status[wort.zh] = reviewCard(alteKarte, qualitaet);
        speichereStatus(status);
        index += 1;
        zeigeKarte();
      });
    });
  }

  zeigeKarte();
}
