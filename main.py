"""FIRE Dashboard — entry point."""
import sys
import platform

def main():
    # Enable Retina / HiDPI rendering on macOS
    if platform.system() == "Darwin":
        try:
            from ctypes import cdll, c_int
            cdll.LoadLibrary("libobjc.dylib").objc_msgSend
            import subprocess
            # Tell the OS this process is HiDPI-aware
            subprocess.Popen(
                ["defaults", "write", "com.apple.tkinter", "NSHighResolutionCapable", "-bool", "YES"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
        except Exception:
            pass

    from app.app import FIREApp
    app = FIREApp()
    # Defer matplotlib font setup until after the window is visible
    def _late_init():
        from app.utils.formatting import setup_matplotlib_fonts
        setup_matplotlib_fonts()
    app.after(100, _late_init)
    app.mainloop()

if __name__ == "__main__":
    main()
