# Technical references

These sources support the dataset, validation procedure, explanation method, and anatomical assets used by VesselRisk.

- **Competition:** [official rules](https://multimodal-ai-hackathon-2026-7.devpost.com/rules) and [Track A specification](https://drive.google.com/file/d/1T9Whog4kWF3mYB7ZMGyihGWpbJBJtsfz/view).
- **Dataset:** [UCI Extension of Z-Alizadeh Sani](https://archive.ics.uci.edu/dataset/411/extention+of+z+alizadeh+sani+dataset), DOI [10.24432/C5461K](https://doi.org/10.24432/C5461K). The original workbook supplies the labels and input definitions.
- **Nested validation:** [scikit-learn nested cross-validation example](https://scikit-learn.org/stable/auto_examples/model_selection/plot_nested_cross_validation_iris.html). Model selection belongs inside the training partitions.
- **Calibration:** [scikit-learn probability calibration](https://scikit-learn.org/stable/modules/calibration.html). Sigmoid calibration is fitted inside training partitions; raw and isotonic scores are reported as comparisons.
- **Thresholds:** [scikit-learn threshold tuning](https://scikit-learn.org/1.7/modules/classification_threshold.html). Research thresholds use training data and are evaluated separately from the fixed 0.50 results.
- **SHAP:** [PermutationExplainer documentation](https://shap.readthedocs.io/en/latest/generated/shap.PermutationExplainer.html). VesselRisk explains the selected model's calibrated probability using training-only background patients.
- **Saved models:** [scikit-learn model persistence](https://scikit-learn.org/1.7/model_persistence.html). The pinned environment and startup compatibility checks prevent loading models with an incompatible scikit-learn version.
- **Anatomy:** [BodyParts3D license](https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html), [BodyParts3D paper](https://doi.org/10.1093/nar/gkn613), and the [pinned human-atlas geometry revision](https://github.com/ashemag/human-atlas/tree/1c38bf35c254a891200d3cedecfd57abebe83d8d). Source mesh IDs and transformations are recorded in the anatomy manifest.

The measured results are in `ml/artifacts/evidence.json`. The report and Model evidence display these records rather than values copied from published studies.
