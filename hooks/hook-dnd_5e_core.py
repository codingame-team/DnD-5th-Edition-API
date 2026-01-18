# PyInstaller hook for dnd-5e-core package
from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_submodules

# Collect all submodules
hiddenimports = collect_submodules('dnd_5e_core')

# Collect data files (JSON collections, etc.)
datas, binaries, _ = collect_all('dnd_5e_core')

