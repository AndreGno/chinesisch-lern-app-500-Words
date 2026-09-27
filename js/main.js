import { ladeLektionsListe, ladeFortschritt, rendereLektionsGrid } from "./app.js";

const lektionen = await ladeLektionsListe();
const fortschritt = ladeFortschritt();
rendereLektionsGrid(lektionen, fortschritt, document.getElementById("lektion-grid"));
