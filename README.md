# pydantic-config-builder

A tool to build YAML configurations by merging multiple files.

## Features

- Merge multiple YAML files into a single configuration file
- Support for base configuration files with overlay files
- Recursive merging of dictionaries and arrays
- Use built configurations as base for other configurations
- Configuration file based build management
- Command line interface tool
- Support for relative and absolute paths
- Home directory expansion with ~

## Installation

```bash
pip install pydantic-config-builder
```

## Usage

Create a configuration file named `pydantic_config_builder.yml` in your project directory:

```yaml
# Keys are output file paths
# Values are lists of source files to merge
default.yaml:
  - base.yaml
  - path/to/base.yaml
~/path/to/config.yaml:
  - default.yaml
  - /path/to/overlay.yaml
```

Then run the builder:

```bash
# Use default configuration file (pydantic_config_builder.yml)
pydantic_config_builder

# Or specify a configuration file
pydantic_config_builder -c path/to/config.yml

# Enable verbose output
pydantic_config_builder -v
```

### Path Resolution

- Absolute paths (starting with /) are used as is
- Paths starting with ~ are expanded to the user's home directory
- Relative paths are resolved relative to the configuration file's directory

### Merging Behavior

- Dictionaries are merged recursively, with later files overwriting earlier ones
- Arrays are replaced entirely (not appended or merged by index)

## Example

Given these files:

`base.yaml`:
```yaml
database:
  host: localhost
  port: 5432
  credentials:
    username: admin
logging:
  level: info
```

`overlay.yaml`:
```yaml
database:
  port: 5433
  credentials:
    password: secret
logging:
  format: json
```

And this configuration:

```yaml
# pydantic_config_builder.yml
config.yaml:
  - base.yaml
  - overlay.yaml
```

The resulting `config.yaml` will be:

```yaml
database:
  host: localhost
  port: 5433
  credentials:
    username: admin
    password: secret
logging:
  level: info
  format: json
```

## Documentation

For more detailed documentation, please see the [GitHub repository](https://github.com/kiarina/pydantic-config-builder).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
