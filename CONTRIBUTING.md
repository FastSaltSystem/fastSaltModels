# Contributing model changes

Use a branch and a pull request for proposed changes to `main`. Public readers can suggest changes through issues or a pull request from a fork. Collaborators with Write access can push a branch in this repository.

1. Start from updated `main` and create a descriptive branch. Keep unrelated local changes separate.
2. Edit the Python definition and update the relevant guide in `docs/`.
3. Run the affected build and its meaningful geometry checks. Record prerequisites, assumptions and known limitations.
4. Inspect the changed views. Keep routine scenes and renders in ignored `outputs/`.
5. Include a few selected previews when they help review. For a deliberate snapshot, record the source revision and artifact hashes in a new dated directory.
6. Commit, push the branch, and open a pull request describing what changed, why, and how it was checked. Resolve review comments before merging.

Geometry checks establish only the claims they actually test. Preserve reference drawings, baseline files and author credits. Cross-component changes also need an interface or decision update in the [fastSalt hub](https://github.com/FastSaltSystem/fastSalt); open a separate linked pull request there.

For paired local clones and build entry points, see the [starting page](README.md). Project-wide source and calculation conventions are in [the hub contribution guide](https://github.com/FastSaltSystem/fastSalt/blob/main/CONTRIBUTING.md). Licensing choices remain pending; retain the original terms of referenced material.
