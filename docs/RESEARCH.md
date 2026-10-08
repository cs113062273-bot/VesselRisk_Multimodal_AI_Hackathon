# What prior successful submissions demonstrated

Research performed against public primary materials on 2026-10-02. This is design calibration, not proof that a particular feature causes a win.

- [Organizer's winner announcement](https://www.linkedin.com/posts/ihubiitmandi_multimodalai-hackathon-iitmandi-activity-7406989681428656128-irXj) identifies Smart Scribe / Ult4 as first and Yoga Maya / Dropout Society as fifth. Team/project names vary between the announcement and repositories.
- [Smart Scribes repository](https://github.com/Kartavya728/Smart-Scribes) exposes a full Python-to-Next.js workflow, an architecture image and demo/install/documentation links. Its [15-slide presentation](https://drive.google.com/file/d/1ddnYoN5SRydPX6gg-2T6K_LbyNhOXlyg/view) was downloaded and read, including annotated role-specific application screenshots. The [demo](https://youtu.be/DzG_FQJkbAA) is public; its playback/transcript was not independently reviewed. Current repository contents are not a verified competition-time snapshot. Survey percentages in the deck are author claims, not independently audited results.
- [YogMaya repository](https://github.com/Aman071106/dropout_society) contains interface imagery, screen recordings, install instructions and a [demo link](https://youtu.be/mdsIb63s6k0). Its README reports pose matching and latency measurements; those benchmarks were not reproduced. Its public dashboard diagram includes planned features, so breadth should not be confused with implemented completeness.

Applied lessons: show a concrete user journey, connect inputs to visible output, present measured evidence with scope, expose reproducibility and package the final demo/report together. VesselRisk uses independent coronary anatomy and clinical validation; it reuses none of these projects' code, branding, screenshots or claimed metrics. No chatbot/authentication feature was added just because prior entries had one.

Technical references consulted:

- [Official UCI dataset and license](https://archive.ics.uci.edu/dataset/411/extention+of+z+alizadeh+sani+dataset), DOI 10.24432/C5461K.
- [Nested CV guidance](https://scikit-learn.org/stable/auto_examples/model_selection/plot_nested_cross_validation_iris.html).
- [Probability calibration guidance](https://scikit-learn.org/stable/modules/calibration.html), including the small-sample limitations of isotonic regression.
- [SHAP API](https://shap.readthedocs.io/en/latest/generated/shap.Explainer.html).
- [Threshold tuning guidance](https://scikit-learn.org/1.7/modules/classification_threshold.html): tune within training data; do not reuse the classifier's fitting data as a threshold validation set.
- [Model persistence compatibility](https://scikit-learn.org/1.7/model_persistence.html): persisted sklearn artifacts require their training environment; startup now checks the registry version before loading.
- [Official BodyParts3D license](https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html), CC BY 4.0; [geometry derivative](https://github.com/ashemag/human-atlas/tree/1c38bf35c254a891200d3cedecfd57abebe83d8d).

The supplied Track A.pdf is the official implementation authority. The workbook, not an internet summary, determines the actual labels and schema.

Final audit: [Model optimization literature review](MODEL_OPTIMIZATION_RESEARCH.md) compares the 2020 same-cohort vessel study, the 2018 500-patient study, ALEC, and primary methodology references without equating incompatible results. [Completed results](FINAL_AUDIT_RESULTS.md) report the additional predeclared elastic-net/histogram/CatBoost batch, negative primary verdict and unconfirmed RCA shrinkage lead. The prior-winner slide deck was re-read in full; video playback remains unreviewed.
