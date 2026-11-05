# Native Mac Island Experiment

An experimental, open-source LLDB script for enabling MenuBarAgent's native Dynamic Island interface on an older Mac running macOS 27.3.

## Verified results

On November 4, 2026, a user confirmed that the native island worked on an M2 MacBook Air running macOS 27.3 build **26C5035r**. The HUD startup gate and flag-write breakpoints each fired once. The process continued running after the debugger detached. Other devices and external displays have not been tested. This repository distributes the experiment's source code. Apple's system application is not included.

## How it works

Inside MenuBarAgent, an `IsAppleInternalBuild` check restricts access to the `EmulateCenterHUD` and `DisableCenterHUD` preferences. The script installs two breakpoints during process startup. The first sets this particular call's result to `w0=1`. The second sets two flags in the relevant settings structure to `1` and `0`. These changes affect the running process's memory. Restarting the process or the Mac clears the effect.

In the first arm64e slice, the gate address is `0x10057FD98`, and the flag-write location is `0x3c` bytes later. The manifest also includes the second slice's address. That second slice has not been tested at runtime. The executable's SHA-256 and UUID must match the manifest. The script is expected to reject an incompatible executable after a macOS update.

## What is SIP, and what are the risks?

System Integrity Protection limits access to protected system areas and processes, even for software with administrator or root privileges. During this experiment, debugger attachment was denied with SIP enabled and succeeded after SIP was disabled. Disabling SIP does not itself delete files or physically damage hardware. However, it weakens an important defense against malicious or faulty software modifying the system. [Apple's explanation of SIP](https://support.apple.com/en-gb/102149)

This code operates inside a system UI process. A mistake can freeze the menu bar or crash the process. Save your work and keep a current backup. We do not recommend leaving SIP disabled on your primary work computer. Reenabling SIP does not automatically undo earlier changes. The successful method in this package operates in memory, so restarting clears its effect. [Apple's developer documentation](https://developer.apple.com/documentation/security/disabling-and-enabling-system-integrity-protection)

## Requirements

- A MenuBarAgent executable that exactly matches the manifest and its supported build.
- An Apple Silicon Mac with Xcode and a working `xcrun lldb` command.
- An administrator account, physical access to Recovery, and acceptance of the risks.
- An AI tool with local terminal access, or the ability to run commands manually.

## Setup with an AI assistant

Download this repository and extract it into a working folder. Give your AI assistant access to the files and paste the contents of `AI-INSTALL-PROMPT.txt`. An agent with local tool access, such as Claude Code or Codex, can carry out the steps. A chat-only model will need you to run the commands yourself. A skill file alone does not grant computer access.

Start by checking `sw_vers -buildVersion`, `csrutil status`, and `xcrun --find lldb`. Check the executable's hash with `shasum -a 256 /System/Library/CoreServices/MenuBarAgent.app/Contents/MacOS/MenuBarAgent`. It must match `manifest.json`.

## Disabling SIP on Apple Silicon

1. Save your work and shut down your Mac.
2. Hold the power button until startup options appear.
3. Select **Options → Continue** to enter Recovery. Authenticate with your account if prompted.
4. Open **Utilities → Terminal**.
5. Run `csrutil disable`. Read the confirmation prompts and enter your administrator password there if requested.
6. After the command reports success, run `reboot`.
7. Back in your normal session, run `csrutil status` and confirm that it reports `disabled`.

Menu labels may vary with your system language. If Recovery reports an error, stop and inspect the message. This procedure does not require changing AMFI, authenticated root, or FileVault.

## Running manually

Open Terminal in the project folder and review the source code. Then run these commands in order.

```sh
sudo launchctl debug gui/$(id -u)/com.apple.MenuBarAgent --start-suspended
launchctl kickstart -k gui/$(id -u)/com.apple.MenuBarAgent
xcrun lldb -n MenuBarAgent
```

The menu bar may temporarily stop responding during this procedure. Inside LLDB, replace the example path below with the absolute path to your script. Quote the path if it contains spaces.

```text
command script import /YOUR/ABSOLUTE/PATH/startup_lldb.py
continue
```

Check the island using music playback or an existing Live Activity. Then press **Ctrl-C** in the LLDB terminal and run the following commands.

```text
script print(startup_lldb.hits)
breakpoint delete --force
process detach
quit
```

Both `gate` and `flags` counters should be positive. Also verify the visible result on your screen. Increasing counters alone do not prove that the interface works. Use these commands only in a debugger session dedicated to this experiment.

## Moving the island and handling clicks

The default experiment opens the island below the notch. The user confirmed visible movement after applying Y translations of `-20` and then `-28` points to the rendering layer. Changing the NSView bounds alone did not move the visible interface. The system rejected an attempt to move the window.

Clicking problems were reported after moving the island upward. An NSView bounds origin of `(0,28)` was tried together with a layer translation of `(0,-28)`. The coordinate conversion was measured, but successful clicking has not been confirmed. For this reason, the automatic setup leaves the default position in place. Runtime object addresses change between processes. Do not reuse addresses copied from someone else's chat or debugging session.

## Removal and recovery

After detaching the debugger, restart the service to clear the in-memory experiment.

```sh
launchctl kickstart -k gui/$(id -u)/com.apple.MenuBarAgent
```

If the start-suspended setting has not yet been consumed, the first restarted instance may be suspended. Attach with LLDB, run `continue`, press Ctrl-C, run `process detach`, and then `quit`. Restart the service normally again. If problems persist, save your work and restart your Mac.

To reenable SIP, return to **Recovery → Utilities → Terminal** and run the following commands.

```sh
csrutil enable
reboot
```

In your normal session, `csrutil status` should report `enabled`. The island activation and position changes from this method disappear after a restart. On the tested device, SIP blocked the same debugger intervention when enabled.

## Troubleshooting

- **SHA or UUID mismatch.** The executable is unsupported. Do not guess replacement addresses.
- **LLDB cannot be found.** Check your Xcode installation and selected developer tools.
- **Attachment is denied.** Check SIP status and debugserver logs. Do not automatically disable additional protections.
- **A hit counter stays at zero.** The process may not have been caught early enough. Check the start-suspended step.
- **The UI is frozen.** Check whether the debugger has left the process stopped, and detach cleanly.

## Credits and contributions

The post that prompted this experiment was by u/pdfu, who described `EmulateCenterHUD` and its `IsAppleInternalBuild` requirement. This script was developed through local disassembly and runtime experiments. [Original Reddit post](https://www.reddit.com/r/MacOSBeta/comments/1xne7v6/you_can_create_a_dynamic_island_around_macbooks/)

When contributing, include the macOS build, Mac model, executable hash, and observed result. Avoid uploading private logs, Apple binaries, or personal screen content. Supporting a new version requires analyzing its addresses again and documenting the actual device result.

The MIT license applies to this project's source code. Apple components remain subject to their own licenses. This project is not affiliated with Apple. Read the liability disclaimer in the license.
