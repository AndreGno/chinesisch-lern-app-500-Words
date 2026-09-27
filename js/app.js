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
