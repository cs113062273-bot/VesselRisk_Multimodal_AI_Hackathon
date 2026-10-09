# Project instructions

## Desktop-only UI — explicit user directive, 2026-10-09

- This project targets desktop browsers only.
- Never develop, edit, optimize, or test a mobile interface. Do not add mobile-specific styles, navigation, auto-scrolling, viewport tests, or screenshots. This applies to all future work unless the user explicitly changes this directive.
- Validate frontend changes using desktop browser sizes only.
- Do not reintroduce the removed `View explanation`, `Edit inputs`, or `Back to heart & results` shortcuts. Selecting a target already updates the visible explanation panel.
- Do not reintroduce the three vessel-selector cards below the heart. The anatomical labels, viewer target selector and explanation tabs already select the corresponding artery.
- Keep the four probabilities in the explanation tabs. Do not restore separate probability cards above the heart; the viewer target dropdown and explanation tabs stay synchronized.
- Do not automatically scroll or move focus after a prediction.
- Keep the patient field scroll area spacious. Do not shrink it to fit the prediction footer into the first screen on shorter desktop windows; the page may scroll to reach the footer.

- Do not restore the prediction-status strip beneath the heart. Auto-orbit runs on the first workspace opening only; selecting a target or returning from Evidence Lab must not restart it.

Read the Next.js instructions in `web/AGENTS.md` when changing frontend code.
