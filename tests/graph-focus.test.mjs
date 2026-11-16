import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { indexGraph, connections } from "../site/graph-model.mjs";
import {
  focusGroups,
  bridgePaths,
  validTrail,
  findRecords,
} from "../site/graph-focus.mjs";
const graph = JSON.parse(
    readFileSync(new URL("../site/data/graph.json", import.meta.url)),
  ),
  index = indexGraph(graph),
  bank = "pib:standard:PSU 905";
test("groups account for every documented connection and retain its direction and evidence ID", () => {
  const groups = focusGroups(index, bank),
    seen = [];
  for (const group of groups)
    for (const record of group.records) {
      assert.equal(record.node.type, group.type);
      for (const edge of record.edges) {
        assert.equal(edge.type, group.relation);
        assert.equal(group.outgoing, edge.source === bank);
        assert.equal(
          group.outgoing ? edge.target : edge.source,
          record.node.id,
        );
        seen.push(edge.id);
      }
    }
  assert.deepEqual(
    seen.sort(),
    connections(index, bank)
      .map((e) => e.id)
      .sort(),
  );
  assert.ok(groups.some((g) => g.type === "pia" && !g.outgoing));
  assert.ok(groups.every((g) => !["category", "pib_type"].includes(g.type)));
});
test("suggested paths are real resolved two-step citations, with no invented direct link or generic shared-owner shortcut", () => {
  const paths = bridgePaths(index, bank, 6);
  assert.ok(paths.length);
  const neighbors = new Set(
    connections(index, bank).map((e) =>
      e.source === bank ? e.target : e.source,
    ),
  );
  for (const path of paths) {
    assert.ok(!neighbors.has(path.target));
    assert.notEqual(path.target, bank);
    assert.equal(path.edges.length, 2);
    for (const [i, eid] of path.edges.entries()) {
      const e = index.edges.get(eid),
        a = i ? path.via : bank,
        b = i ? path.target : path.via;
      assert.ok(
        (e.source === a && e.target === b) ||
          (e.source === b && e.target === a),
      );
      assert.equal(e.resolution, "resolved");
      assert.notEqual(e.type, "listed_by");
    }
  }
  assert.deepEqual(bridgePaths(index, bank, 6), paths);
});
test("a shared institution alone cannot produce a recommended evidence path", () => {
  const g = indexGraph({
    nodes: [
      { id: "a", type: "pib" },
      { id: "org", type: "institution" },
      { id: "b", type: "pib" },
    ],
    edges: [
      {
        id: "1",
        source: "a",
        target: "org",
        type: "listed_by",
        resolution: "resolved",
      },
      {
        id: "2",
        source: "b",
        target: "org",
        type: "listed_by",
        resolution: "resolved",
      },
    ],
  });
  assert.deepEqual(bridgePaths(g, "a"), []);
});
test("shared URLs preserve validated paths and reject unrelated breadcrumb steps", () => {
  const p = bridgePaths(index, bank)[0];
  assert.deepEqual(validTrail(index, [bank, p.via, p.target], p.target), [
    bank,
    p.via,
    p.target,
  ]);
  assert.deepEqual(
    validTrail(index, ["missing", "institution:made-up"], bank),
    [bank],
  );
  const unrelated = graph.nodes.find(
    (n) =>
      n.id !== bank &&
      !connections(index, bank).some(
        (e) => e.source === n.id || e.target === n.id,
      ),
  );
  assert.deepEqual(validTrail(index, [bank, unrelated.id], unrelated.id), [
    unrelated.id,
  ]);
});
test("one search supports bilingual identifiers, type words and named entities", () => {
  assert.ok(findRecords(index, "FRP 905", "fr").some((n) => n.id === bank));
  assert.ok(findRecords(index, "POU 905").some((n) => n.id === bank));
  assert.ok(findRecords(index, "PIA").every((n) => n.type === "pia"));
  assert.equal(findRecords(index, "zz-no-record-here").length, 0);
});
