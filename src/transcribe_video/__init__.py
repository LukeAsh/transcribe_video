"""transcribe-video: Download and transcribe video audio using Whisper."""

import os
import sys

if sys.platform == "win32":
    import glob
    import sysconfig

    for _bin_dir in glob.glob(os.path.join(sysconfig.get_paths()["purelib"], "nvidia", "*", "bin")):
        os.add_dll_directory(_bin_dir)

__version__ = "0.1.0"
