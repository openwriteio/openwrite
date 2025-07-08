# openwrite changelog

All notable changes to this project will be documented in this file.

## [0.10.4] - 2025-07-08
### Fixed
- pyproject.toml for pypi

## [0.10.0] - 2025-07-08
### Added
- Gemini support for single & multi blog instances
- Blog preview from dashboard

## [0.9.1] - 2025-07-04
### Added
- New theme: obscura

### Fixed
- Gemini views now have proper address
- Gemini supports proxy protocol
- A bit wrong CSS in single-blog mode
- Lack of logo in single-blog mode
- Logging works properly now
- Added ask for captcha in init

## [0.9.0] - 2025-07-03
### Added
- Statistics page in dashboard: charts with views, browsers and OS
- Tests for building: single-blog mode
- Blog description in gemini

### Fixed
- Path to themes
- Wrong date in sqlite

## [0.8.1] - 2025-07-01
### Fixed
- Added current path in dashboard to go back
- Preview now shows current theme
- Preview now shows correct date and time
- warm night theme colors

## [0.8.0] - 2025-06-30
### Added
- Logo change in admin panel
- Home text change in admin panel
- New theme: warm night

## [0.7.0] - 2025-06-29
### Added
- Single-blog mode

### Fixed
- Local upload works now 

## [0.6.1] - 2025-06-29
### Added
- Logging to logs/ directory(optional)

### Fixed
- Adding admin user to database and printing generated password
- run command now runs gunicorn normally, debugrun for werkzeug
- Translations didn't work in new instances

## [0.6.0] - 2025-06-27
### Added
- Theme selection

### Fixed
- Gemini displays date
- Some wrong CSSes

## [0.5.0] - 2025-06-26
### Added
- Gemini protocol
- More admin options

## [0.4.1] - 2025-06-25
### Fixed
- Prettier data import

## [0.4.0] - 2025-06-24
### Added
- Import data from xml/csv

## [0.3.1] - 2025-06-23
### Added
- Change password functionality
- More translations
- Blog created and updated date in db
- Published in ActivityPub blog Person object - date

### Fixed
- Updated initial blog description
