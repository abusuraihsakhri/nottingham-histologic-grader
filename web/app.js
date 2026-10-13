(function () {
  "use strict";
  var $ = function (id) { return document.getElementById(id); };
  var scored = [];
  function node(tag, text, cls) {
    var el = document.createElement(tag);
    el.textContent = text;
    if (cls) el.className = cls;
    return el;
  }
  function download(filename, content) {
    var object = URL.createObjectURL(new Blob([content], {type:"text/csv;charset=utf-8"}));
    var link = document.createElement("a");
    link.href = object; link.download = filename;
    document.body.appendChild(link); link.click(); link.remove();
    setTimeout(function () { URL.revokeObjectURL(object); }, 1000);
  }
  $("grade-form").addEventListener("submit", function (event) {
    event.preventDefault();
    var result = $("result");
    try {
      var g = NottinghamCore.grade($("v1").value, $("v2").value, $("v3").value);
      var fragment = document.createDocumentFragment();
      fragment.appendChild(node("span", $("case-id").value.trim() || "Single case", "tag"));
      fragment.appendChild(node("div", g.score + " / 9", "total"));
      fragment.appendChild(node("div", "Grade " + g.grade + " · " + g.classification, "grade"));
      fragment.appendChild(node("p", "Tubules " + $("v1").value + " + nuclei " +
        $("v2").value + " + mitoses " + $("v3").value, "help"));
      result.replaceChildren(fragment);
    } catch (error) {
      result.replaceChildren(node("p", error.message));
    }
  });
  $("sample").addEventListener("click", function () {
    download("nottingham_sample.csv",
      "case_id,v1,v2,v3\r\nCASE-001,1,1,1\r\nCASE-002,2,2,3\r\nCASE-003,3,3,3\r\n");
  });
  $("csv-file").addEventListener("change", async function () {
    scored = []; $("export").hidden = true; $("batch-table").hidden = true;
    $("batch-body").replaceChildren();
    $("batch-message").textContent = "";
    var file = this.files && this.files[0];
    if (!file) return;
    if (file.size > 2 * 1024 * 1024) {
      $("batch-message").textContent = "File exceeds the 2 MB limit.";
      return;
    }
    try {
      var content = await file.text();
      scored = NottinghamBatch.assess(content);
      var fragment = document.createDocumentFragment();
      scored.slice(0, 500).forEach(function (row) {
        var tr = document.createElement("tr");
        ["case_id", "v1", "v2", "v3", "score", "grade"].forEach(function (key) {
          tr.appendChild(node("td", row[key]));
        });
        fragment.appendChild(tr);
      });
      $("batch-body").appendChild(fragment);
      $("batch-table").hidden = false;
      $("export").hidden = false;
      $("batch-message").textContent = scored.length + " cases graded locally. " +
        (scored.length > 500 ? "Showing first 500; download includes all results." : "Ready to download.");
    } catch (error) {
      scored = [];
      $("batch-message").textContent = "Unable to grade CSV: " + error.message;
    }
  });
  $("export").addEventListener("click", function () {
    if (scored.length) download("nottingham_results.csv", NottinghamBatch.exportCsv(scored));
  });
})();
