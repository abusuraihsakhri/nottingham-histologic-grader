(function (root) {
  "use strict";
  function score(v, label) {
    if (v === null || v === undefined || typeof v === "boolean" || String(v).trim() === "") {
      throw new Error(label + " must be 1, 2 or 3.");
    }
    var raw = String(v).trim();
    if (!/^[123](?:\\.0+)?$/.test(raw)) throw new Error(label + " must be 1, 2 or 3.");
    var n = Number(raw);
    if (!Number.isInteger(n) || n < 1 || n > 3) {
      throw new Error(label + " must be 1, 2 or 3.");
    }
    return n;
  }
  function grade(v1, v2, v3) {
    var a = score(v1, "Tubule formation");
    var b = score(v2, "Nuclear pleomorphism");
    var c = score(v3, "Mitotic activity");
    var total = a + b + c;
    var level = total <= 5 ? 1 : (total <= 7 ? 2 : 3);
    return { score: total, grade: level, classification: [
      "", "Well differentiated", "Moderately differentiated", "Poorly differentiated"
    ][level] };
  }
  var api = { grade: grade };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  root.NottinghamCore = api;
})(typeof window !== "undefined" ? window : globalThis);
