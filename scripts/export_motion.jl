# Read a saved result using PMS's own reconstruction code. No HDF5 dependency
# is required in Blender, and body-reference/CM conventions stay owned by PMS.
length(ARGS) == 3 || error("usage: export_motion.jl PMS_ROOT INPUT.simp OUTPUT.json")
pms_root, input, output = abspath.(ARGS)
include(joinpath(pms_root, "src", "viewer", "ResultGraphicsWriter.jl"))
stored = read_result(input)
stored.status == :complete || error("Only completed results are accepted")
stored.analysis_mode in (:dynamic, :kinematic) || error("Expected a motion result")
reconstructed = reconstructed_viewer_results(input)
write_viewer_document(output, reconstructed.results;
    labels = reconstructed.labels,
    choice_name = reconstructed.choice_name,
    include_signals = false)
println("Exported reference-frame motion to ", output)
