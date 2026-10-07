"""transcribe-video: Download and transcribe video audio using Whisper."""

import os
import sys

if sys.platform == "win32":
    import ctypes
    import glob
    import sysconfig

    # ctranslate2 loads cuBLAS on demand from native code, which does not consult
    # directories registered via os.add_dll_directory(). Pre-load the NVIDIA runtime
    # DLLs by absolute path so later bare-name loads resolve to them.
    for _bin_dir in glob.glob(os.path.join(sysconfig.get_paths()["purelib"], "nvidia", "*", "bin")):
        try:
            os.add_dll_directory(_bin_dir)
        except OSError:
            continue
        for _dll in glob.glob(os.path.join(_bin_dir, "*.dll")):
            try:
                ctypes.CDLL(_dll)
            except OSError:
                pass

__version__ = "0.1.0"
