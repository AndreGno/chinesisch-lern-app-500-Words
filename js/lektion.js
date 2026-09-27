const TABS = [
  { key: "text", label: "課文 Text" },
  { key: "woerter", label: "字與詞 Wörter" },
  { key: "wiederholung", label: "溫習 Wiederholung" },
  { key: "anwendung", label: "應用 Anwendung" },
  { key: "uebungen", label: "Übungen" },
];

export function rendereTabs(lektion, container, onWahl) {
  container.innerHTML = "";
  for (const tab of TABS) {
    const btn = document.createElement("button");
    btn.textContent = tab.label;
    btn.addEventListener("click", () => onWahl(tab.key));
    container.appendChild(btn);
  }
}

export function rendereDialogListe(eintraege) {
  return eintraege
    .map(
      (e) => `
      <div class="dialog-zeile">
        <p class="zh">${e.sprecher ? e.sprecher + "：" : ""}${e.zh}</p>
        ${e.pinyin ? `<p class="pinyin">${e.pinyin}</p>` : ""}
        ${e.de ? `<p class="de">${e.de}</p>` : ""}
        ${e.audio ? `<audio controls src="${e.audio}"></audio>` : ""}
      </div>`
    )
    .join("");
}

export function rendereWoerterListe(eintraege) {
  return eintraege
    .map(
      (e) => `
      <div class="wort-zeile">
        <p class="zh">${e.zh} <span class="zhuyin">${e.zhuyin}</span></p>
        <p class="pinyin">${e.pinyin}</p>
        <p class="de">${e.de}</p>
      </div>`
    )
    .join("");
}

export function rendereTabInhalt(lektion, tabKey, container) {
  if (tabKey === "text" || tabKey === "anwendung") {
    container.innerHTML = rendereDialogListe(lektion[tabKey]);
  } else if (tabKey === "woerter") {
    container.innerHTML = rendereWoerterListe(lektion.woerter);
  } else if (tabKey === "wiederholung") {
    container.innerHTML = lektion.wiederholung
      .map((e) => `<p class="zh">${e.sprecher}：${e.zh}</p>`)
      .join("");
  } else if (tabKey === "uebungen") {
    container.innerHTML = `
      <div class="uebungen-menu">
        <button data-uebung="karteikarten">Karteikarten</button>
        <button data-uebung="satzbau">Satzbau</button>
        <button data-uebung="hoerverstehen">Hörverständnis</button>
        <button data-uebung="aussprache">Aussprache</button>
      </div>
      <div id="uebung-inhalt"></div>
    `;
    const inhalt = container.querySelector("#uebung-inhalt");
    container.querySelectorAll("[data-uebung]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const modul = btn.dataset.uebung;
        try {
          if (modul === "karteikarten") {
            const { rendereKarteikarten } = await import("./karteikarten.js");
            if (!inhalt.isConnected) return;
            rendereKarteikarten(lektion.woerter, inhalt);
          } else if (modul === "satzbau") {
            const { rendereSatzbau } = await import("./satzbau.js");
            if (!inhalt.isConnected) return;
            rendereSatzbau(lektion.text, inhalt);
          } else if (modul === "hoerverstehen") {
            const { rendereHoerverstehen } = await import("./hoerverstehen.js");
            if (!inhalt.isConnected) return;
            rendereHoerverstehen(lektion.text, inhalt);
          } else if (modul === "aussprache") {
            const { rendereAussprache } = await import("./aussprache.js");
            if (!inhalt.isConnected) return;
            rendereAussprache(lektion.text, inhalt);
          }
        } catch (fehler) {
          if (!inhalt.isConnected) return;
          inhalt.innerHTML = `<p>Übung konnte nicht geladen werden: ${fehler.message}</p>`;
        }
      });
    });
  }
}
