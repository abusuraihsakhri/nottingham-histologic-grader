const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const core = require("../web/core.js");
const batch = require("../web/batch.js");

test("all Nottingham boundary scores", () => {
  [[1,1,1,3,1],[1,2,2,5,1],[2,2,2,6,2],
   [2,2,3,7,2],[2,3,3,8,3],[3,3,3,9,3]].forEach(v => {
    const actual = core.grade(v[0],v[1],v[2]);
    assert.equal(actual.score,v[3]); assert.equal(actual.grade,v[4]);
  });
});
test("reject invalid, incomplete and non-numeric component scores", () => {
  ["",null,"banana",0,4,1.5,Infinity,NaN].forEach(v => {
    assert.throws(() => core.grade(v,1,2));
  });
});
test("decimal-form integer component scores", () => {
  assert.equal(core.grade("1.0","2.00","3").score,6);
  assert.throws(() => core.grade(true,1,1));
  assert.throws(() => core.grade("0x1",1,1));
});
test("batch grading handles BOM, quoted fields, and malicious CSV labels", () => {
  const rows = batch.assess('\uFEFFcase_id,v1,v2,v3\r\n"CASE, A",1,2,3\r\n"=2+2",3,3,3\r\n');
  assert.equal(rows.length,2);
  assert.equal(rows[0].case_id,"CASE, A");
  assert.equal(rows[0].grade,2);
  assert.equal(rows[1].grade,3);
  const csv=batch.exportCsv(rows);
  assert.match(csv, /"'=2\+2"/);
  assert.equal(batch.parse(csv)[1][0],"CASE, A");
});
test("batch rejects malformed data", () => {
  assert.throws(() => batch.assess("case_id,v1,v2,v3\nONE,1,1,4"));
  assert.throws(() => batch.assess("x,y,z\n1,2,3"));
  assert.throws(() => batch.assess("v1,v2,v3\n1,2"));
});
test("static site references only existing local JS and CSS assets", () => {
  const html=fs.readFileSync(path.join(__dirname,"../web/index.html"),"utf8");
  ["./core.js","./batch.js","./app.js","./style.css"].forEach(ref=>{
    assert.ok(html.includes(ref));
    assert.ok(fs.existsSync(path.join(__dirname,"../web",ref)));
  });
  assert.ok(!html.includes("fetch('/api/audit'"));
});
