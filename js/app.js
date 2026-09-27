export async function ladeLektionsListe() {
  const nummern = Array.from({ length: 30 }, (_, i) => i + 1);
  const lektionen = await Promise.all(
    nummern.map(async (n) => {
      const id = String(n).padStart(2, "0");
      const res = await fetch(`data/lektion-${id}.json`);
      return res.json();
    })
  );
  return lektionen;
}

export async function ladeLektion(nummer) {
  const id = String(nummer).padStart(2, "0");
  const res = await fetch(`data/lektion-${id}.json`);
  if (!res.ok) throw new Error(`Lektion ${nummer} nicht gefunden`);
  return res.json();
}

export function ladeFortschritt() {
  try {
    return JSON.parse(localStorage.getItem("fortschritt") || "{}");
  } catch {
    return {};
  }
}

export function rendereLektionsGrid(lektionen, fortschritt, container) {
  container.innerHTML = "";
  for (const lektion of lektionen) {
    const gelernt = fortschritt[`lektion-${lektion.nummer}`]?.gelesenAnteil ?? 0;
    const a = document.createElement("a");
    a.href = `lektion.html?id=${lektion.nummer}`;
    a.className = "lektion-karte";
    a.innerHTML = `
      <p class="zh">第${lektion.nummer}課</p>
      <p class="de">${lektion.text[0]?.de ?? ""}</p>
      <div class="fortschritt-balken"><span style="width:${gelernt * 100}%"></span></div>
    `;
    container.appendChild(a);
  }
}
