"""Backward-compatible Figure 13 entry point."""
from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_spec = spec_from_file_location("render_f13", Path(__file__).with_name("render_f13.py"))
_mod = module_from_spec(_spec)
_spec.loader.exec_module(_mod)
main = _mod.main

if __name__ == "__main__":
    main()
