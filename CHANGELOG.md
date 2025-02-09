# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2024-02-10

### Added
- New `-g/--group` option to build only specified groups
  ```bash
  # Build only development group
  pydantic_config_builder -g development

  # Build multiple groups
  pydantic_config_builder -g development -g staging
  ```

## [0.4.0] - 2024-02-10

### Added
- New configuration format with separate input and output sections
  ```yaml
  group_name:
    input:
      - input1.yaml
      - input2.yaml
    output:
      - output1.yaml
      - output2.yaml
  ```
- Support for multiple output files from the same input files
- Backward compatibility with the old configuration format

## [0.3.0] - 2024-02-09

### Added
- Support for both `pydantic-config-builder.yaml` and `pydantic-config-builder.yml` as default configuration files
- Support for `-h` as an alternative to `--help` for displaying help message

## [0.2.0] - 2024-02-09

### Added
- Support for glob patterns in source file paths
  - `*.yaml` matches all YAML files in current directory
  - `**/*.yaml` matches all YAML files recursively in subdirectories
  - Automatic deduplication of matched files
  - Warning messages for patterns with no matches

## [0.1.0] - 2024-02-09

### Added
- Initial release
- Implemented YAML configuration builder
- Support for merging multiple YAML files
- Command line interface with configuration file support
- Relative and absolute path resolution
- Verbose mode for debugging
