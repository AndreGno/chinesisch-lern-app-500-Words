const RELEVANTE_SCHLUESSEL = ["karteikarten-status", "fortschritt"];

export function exportiereFortschritt() {
  const daten = {};
  for (const schluessel of RELEVANTE_SCHLUESSEL) {
    const wert = localStorage.getItem(schluessel);
    if (wert) daten[schluessel] = JSON.parse(wert);
  }
  const blob = new Blob([JSON.stringify(daten, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  const heute = new Date().toISOString().slice(0, 10);
  a.href = url;
  a.download = `fortschritt-${heute}.json`;
  a.click();
  URL.revokeObjectURL(url);
}

export async function importiereFortschritt(datei) {
  const text = await datei.text();
  const daten = JSON.parse(text);
  for (const schluessel of RELEVANTE_SCHLUESSEL) {
    if (daten[schluessel]) {
      localStorage.setItem(schluessel, JSON.stringify(daten[schluessel]));
    }
  }
}
