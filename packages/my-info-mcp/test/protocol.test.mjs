import assert from "node:assert/strict";
import test from "node:test";

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { InMemoryTransport } from "@modelcontextprotocol/sdk/inMemory.js";

import { createServer, registerAll } from "../dist/server.mjs";

test("MCP discovery and structured manifest call work", async () => {
  const server = createServer();
  registerAll(server);
  const client = new Client({ name: "my-info-test", version: "1.0.0" });
  const [clientTransport, serverTransport] = InMemoryTransport.createLinkedPair();
  await Promise.all([server.connect(serverTransport), client.connect(clientTransport)]);
  try {
    const listed = await client.listTools();
    assert.deepEqual(
      listed.tools.map((tool) => tool.name).sort(),
      [
        "my_info_advance",
        "my_info_evaluate",
        "my_info_explain_result",
        "my_info_get_manifest"
      ]
    );
    for (const tool of listed.tools) {
      assert.equal(tool.annotations.readOnlyHint, true);
      assert.ok(tool.outputSchema);
    }
    const result = await client.callTool({ name: "my_info_get_manifest", arguments: {} });
    assert.equal(result.structuredContent.tool_api_version, "0.2.0");
    assert.equal(result.structuredContent.pib_count, 1028);
  } finally {
    await client.close();
    await server.close();
  }
});
