#!/usr/bin/env python3
"""Export the My Info MCP tool metadata and JSON Schemas for review."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from my_info.agent_tools import get_manifest
from my_info.mcp_server import SERVER_INSTRUCTIONS, mcp


OUTPUT_PATH = ROOT / "data/derived/my_info/my_info_mcp_tools.json"


async def build_export() -> dict[str, object]:
    tools = await mcp.list_tools()
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "server": {
            "name": mcp.name,
            "title": mcp.title,
            "version": mcp.version,
            "instructions": SERVER_INSTRUCTIONS,
        },
        "manifest": get_manifest(),
        "tools": [
            tool.model_dump(by_alias=True, exclude_none=True)
            for tool in sorted(tools, key=lambda item: item.name)
        ],
    }


def main() -> None:
    output = asyncio.run(build_export())
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(output['tools'])} MCP tool schemas to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
