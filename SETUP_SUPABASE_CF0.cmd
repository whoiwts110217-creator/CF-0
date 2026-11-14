@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo [CF-0] Supabase optional project setup
echo [CF-0] Working directory: %CD%
where node >nul 2>&1
if errorlevel 1 goto :need_node
where npm >nul 2>&1
if errorlevel 1 goto :need_node
where npx >nul 2>&1
if errorlevel 1 goto :need_node
for /f "delims=" %%V in ('node -p "process.versions.node.split('.')[0]"') do set "NODE_MAJOR=%%V"
if not defined NODE_MAJOR goto :need_node
if %NODE_MAJOR% LSS 20 goto :need_node
if not exist package.json (
  echo ERROR: CF-0 package.json missing. Run from the CF-0 checkout.
  exit /b 1
)

echo [1/4] Installing Supabase CLI as an EXACT project dev dependency...
call npm install supabase --save-dev --save-exact
if errorlevel 1 goto :failed

echo [2/4] Installing the Supabase agent plugin into detected AI agents...
set "PLUGIN_FAILED="
call npx plugins add supabase-community/supabase-plugin --yes
if errorlevel 1 (
  set "PLUGIN_FAILED=1"
  echo WARNING: Plugin installation failed or no supported AI agent was detected.
  echo Continue with CLI setup. You can retry the plugin command separately.
)

echo [3/4] Checking Supabase initialization...
if exist "supabase\config.toml" (
  echo Supabase configuration already exists; keeping it unchanged.
) else (
  call npx supabase init
  if errorlevel 1 goto :failed
)

echo [4/4] Checking installed CLI version...
call npx --no-install supabase --version
if errorlevel 1 goto :failed

echo.
echo CF-0 CLI setup and Supabase initialization finished.
if defined PLUGIN_FAILED echo WARNING: Plugin installation was NOT verified. Retry after reviewing agent setup.
echo Review changes with git status; commit package-lock.json and supabase/config.toml when ready.
echo Do NOT commit database passwords, access tokens, or private contacts.
echo Local Supabase containers were NOT started (high RAM requirement).
exit /b 0

:need_node
echo ERROR: Node.js 20+ with npm and npx is required.
exit /b 1

:failed
echo ERROR: Setup stopped. Review the command failure above. Existing files were not intentionally reset.
exit /b 1
