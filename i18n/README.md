# CF-0 public homepage languages

The public homepage is **English-first**. The optional small `🌐 EN` menu lets a visitor manually switch to Spanish (`es`), French (`fr`), or Portuguese (`pt`) without any popup, browser-language detection, geolocation, account creation, or third-party translation service.

- [English homepage](https://whoiwts110217-creator.github.io/CF-0/) — original source of truth.
- [Spanish](https://whoiwts110217-creator.github.io/CF-0/?lang=es), [French](https://whoiwts110217-creator.github.io/CF-0/?lang=fr), [Portuguese](https://whoiwts110217-creator.github.io/CF-0/?lang=pt) — explicit URL parameters. A valid choice is remembered locally in the visitor's browser.
- [Translation catalog and switcher](home.mjs) — the public homepage text catalog now includes 114 keyed English segments with corresponding Spanish, French, and Portuguese versions; the matching source test checks that every displayed text segment is covered. Names, code identifiers, GitHub links, and monetary amounts remain unchanged.
- [Coverage tests](home.test.mjs) — check English default, language menu and completeness, including disclaimers. Run `node --test i18n/home.test.mjs` before publishing.
- [Website deployment workflow](../.github/workflows/publish-website.yml) — publishes the catalog to GitHub Pages at `/CF-0/i18n/home.mjs` with no paid translation dependency.

**To add or edit a sentence:** update the literal English in [`index.html`](../index.html) and update the matching English key and all three translations in `COPY` in `home.mjs`. The English source remains visible without JavaScript. The test will fail if a newly visible text segment has not been translated. Avoid changing financial, legal or uncertainty disclosures without an accuracy check in each language. Do not translate owner names, identifiers or legal claims into claims of verified corporate or financial status.

**Scope:** This version translates the **public homepage**; the separate Mission Control technical application, GitHub source files and private archives remain in English. It must not claim multilingual support for those surfaces. Expansion should reuse the existing visitor language choice and independently test dynamic evidence labels without falsifying numeric data.

**Status:** First deployed on November 7, 2026; see the [GitHub Pages success](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42370884903). The user directed that English stay default and visitors choose translation only if they want it.

## November 9 · New public first-visit experience

The homepage now leads with the free Mission Control learning challenge and places honest source/test/unfinished-status explanation **before** the donation section. New texts are translated across all four supported homepage languages, and a PR test checks the free-first ordering, supporter/contributor credit distinction, in-page anchors and translation coverage. The secondary First Drop page remains English-first and is not claimed to be multilingual. No chat, payment, local HP, or browser executor permission changed.
