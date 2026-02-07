#!/usr/bin/env python3
"""
Matrix Generator - Policy-Mechanism Separation

Generates CI evaluation matrix from configuration.
Policy: ci/config.yaml defines what to run
Mechanism: This script transforms config into actionable matrix

Applied Skills:
- Policy-Mechanism Separation: Configuration drives execution
- Single Responsibility: Only generates matrix, doesn't execute
- Explicit State Invariants: Validates configuration structure
- Error Handling Design: Clear error messages for invalid config
"""

import yaml
import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any


def validate_provider_config(provider_name: str, config: Dict[str, Any]) -> List[str]:
    """Validate provider configuration structure."""
    errors = []
    
    if not isinstance(config.get("enabled"), bool):
        errors.append(f"{provider_name}: 'enabled' must be a boolean")
    
    if "models" not in config:
        errors.append(f"{provider_name}: missing 'models' list")
    elif not isinstance(config["models"], list):
        errors.append(f"{provider_name}: 'models' must be a list")
    elif len(config["models"]) == 0:
        errors.append(f"{provider_name}: 'models' list is empty")
    
    return errors


def generate_matrix(config: Dict[str, Any], filter_provider: str = "all") -> Dict[str, List[Dict[str, str]]]:
    """
    Generate evaluation matrix from configuration.
    
    Returns matrix suitable for CI parallelization.
    Each item contains provider, model, and extra args.
    """
    matrix = {"include": []}
    
    for provider_name, provider_config in config.items():
        # Skip disabled providers
        if not provider_config.get("enabled", False):
            continue
        
        # Apply filter if specified
        if filter_provider != "all" and filter_provider != provider_name:
            continue
        
        # Validate configuration
        errors = validate_provider_config(provider_name, provider_config)
        if errors:
            print(f"Configuration errors in '{provider_name}':", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
            continue
        
        # Generate matrix items for each model
        models = provider_config.get("models", [])
        for model in models:
            item = {
                "provider": provider_name,
                "model": model,
                "display_name": f"{provider_name}/{model}"
            }
            
            # Add provider-specific arguments (now handled implicitly in adapter)
            # extra_args = []
            # if provider_name == "ollama":
            #     if not provider_config.get("local", True):
            #         extra_args.append("--ollama-cloud")

            # item["extra_args"] = " ".join(extra_args)
            matrix["include"].append(item)

    return matrix


def main():
    parser = argparse.ArgumentParser(
        description="Generate CI evaluation matrix from configuration",
        epilog="Example: %(prog)s --filter-provider ollama"
    )
    parser.add_argument(
        "--config",
        default="ci/config.yaml",
        help="Path to configuration file (default: ci/config.yaml)"
    )
    parser.add_argument(
        "--filter-provider",
        default="all",
        help="Filter by provider name (default: all)"
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate configuration, don't generate matrix"
    )
    
    args = parser.parse_args()
    
    # Read configuration
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: Configuration file not found: {config_path}", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading config: {e}", file=sys.stderr)
        sys.exit(1)
    
    if not isinstance(config, dict):
        print("Error: Configuration must be a dictionary", file=sys.stderr)
        sys.exit(1)
    
    # Validate-only mode
    if args.validate_only:
        all_valid = True
        for provider_name, provider_config in config.items():
            errors = validate_provider_config(provider_name, provider_config)
            if errors:
                all_valid = False
                print(f"Errors in '{provider_name}':", file=sys.stderr)
                for error in errors:
                    print(f"  - {error}", file=sys.stderr)
        
        if all_valid:
            print("✓ Configuration is valid")
            sys.exit(0)
        else:
            print("✗ Configuration has errors", file=sys.stderr)
            sys.exit(1)
    
    # Generate matrix
    matrix = generate_matrix(config, args.filter_provider)
    
    if len(matrix["include"]) == 0:
        print("Warning: No enabled providers match filter criteria", file=sys.stderr)
    
    # Output ONLY JSON (no extra output to stdout)
    print(json.dumps(matrix))


if __name__ == "__main__":
    main()
