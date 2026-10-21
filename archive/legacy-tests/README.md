# Legacy test source

These two files are preserved from the supplied project directory. They refer to `swarm` and `knowledge.milvus_kb`, neither of which is present in the supplied source. They cannot verify the current `src/` and `apps/` implementation.

The original `python -m pytest -q` stopped during collection with `ModuleNotFoundError: No module named 'knowledge'`. The `swarm` import test also references a missing module. The files were moved here, without changing their contents, and given `.py.txt` extensions to preserve the old tests without advertising missing implementations as current features.

Restore the corresponding source modules and move these files back to `tests/` with `.py` extensions before claiming legacy swarm/Milvus functionality. No replacement implementation or passing legacy-test result is claimed.
