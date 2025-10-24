import sys
import importlib

OK = "\x1b[42m[ OK ]\x1b[0m"
FAIL = "\x1b[41m[FAIL]\x1b[0m"

try:
    from packaging.version import Version
except ImportError:
    print(
        FAIL, "'packaging' package not installed, install it with conda or pip"
    )
    sys.exit(1)

# first check the python version
print("Using python in", sys.prefix)
print(sys.version)
pyversion_str = f"{sys.version_info.major}.{sys.version_info.minor}"
pyversion = Version(pyversion_str)

if pyversion < Version("3.8"):
    print(
        FAIL,
        (
            "Python version 3.8 or above is required,"
            f" but {pyversion_str} is installed."
        ),
    )
    sys.exit(1)

if pyversion > Version("3.13"):
    print(
        FAIL,
        (
            "Python version 3.13 or below is required,"
            f" but {pyversion_str} is installed."
        ),
    )
    sys.exit(1)
print()


def import_version(pkg, min_ver, fail_msg=""):
    mod = None
    try:
        mod = importlib.import_module(pkg)
        if pkg in {"PIL"}:
            try:
                ver = mod.__version__
            except AttributeError:
                try:
                    ver = mod.VERSION
                except AttributeError:
                    try:
                        ver = mod.PILLOW_VERSION
                    except Exception:
                        raise
        elif pkg == "playwright":
            # Playwright uses a different version access method
            try:
                ver = mod.__version__
            except AttributeError:
                # If __version__ not available, check if module is importable
                print(OK, f"{pkg} installed (version check skipped)")
                return mod
        else:
            ver = mod.__version__
        if Version(ver) < Version(min_ver):
            print(
                FAIL,
                (
                    f"{pkg} version {min_ver} or higher required, but"
                    f" {ver} installed."
                ),
            )
        else:
            print(OK, f"{pkg} version {ver}")
    except ImportError:
        print(FAIL, f"{pkg} not installed. {fail_msg}")
    return mod


requirements = {
    "numpy": "1.21",
    "scipy": "1.7",
    "matplotlib": "3.5",
    "sklearn": "1.0",
    "pandas": "1.3",
    "seaborn": "0.13",
    "notebook": "6.4",
    "plotly": "5.10",
    "requests": "2.26",
    "playwright": "1.20",
    "scrapy": "2.5",
    "lxml": "4.6",
    "trafilatura": "1.0",
    "bs4": "0.0.1",
}

# now the dependencies
for lib, required_version in list(requirements.items()):
    import_version(lib, required_version)
