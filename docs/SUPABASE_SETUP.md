# CF-0 — optional Supabase project setup

**Scope:** `whoiwts110217-creator/CF-0` repository root. The existing Spider / Millennium Puzzle remains an offline, browser-first application. Supabase is optional; nothing in Spider is redirected to a hosted database.

## Status and prerequisites

At the November 14, 2026 inspection, the public `main` branch had **no** `package.json`, npm lockfile, or `supabase/config.toml`. This change adds a minimal `package.json` with the Supabase CLI as an **exact, project-local dev dependency**, and a Windows setup script. It does **not** claim an installed CLI, installed agent plugin, initialized database, or Supabase account. Those require running the commands in a checked-out project with network access.

Required: Windows with Node.js 20+, npm, npx, internet access, sufficient free disk space, and (for the agent plugin) a supported local AI coding agent. **Do not run `supabase start` on the low-RAM CF-0 HP by default.** Supabase documentation recommends at least 7 GB RAM for the full local Docker stack; initial setup does not need Docker.

## One action on the Windows HP

From the root of an updated CF-0 checkout, double-click `SETUP_SUPABASE_CF0.cmd`, or run it in Command Prompt:

```bat
cd /d C:\path\to\CF-0
SETUP_SUPABASE_CF0.cmd
```

The script runs the requested operations, with `--save-exact` to pin the CLI version and `--yes` to avoid an interactive plugin confirmation:

```bat
npm install supabase --save-dev --save-exact
npx plugins add supabase-community/supabase-plugin --yes
```

It then checks `supabase/config.toml` before calling `npx supabase init`. If that file already exists, it is preserved. A plugin-install failure is reported separately; it does not prevent the local CLI from being initialized.

The lockfile is created by `npm install` **on the actual machine**, not fabricated in this repository. Keep and commit `package-lock.json`, `supabase/config.toml`, and any agent config files that are appropriate for public sharing. Do not commit secrets.

## Verify the result

```bat
npx supabase --version
if exist supabase\config.toml echo SUPABASE_INITIALIZED
git status --short
```

The Supabase agent plugin is installed into detected AI coding-agent environments. It is a separate installation from the npm dev dependency. An AI agent may need a restart and Supabase browser authorization before its MCP tools become available.

## Relevant next steps for Spider

1. **First decide the purpose.** Keep the puzzle's source, code pieces, tests, and local evidence offline. Consider Supabase only for optional public-safe project status, a collaborative issue/parts inventory, or a small opt-in cross-device sync service.
2. **Create and link a hosted Supabase project only if needed.** In the browser, create a project you control; then use `npx supabase login` and `npx supabase link --project-ref YOUR_PROJECT_REF`. Neither action is completed by the setup script.
3. **Start with a small migration and RLS.** For anything public-facing, design tables and row-level security before storing data. Never put service-role keys or private contacts in the public website, repo, or browser bundle.
4. **Avoid a local full-stack start on the 4 GB HP.** The Supabase CLI itself can manage a remote project without running the entire Docker development stack on this computer.
5. **Verify before calling the setup complete.** The acceptance gates are CLI version output, the presence of `supabase/config.toml`, agent plugin availability if an agent is installed, and a clean review of generated files.

Official documentation: https://supabase.com/docs/guides/local-development/cli/getting-started and https://supabase.com/docs/guides/ai-tools/plugins .
