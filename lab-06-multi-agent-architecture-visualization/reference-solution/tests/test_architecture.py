from pathlib import Path
import shutil

import pytest
from agents import Agent
from agents.extensions.visualization import draw_graph

from architecture import build_architecture
from export_diagram import export_diagram


def test_architecture_has_three_agents_and_exactly_two_handoffs():
    intake = build_architecture()
    assert isinstance(intake, Agent)
    assert intake.model == "gpt-6-luna"
    assert len(intake.handoffs) == 1
    research = intake.handoffs[0]
    assert isinstance(research, Agent)
    assert research.model == "gpt-6-luna"
    assert len(research.handoffs) == 1
    writer = research.handoffs[0]
    assert isinstance(writer, Agent)
    assert writer.model == "gpt-6-luna"
    assert writer.handoffs == []


def test_graph_source_contains_both_handover_edges():
    graph = draw_graph(build_architecture())
    assert '"Intake agent" -> "Research agent";' in graph.source
    assert '"Research agent" -> "Response writer";' in graph.source


@pytest.mark.skipif(shutil.which("dot") is None, reason="Graphviz dot executable is not installed")
def test_exporter_writes_png_signature(tmp_path: Path):
    output = export_diagram(tmp_path / "architecture.png")
    assert output.exists()
    assert output.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
