## [1.0.4] - 2026-05-19
### Added
- Added automatic loading and saving of the click sequence configuration to `config.json` in the application directory.
- Added a "Keep existing configuration / sequences" checkbox to the installer setup wizard (default to checked) to allow users to preserve or reset configuration settings during updates or reinstallation.
- Added multiple dynamic color themes (Dark Blue, Light, Matrix Green, and Sunset Purple) and dynamic hotkey selectors (Start/Stop, Add Point, and Clear Sequence) packaged inside a new dedicated, theme-coordinated Settings dialog window.

### Fixed
- Fixed installer deduplication issue to allow running the setup wizard from the desktop without self-replacing.
- Fixed installer to detect previous installation directory using a Windows Registry key.
- Fixed installer to terminate old running app processes before overwriting the executable.