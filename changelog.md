## [1.0.2] - 2026-05-19
### Fixed
- Fixed an issue where changing click positions manually caused lag and opened numerous duplicate top-level windows.
- Fixed UI stylesheet and palette fallbacks to force a consistent dark theme regardless of host OS light/dark preferences.

### Added
- Added automatic update checks against GitHub Releases with a notification banner to download new versions.
- Added up and down arrow buttons on action cards to reorder the sequence list.
- Added a built-in Setup Wizard that automates user installation directory choice, desktop & start menu shortcut configuration, and self-replacement/cleanup of the installer.
- Created an application icon and configured it for the PyQt6 window, desktop shortcut links, and compiled PyInstaller executable.