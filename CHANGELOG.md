# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
- Improved Error messages; Line tracking 
- Speedup for large data parsing (> 150,000 characters) 
## [0.0.1] - 2022-08-06 
### Added
- Simplified object parsing (single function, non recursive) 
- Fixed recursive limit for sub-object parsing; previously python recursion limit 
### Removed
- Removed rule parser (Unnecessary addition)  

[0.0.1]: https://github.com/heyitsmass/mass-json/tree/release