import { ladeLektionsListe, ladeFortschritt, rendereLektionsGrid } from "./app.js";
import { exportiereFortschritt, importiereFortschritt } from "./fortschritt.js";

const lektionen = await ladeLektionsListe();
const fortschritt = ladeFortschritt();
rendereLektionsGrid(lektionen, fortschritt, document.getElementById("lektion-grid"));

document.getElementById("export-btn").addEventListener("click", exportiereFortschritt);
document.getElementById("import-input").addEventListener("change", async (e) => {
  const datei = e.target.files[0];
  if (!datei) return;
  if (!confirm("Aktuellen Fortschritt mit der importierten Datei überschreiben?")) return;
  await importiereFortschritt(datei);
  location.reload();
});
