(function (root) {
  "use strict";
  function parse(text) {
    var rows = [], row = [], cell = "", quoted = false;
    for (var i = 0; i < text.length; i++) {
      var ch = text[i];
      if (quoted) {
        if (ch === '"' && text[i + 1] === '"') { cell += '"'; i++; }
        else if (ch === '"') quoted = false;
        else cell += ch;
      } else if (ch === '"' && cell === "") quoted = true;
      else if (ch === ",") { row.push(cell); cell = ""; }
      else if (ch === "\n" || ch === "\r") {
        if (ch === "\r" && text[i + 1] === "\n") i++;
        row.push(cell);
        if (row.some(function (v) { return v !== ""; })) rows.push(row);
        row = []; cell = "";
      } else if (ch === '"') throw new Error("Unexpected quote in CSV.");
      else cell += ch;
    }
    if (quoted) throw new Error("Unclosed quote in CSV.");
    row.push(cell);
    if (row.some(function (v) { return v !== ""; })) rows.push(row);
    return rows;
  }
  function assess(text) {
    var rows = parse(text.replace(/^\uFEFF/, ""));
    if (rows.length < 2) throw new Error("CSV requires a header and at least one case.");
    if (rows.length > 5001) throw new Error("Maximum 5,000 cases per file.");
    var headers = rows.shift().map(function (v) { return v.trim(); });
    if (new Set(headers).size !== headers.length) throw new Error("Duplicate CSV headers.");
    var indexes = ["v1", "v2", "v3"].map(function (h) { return headers.indexOf(h); });
    if (indexes.some(function (x) { return x < 0; })) {
      throw new Error("CSV must contain v1,v2,v3 columns (component scores).");
    }
    return rows.map(function (row, i) {
      if (row.length !== headers.length) throw new Error("CSV case " + (i + 2) + ": column count mismatch.");
      try {
        var g = root.NottinghamCore.grade.apply(null, indexes.map(function (n) { return row[n]; }));
        return { case_id: headers.includes("case_id") ? row[headers.indexOf("case_id")] : "Case " + (i + 1),
          v1: row[indexes[0]], v2: row[indexes[1]], v3: row[indexes[2]],
          score: g.score, grade: g.grade, classification: g.classification };
      } catch (err) { throw new Error("CSV row " + (i + 2) + ": " + err.message); }
    });
  }
  function csvCell(value) {
    var s = String(value);
    if (/^\s*[=+@-]/.test(s)) s = "'" + s;
    return '"' + s.replace(/"/g, '""') + '"';
  }
  function exportCsv(rows) {
    var keys = ["case_id", "v1", "v2", "v3", "score", "grade", "classification"];
    return [keys.join(",")].concat(rows.map(function (row) {
      return keys.map(function (key) { return csvCell(row[key]); }).join(",");
    })).join("\r\n") + "\r\n";
  }
  var api = {parse:parse, assess:assess, exportCsv:exportCsv};
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  root.NottinghamBatch = api;
})(typeof window !== "undefined" ? window : globalThis);
