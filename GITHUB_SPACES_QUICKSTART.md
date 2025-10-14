# GitHub Spaces Quickstart

Use this cheat sheet to wire up a GitHub Space for the DatingApp project and get Copilot answering with the right context in under five minutes.

## 1. Connect VS Code to your Space
1. Install the **GitHub Copilot** and **GitHub Spaces** extensions (already done).
2. Press `Ctrl+Shift+P` / `Cmd+Shift+P` and run **"GitHub Copilot: Connect to Space…"**.
3. Pick an existing Space or paste the invite link.
4. Sign in with the same GitHub account that has repo access.

> ✅ Once connected you should see the Space name in the Copilot side panel and a contextual history timeline.

## 2. Share essential project context
Drag these files into the Space context pane or drop them directly into a thread so Copilot can read them during the session:

- `AI_CONTEXT.md` – architecture, tech stack, migrations, next steps
- `API_DOCUMENTATION.md` – endpoints and request/response contracts
- `TROUBLESHOOTING.md` – runbook for common failures
- `GITHUB_SPACES_QUICKSTART.md` (this file) – setup reminders
- Any active diff or log snippet you want help with (`git diff`, test output, etc.)

Tip: select text in VS Code → right-click → **"Add to Copilot Context"** to push only the relevant chunk.

## 3. Start a task-focused thread
1. In the Space, click **New Thread** → give it a short goal (e.g., "Migrate UserService to PostgreSQL").
2. Paste a snapshot of the current state (errors, TODOs, or diff summary).
3. Ask for the outcome explicitly: _"Implement the new connection string in `UserService/appsettings.json` and update `Program.cs` to use Keycloak."_

Copilot will now respond using the shared context and preserve the full conversation history for later.

## 4. Validate changes from VS Code
After Copilot suggests changes, run quick checks and feed the results back into the thread:

```bash
cd /home/m/development/DatingApp
# example validation
dotnet build UserService/UserService.csproj
```

Attach the command output if something fails so Copilot can iterate.

## 5. Capture hand-off notes
Before ending the session, add a short summary message or drop a Markdown note (see `notes/` folder suggestion below) covering:

- What changed
- Remaining TODOs with file paths
- Any failing tests or blocked items

This becomes the entry point next time you or a teammate open the Space.

---

### Optional: notes folder template
Create a `notes/` folder and keep small Markdown files like `notes/2025-10-10-keycloak.md`. Drag the relevant note into the Space; it keeps history tidy and makes it easy to revive context later.

Happy collaborating! Let me know when you want to wire the next workflow (e.g., automated checks or shared snippets).
