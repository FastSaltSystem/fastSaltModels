# Stacked absorber module illustration

This standalone presentation prop shows the requested ordering: surge tank below pressure tank, with a control box above both. Proportions are arbitrary and unitless. No volumes, dimensions, vessel internals, valve details or process routing are represented. Short exterior connection stubs indicate interfaces only; they do not define which equipment is connected internally.

[Blender model](../outputs/absorber-stack-illustration/absorber-stack.blend) and [render](../outputs/absorber-stack-illustration/absorber-stack.png).

Build from the repository root:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --python-exit-code 1 --python scripts/build_absorber_stack_illustration.py
```

The builder creates a new scene and leaves all existing reactor and site scenes untouched. The image and Blender file are ignored working outputs. This illustration does not supersede the engineering model or the Michigan team's analysis.
