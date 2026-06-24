# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.3.0] - 2024-06-18

### Added
- Initial MVP release of AI ERP system
- FastAPI backend with tax calculation engine for Myanmar tax system
- Support for 6 tax types: Commercial, Income, VAT, Specific Goods, Customs, and Stamp Duty
- Township data management for delivery calculations
- RESTful API endpoints for health checks, tax calculations, and township queries
- Comprehensive unit test suite with 100% endpoint coverage
- Security documentation with OWASP Top 10 mitigations
- Architecture and deployment documentation
- Environment-based configuration using pydantic-settings
- Docker support for containerization
- Kubernetes manifests for deployment

### Changed
- Refactored monolithic documentation into modular structure
- Moved hardcoded credentials to environment variables
- Improved project structure following Python best practices

### Fixed
- Resolved import errors in test suite
- Fixed filename with trailing space
- Corrected package structure with proper `__init__.py` files

### Removed
- Removed monolithic documentation file
- Eliminated hardcoded secrets from codebase
- Cleaned up unnecessary frontend and infrastructure files for MVP focus

## [3.2.0] - Previous Version
- Documentation and specification phase
- Initial architecture design
- Requirements gathering
