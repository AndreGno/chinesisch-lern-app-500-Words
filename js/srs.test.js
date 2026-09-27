import test from "node:test";
import assert from "node:assert/strict";
import { reviewCard, istFaellig } from "./srs.js";

test("erste korrekte Wiederholung setzt Intervall auf 1 Tag", () => {
  const karte = { interval: 0, repetitions: 0, easeFactor: 2.5 };
  const ergebnis = reviewCard(karte, 2);
  assert.equal(ergebnis.interval, 1);
  assert.equal(ergebnis.repetitions, 1);
});

test("zweite korrekte Wiederholung setzt Intervall auf 6 Tage", () => {
  const karte = { interval: 1, repetitions: 1, easeFactor: 2.5 };
  const ergebnis = reviewCard(karte, 2);
  assert.equal(ergebnis.interval, 6);
});

test("falsche Antwort setzt Wiederholungen zurueck", () => {
  const karte = { interval: 10, repetitions: 3, easeFactor: 2.5 };
  const ergebnis = reviewCard(karte, 0);
  assert.equal(ergebnis.repetitions, 0);
  assert.equal(ergebnis.interval, 1);
});

test("istFaellig erkennt ueberfaellige Karten", () => {
  assert.equal(istFaellig({ dueDate: "2020-01-01" }, "2026-01-01"), true);
  assert.equal(istFaellig({ dueDate: "2030-01-01" }, "2026-01-01"), false);
  assert.equal(istFaellig({}, "2026-01-01"), true);
});
