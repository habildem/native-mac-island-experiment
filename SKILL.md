---
name: native-mac-island-experiment
description: Guide a user through the build-pinned native MenuBarAgent HUD experiment on macOS 27.3, including SIP explanation, startup debugging, verification, and rollback.
---

# Native Mac Island experiment

Treat this as a supervised experimental installation on the user's own Mac. Read README.md before acting. Never claim support from a version number alone. The manifest binary SHA-256 and loaded slice UUID must match. Source review and syntax checks are not runtime success.

## Workflow

1. Explain the current result and limits. Native HUD activation was confirmed by one user on an M2 Air running build 26C5035r. Relocation was visually confirmed. Click alignment is unresolved. Other machines, external displays, and persistence have not been validated.
2. Inspect `sw_vers`, `uname -m`, `csrutil status`, `xcrun --find lldb`, and the SHA-256 of `/System/Library/CoreServices/MenuBarAgent.app/Contents/MacOS/MenuBarAgent`. Compare to manifest.json. Stop before changing anything on a mismatch. Never guess replacement offsets or edit the manifest to suppress failure.
3. If SIP is enabled, explain the risks in README.md and let the user decide. The user performs Recovery and password entry. Do not claim to disable SIP from the running OS. Never request a password in chat. Do not disable AMFI, authenticated root, FileVault, or Gatekeeper.
4. Review startup_lldb.py. Compile-check Python. Resolve its absolute path on THIS machine. Never reuse the author's home directory, process ID, or object addresses.
5. Have the user execute `sudo launchctl debug gui/$(id -u)/com.apple.MenuBarAgent --start-suspended` in Terminal. If admin authorization is available through an approved local mechanism, follow the tool's permission rules. Explain that the next restart briefly interrupts the menu bar.
6. Run `launchctl kickstart -k gui/$(id -u)/com.apple.MenuBarAgent`, then `xcrun lldb -n MenuBarAgent`. Confirm the process is stopped at dyld startup. If attachment fails, recover the menu bar before further work.
7. Import the absolute path to startup_lldb.py using `command script import`. Inspect output. On validation errors, remove any created breakpoints, detach, and restart the service to clear partial state. Do not continue a partially installed experiment.
8. Run `continue`. Ask the user to inspect their existing music or Live Activity. Stop with Ctrl-C, print `startup_lldb.hits`. Both counts must be positive, and the user must confirm actual visible behavior. A hit counter alone is insufficient.
9. Run `breakpoint delete --force`, `process detach`, then `quit` in this dedicated debugger session. Verify the service is running. Do not leave MenuBarAgent suspended.
10. Report whether activation was visibly verified. Remind the user that a process restart clears the effect and SIP remains disabled. Provide rollback instructions.

## Relocation

Do not apply relocation automatically. Read README.md first. If requested, inspect current NSApplication windows and view/layer hierarchy in the current process. The HUD window was full-screen, while the second window was 33 points tall. Those observations are clues, not stable selectors. Never dereference old addresses.

The confirmed visual experiment applied a root layer sublayerTransform of CATransform3DMakeTranslation(0,-28,0), inside a disabled-animation CATransaction followed by flush. Capture the original transform before applying. The root NSView bounds-origin change alone had no visible effect. Combining bounds origin (0,28) with the layer transform was attempted to align hit testing, but clicking was never confirmed fixed. Disclose this and keep relocation optional. Restore original values on failure. Never claim a coordinate conversion proves working input.

## Failure recovery

Remove experiment breakpoints and detach if attached. `launchctl kickstart -k gui/$(id -u)/com.apple.MenuBarAgent` restarts the process and removes memory-only changes. If a pending launchctl debug setting leaves the next instance suspended, attach, continue, detach, then restart once more normally. Logging out or restarting macOS is a fallback after the user saves work. Offer Recovery instructions to reenable SIP. Confirm `csrutil status` after reboot.

Do not upload logs, binaries, screenshots, identifiers, or other user data. Publish only author-owned source and reviewed documentation when explicitly requested. Apple binaries are not included in this package.
