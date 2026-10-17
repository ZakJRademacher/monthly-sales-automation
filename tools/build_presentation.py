"""Compatibility entry point for the generated sales briefing."""

from build_briefing import ROOT, build

if __name__ == "__main__":
    print(build(ROOT / "evidence", ROOT / "deliverables"))
