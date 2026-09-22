"""Rendering ASCII di un Behaviour Tree (per debug e CLI)."""

from __future__ import annotations

from simai.npc.ai.bt.base import BTNode


def render_tree(node: BTNode, indent: int = 0) -> str:
    """Rende il tree in formato ASCII indentato (2 spazi per livello)."""
    prefix = "  " * indent
    lines = [f"{prefix}{node!r}"]
    for child in node.child_nodes():
        lines.append(render_tree(child, indent + 1))
    return "\n".join(lines)


__all__ = ["render_tree"]
