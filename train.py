"""Convenience entry point; authoritative training code lives in ml.train."""
import runpy

if __name__ == "__main__":
    runpy.run_module("ml.train", run_name="__main__")
