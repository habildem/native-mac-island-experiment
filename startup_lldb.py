"""Import after attaching to a launchctl --start-suspended MenuBarAgent.
No persistent preferences. Override HUD eligibility and initializer flags only.
"""
import hashlib
import json
from pathlib import Path
import lldb
hits = {'gate': 0, 'flags': 0}

def gate(frame, location, internal):
    if not frame.FindRegister('w0').SetValueFromCString('1'):
        return True
    hits['gate'] += 1
    return False

def flags(frame, location, internal):
    error = lldb.SBError()
    address = frame.FindRegister('x19').GetValueAsUnsigned()
    written = frame.GetThread().GetProcess().WriteMemory(address, bytes([1, 0]), error)
    if error.Fail() or written != 2:
        print('HUD flag write failed: ' + str(error))
        return True
    hits['flags'] += 1
    return False

def __lldb_init_module(debugger, internal):
    target = debugger.GetSelectedTarget()
    module = target.GetModuleAtIndex(0)
    manifest = json.loads(Path(__file__).with_name('manifest.json').read_text())
    assert hashlib.sha256(Path(str(module.GetFileSpec())).read_bytes()).hexdigest() == manifest['sha256']
    uuid = module.GetUUIDString().replace('-', '').upper()
    item = next(x for x in manifest['slices'] if x['uuid'] == uuid)
    # +0x3c: both preference loads have completed; x19 points at the HUD settings.
    for offset, callback in [(0, 'gate'), (0x3c, 'flags')]:
        address = module.ResolveFileAddress(item['address'] + offset)
        bp = target.BreakpointCreateBySBAddress(address)
        assert bp.IsValid() and bp.GetNumLocations() == 1
        bp.SetScriptCallbackFunction(__name__ + '.' + callback)
    print('Startup HUD breakpoints installed. Continue; inspect startup_lldb.hits before claiming success.')
