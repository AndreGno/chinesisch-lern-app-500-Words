import { ladeLektion } from "./app.js";
import { rendereTabs, rendereTabInhalt } from "./lektion.js";

const params = new URLSearchParams(location.search);
const nummer = Number(params.get("id")) || 1;
const lektion = await ladeLektion(nummer);

document.getElementById("lektion-titel").textContent =
  `第${lektion.nummer}課 — ${lektion.text[0]?.de ?? ""}`;

const inhaltEl = document.getElementById("tab-inhalt");
rendereTabs(lektion, document.getElementById("tabs"), (tabKey) =>
  rendereTabInhalt(lektion, tabKey, inhaltEl)
);
rendereTabInhalt(lektion, "text", inhaltEl);
