"""Export the SDK handoff graph as a PNG without making an API request."""

import argparse
from pathlib import Path

from agents.extensions.visualization import draw_graph

from architecture import build_architecture

DEFAULT_OUTPUT = Path(__file__).resolve().parent / "outputs" / "multi-agent-handoffs.png"


def export_diagram(output: Path = DEFAULT_OUTPUT) -> Path:
    output = output.expanduser().resolve()
    if output.suffix.lower() != ".png":
        output = output.with_suffix(".png")
    output.parent.mkdir(parents=True, exist_ok=True)
    # Graphviz Source.render appends the selected format extension itself.
    prefix = output.with_suffix("")
    draw_graph(build_architecture(), filename=str(prefix))
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="PNG output path")
    args = parser.parse_args()
    print(export_diagram(args.output))


if __name__ == "__main__":
    main()
