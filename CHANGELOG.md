# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2024-12-19

### Changed

- Updated Textual to 1.0.0.
- Shortcuts are slightly different with the newer Textual release.
- Lots of under-the-hood changes.

### Fixed

- Fix removing environments not working with newer conda versions.
- Fix blocked event loop during shutdown where the loading indicator was not moving.
