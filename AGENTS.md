# Project guidance

This repository owns Python geometry, Blender generation, and model-specific checks. The sibling `fastSalt` repository participates in the same Fast Salt System project and keeps its own Git history.

Start with [README.md](README.md), the relevant guide in `docs/`, and the sibling project's `STATUS.md` and `design/design-basis.md`.

- Keep the Python package name `textual_graphics`; the repository folder is `fastSaltModels`.
- Run Blender scripts from the repository root. Use file-relative paths so builds remain portable.
- Preserve `references/` and existing `baselines/`; create new snapshots for newly approved baselines.
- Generated working models and renders belong in ignored `outputs/`.
- Record geometry changes and their checks in the relevant model guide; update shared design/interface records when affected.
- Distinguish visual checks from structural, thermal, neutronics, or mass-property validation.
- Review and commit each repository separately. Do not discard unrelated changes.
