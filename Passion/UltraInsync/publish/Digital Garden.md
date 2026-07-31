---
dg-publish: true
---


> [!summary]
> Git Push ultrainsync.github.io repo will start GitHub workflow of serving GitHub Pages (with no-indexing business and tax folders)
> run `npm run build:adsvise` and put it inside `/on/` folder inside adsvise.me
> `npm run dev` will default to GitHub workflow (which is no-indexing `adsvise.me/on` blogpost)
> >[!info]
> > compare customized Digital Garden repo with main dev at `.tmp/digitalgarden`
> 
> >[!warning]
> > use `insert margin note + ;;` for sensitive information (it will omit from publishing it)

## Gripes
### Operon todo
![[embedding operon task (with its Id) dont show stylized checklist.png]]
- [x] graph on mobile only takes 75% of the full width. Make it fill all up instead
- [x] graph overlap file tree side column
- [x] using fingers zooming in and out of wack (the target point is off)
## Customizations (Divergence from Upstream)

### 1. Obsidian Plugin (`obsidian-digital-garden`)
We maintain a custom fork of the Obsidian plugin to enforce a strict security boundary for transclusions.
- **Why:** The upstream plugin blindly resolves all embeds, meaning if you embedded a private file inside a public file, the private file's contents would leak into the static site.
- **Our Fix:** Modified `src/compiler/GardenPageCompiler.ts` so that if an embedded file is not marked for publishing, it intercepts the embed and replaces it with a beautiful, natively-styled `Protected block` UI lock box.
- **Maintenance:** We bumped the version to `99.99.99` in `manifest.json` to prevent Obsidian from auto-overwriting it. If you ever want to update the plugin from upstream, you must pull from the main repo, re-apply the patch in `GardenPageCompiler.ts`, build with `npm run build`, and copy `main.js` and `manifest.json` back to your `.obsidian/plugins/digitalgarden` folder.

### 2. Static Site Template (`ultrainsync.github.io`)
When pulling updates from `https://github.com/oleeskild/digitalgarden`, be aware of the following local customizations we've made to support dual deployment (`ultrainsync.github.io` and `adsvise.me/on/`).

**Date:** July 26, 2026
**Conversation ID:** 902be4ad-e781-42a1-91d2-67c77defc3e7
**Haft Decisions:** `prob-20260725-a2fdb368`, `dec-20260725-27f791ac`

### Changes Made:
1. **`.eleventy.js`**: Added dynamic `pathPrefix` injection.
   - **What changed:** Appended `pathPrefix: process.env.PATH_PREFIX || "/",` to the returned configuration object at the end of the file.
   - **Why:** Allows Eleventy 3.0's HTML Base Plugin to automatically rewrite all `href` and `src` paths in the generated HTML based on the deployment target (e.g., prepending `/on/` for adsvise.me).
2. **`package.json`**: Added custom dev and build scripts.
   - **What changed:** Added `"build:adsvise": "cross-env PATH_PREFIX=/on/ npm-run-all get-theme build:sass build:eleventy"` and `"dev:adsvise": "cross-env PATH_PREFIX=/on/ npm-run-all get-theme build:sass --parallel watch:*"` to the `scripts` object.
   - **Why:** Used to build and preview the site targeting the subfolder deployment (Adsvise) with the correct `PATH_PREFIX` environment variable.
3. **`src/site/_data/meta.js` & `src/site/_includes/components/pageheader.njk`**: Added Conditional SEO NoIndex.
   - **What changed:** Exported `pathPrefix` in `meta.js` and added Jinja if-statements in `pageheader.njk` to inject `<meta name="robots" content="noindex, nofollow">`.
   - **Why:** Prevents duplicate content SEO penalties. Prime/Public rank on Github Pages; Profession/Passion rank on Adsvise.me.
4. **`src/helpers/filetreeUtils.js`**: Dynamic File Tree Hiding.
   - **What changed:** Intercepted the `getFileTree(data)` function to check the `note.filePathStem`. If `process.env.PATH_PREFIX === '/on/'` (Adsvise), it skips adding notes from `on/Prime` and `on/Public` to the tree. If it's Github Pages, it skips `on/Passion` and `on/Profession`.
   - **Why:** This hides the irrelevant folders from the left sidebar UI, while respecting the Obsidian Path Rewrite rules, and without needing to physically ignore files during Eleventy build (which would break search/graph).
5. **`.eleventy.js`**: Operon tag stripping and task transclusion (embeds).
   - **What changed:** Added custom `markdown-it` core rules near line 163. The `transclude_operon` rule intercepts `[[path#-operonId]]` wikilinks, synchronously fetches the target file from `src/site/notes/`, extracts the specific task by its `operonId`, and directly replaces the wikilink with the raw markdown task text. Then, `strip_operon` silently strips out `{{key:: value}}` metadata tags from the raw markdown.
   - **Why:** This replicates the Obsidian Operon plugin's behavior by turning dead anchor links into basic native checklists on your website, avoiding complex HTML wrappers and styling conflicts while keeping backend parameters hidden.
6. **`.eleventy.js`**: Internal Link `pathPrefix` fixing.
   - **What changed:** Added an `applyPathPrefix` helper and wrapped the `href` output of `getAnchorAttributes` to ensure it dynamically injects `process.env.PATH_PREFIX`.
   - **Why:** The built-in markdown renderer for Canvas and wikilinks bypassed Eleventy's `url` filter. When deployed to a subfolder (`/on/`), internal links in Canvas files were broken (pointing to the root `/` instead of `/on/`). This patch ensures internal links correctly respect the deployment prefix.
7. **`linkUtils.js` & `.eleventy.js`**: Link Graph standard wikilink extraction.
   - **What changed:** Updated `wikiLinkRegex` from `/\[\[(.*?\|.*?)\]\]/g` to `/\[\[(.*?)\]\]/g` across the parsing logic.
   - **Why:** Previously, only aliased wikilinks (with a pipe `|`) were registered as edges in the graph. This fix ensures standard wikilinks `[[Note]]` are accurately captured to populate the link graph.
8. **`graphScript.njk`**: Subfolder deployment path resolution for Link Graph.
   - **What changed:** Replaced the hardcoded `fetch('/graph.json')` with `fetch('{{ "/graph.json" | url }}')`, and updated `filterLocalGraphData` to strip `meta.pathPrefix` before performing node lookups.
   - **Why:** The frontend widget was attempting to fetch graph payloads from the root domain and failing to identify the active node when deployed to `/on/`. This ensures the link graph functions dynamically in subfolder deployments.
9. **`.eleventy.js`**: Optimized nested Canvas embeds.
   - **What changed:** Expanded the `canvas-markdown` build transform to intercept any `<iframe class="canvas-file-iframe">` embedding a nested `.canvas` file, swapping it out entirely at build-time with a lightweight blurred placeholder link (`<a class="canvas-placeholder">`).
   - **Why:** Recursively loading iframes for nested canvases causes massive performance drops and "flickering" UI bugs on the client side. A static placeholder eliminates DOM explosion, improves page load speeds, and boosts SEO while maintaining navigational UX.

### SOP: How to Safely Update the Template (Upstream Merges)
**CRITICAL**: DO NOT use the Obsidian Digital Garden plugin's "Update Template" button. It generates a PR that force-overwrites all customized files (like `.eleventy.js`, `.njk`, and `.scss`) back to the stock state, which will destroy our dual deployment, Operon transclusions, and custom SEO logic.

To safely update the template from [Upstream Tags](https://github.com/oleeskild/digitalgarden/tags):
1. **Fetch Upstream**: Ensure the upstream remote is tracked and fetch the latest tags via the terminal.
   ```bash
   git remote add upstream https://github.com/oleeskild/digitalgarden.git
   git fetch upstream --tags
   ```
2. **Merge the Tag**: Use Git to merge the specific release tag (e.g., `1.81.6`) into our main branch.
   ```bash
   git merge refs/tags/1.81.6
   ```
3. **Resolve Conflicts Carefully**: Git will successfully auto-merge core files we haven't touched. However, it will throw a merge conflict for files we have heavily customized. When resolving conflicts in these files, you must manually merge the code to ensure our custom logic remains intact while adopting the upstream dev's bug fixes:
   - **`.eleventy.js`**, **`package.json`**, and **`src/helpers/filetreeUtils.js`**: These contain logic vital for dual deployment (`PATH_PREFIX`).
   - **`pageheader.njk`**: Contains custom conditional SEO NoIndex logic.