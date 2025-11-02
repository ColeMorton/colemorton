#!/usr/bin/env python3
"""
Command Script Resolver

Resolves Claude command references to actual script paths, schemas, and templates
for consistent sub-agent execution across the DASV framework.
"""

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


@dataclass
class CommandScriptMapping:
    """Comprehensive mapping for a single command phase"""

    domain: str
    phase: str
    sub_agent: str
    primary_script: str
    cli_services: list[str]
    schema: str
    template: str
    output_dir: str
    file_pattern: str
    supporting_scripts: list[str] | None = None
    script_class: str | None = None
    registry_name: str | None = None
    content_types: list[str] | None = None


@dataclass
class TwitterCommandMapping:
    """Mapping for Twitter command configurations"""

    command_name: str
    sub_agent: str
    primary_script: str
    script_class: str
    registry_name: str
    content_types: list[str]
    supporting_components: dict[str, str]
    templates: dict[str, Any]
    output_dir: str
    file_pattern: str


@dataclass
class CLIServiceMapping:
    """Mapping for CLI service configurations"""

    service_name: str
    script_path: str
    service_class: str
    capabilities: list[str]
    common_commands: dict[str, str]


class CommandScriptResolver:
    """Resolves command references to actual script paths for sub-agent execution"""

    def __init__(self, registry_path: str | None = None):
        """
        Initialize resolver with command registry

        Args:
            registry_path: Path to command_script_registry.json
        """
        if registry_path is None:
            registry_path = Path(__file__).parent.parent / "command_script_registry.json"

        self.registry_path = Path(registry_path)
        self.registry = self._load_registry()
        self.path_variables = self.registry.get("path_variables", {})

    def _load_registry(self) -> dict[str, Any]:
        """Load the command script registry"""
        try:
            with open(self.registry_path) as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Command registry not found at {self.registry_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in command registry: {e}")

    def _resolve_path_variables(self, path: str) -> str:
        """Resolve path variables like {SCRIPTS_BASE} to actual paths"""
        resolved_path = path
        for variable, value in self.path_variables.items():
            resolved_path = resolved_path.replace(f"{{{variable}}}", value)
        return resolved_path

    def get_scripts_for_command(self, domain: str, phase: str) -> CommandScriptMapping | None:
        """
        Get all scripts, schemas, templates for a DASV command

        Args:
            domain: Analysis domain (fundamental_analysis, trade_history, etc.)
            phase: DASV phase (discover, analyze, synthesize, validate)

        Returns:
            CommandScriptMapping with all resolved paths
        """
        command_mappings = self.registry.get("command_mappings", {})

        if domain not in command_mappings:
            return None

        domain_config = command_mappings[domain]
        if phase not in domain_config:
            return None

        phase_config = domain_config[phase]

        # Resolve all path variables
        primary_script = self._resolve_path_variables(phase_config["primary_script"])
        cli_services = [self._resolve_path_variables(service) for service in phase_config.get("cli_services", [])]
        schema = self._resolve_path_variables(phase_config["schema"])
        template = phase_config.get("template", "")
        output_dir = self._resolve_path_variables(phase_config["output_dir"])
        supporting_scripts = None
        if "supporting_scripts" in phase_config:
            supporting_scripts = [self._resolve_path_variables(script) for script in phase_config["supporting_scripts"]]

        return CommandScriptMapping(
            domain=domain,
            phase=phase,
            sub_agent=phase_config["sub_agent"],
            primary_script=primary_script,
            cli_services=cli_services,
            schema=schema,
            template=template,
            output_dir=output_dir,
            file_pattern=phase_config["file_pattern"],
            supporting_scripts=supporting_scripts,
        )

    def resolve_sub_agent_scripts(self, domain: str, phase: str, sub_agent: str) -> list[str]:
        """
        Get script paths a specific sub-agent should execute for a command

        Args:
            domain: Analysis domain
            phase: DASV phase
            sub_agent: Sub-agent name (researcher, analyst, synthesist, twitter_writer)

        Returns:
            List of resolved script paths for the sub-agent
        """
        mapping = self.get_scripts_for_command(domain, phase)
        if not mapping or mapping.sub_agent != sub_agent:
            return []

        scripts = [mapping.primary_script]
        if mapping.supporting_scripts:
            scripts.extend(mapping.supporting_scripts)
        if mapping.cli_services:
            scripts.extend(mapping.cli_services)

        return scripts

    def get_twitter_command(self, command_name: str) -> TwitterCommandMapping | None:
        """
        Get Twitter command configuration

        Args:
            command_name: Twitter command name

        Returns:
            TwitterCommandMapping with resolved paths
        """
        twitter_commands = self.registry.get("twitter_commands", {})

        if command_name not in twitter_commands:
            return None

        config = twitter_commands[command_name]

        # Resolve path variables
        primary_script = self._resolve_path_variables(config["primary_script"])
        supporting_components = {
            key: self._resolve_path_variables(path) for key, path in config["supporting_components"].items()
        }

        templates = config["templates"].copy()
        if "base_dir" in templates:
            templates["base_dir"] = self._resolve_path_variables(templates["base_dir"])

        output_dir = self._resolve_path_variables(config["output_dir"])

        return TwitterCommandMapping(
            command_name=command_name,
            sub_agent=config["sub_agent"],
            primary_script=primary_script,
            script_class=config["script_class"],
            registry_name=config["registry_name"],
            content_types=config["content_types"],
            supporting_components=supporting_components,
            templates=templates,
            output_dir=output_dir,
            file_pattern=config["file_pattern"],
        )

    def get_cli_service(self, service_name: str) -> CLIServiceMapping | None:
        """
        Get CLI service configuration

        Args:
            service_name: CLI service name

        Returns:
            CLIServiceMapping with resolved paths
        """
        cli_services = self.registry.get("cli_services", {})

        if service_name not in cli_services:
            return None

        config = cli_services[service_name]

        # Resolve path variables
        script_path = self._resolve_path_variables(config["script_path"])
        common_commands = {key: self._resolve_path_variables(cmd) for key, cmd in config["common_commands"].items()}

        return CLIServiceMapping(
            service_name=service_name,
            script_path=script_path,
            service_class=config["service_class"],
            capabilities=config["capabilities"],
            common_commands=common_commands,
        )

    def list_available_domains(self) -> list[str]:
        """Get list of available analysis domains"""
        return list(self.registry.get("command_mappings", {}).keys())

    def list_available_phases(self, domain: str) -> list[str]:
        """Get list of available phases for a domain"""
        command_mappings = self.registry.get("command_mappings", {})
        if domain not in command_mappings:
            return []
        return list(command_mappings[domain].keys())

    def list_twitter_commands(self) -> list[str]:
        """Get list of available Twitter commands"""
        return list(self.registry.get("twitter_commands", {}).keys())

    def list_cli_services(self) -> list[str]:
        """Get list of available CLI services"""
        return list(self.registry.get("cli_services", {}).keys())

    def validate_script_paths_exist(self) -> dict[str, list[str]]:
        """
        Validate that all script paths in registry exist

        Returns:
            Dictionary with 'missing' and 'found' lists
        """
        missing = []
        found = []

        # Check DASV command scripts
        for domain, phases in self.registry.get("command_mappings", {}).items():
            for phase, config in phases.items():
                primary_script = self._resolve_path_variables(config["primary_script"])
                if Path(primary_script).exists():
                    found.append(primary_script)
                else:
                    missing.append(primary_script)

                # Check supporting scripts
                for script in config.get("supporting_scripts", []):
                    resolved_script = self._resolve_path_variables(script)
                    if Path(resolved_script).exists():
                        found.append(resolved_script)
                    else:
                        missing.append(resolved_script)

                # Check CLI services
                for service in config.get("cli_services", []):
                    resolved_service = self._resolve_path_variables(service)
                    if Path(resolved_service).exists():
                        found.append(resolved_service)
                    else:
                        missing.append(resolved_service)

        # Check Twitter command scripts
        for command, config in self.registry.get("twitter_commands", {}).items():
            primary_script = self._resolve_path_variables(config["primary_script"])
            if Path(primary_script).exists():
                found.append(primary_script)
            else:
                missing.append(primary_script)

        return {"missing": list(set(missing)), "found": list(set(found))}

    def validate_schema_paths_exist(self) -> dict[str, list[str]]:
        """
        Validate that all schema paths in registry exist

        Returns:
            Dictionary with 'missing' and 'found' lists
        """
        missing = []
        found = []

        for domain, phases in self.registry.get("command_mappings", {}).items():
            for phase, config in phases.items():
                schema_path = self._resolve_path_variables(config["schema"])
                if Path(schema_path).exists():
                    found.append(schema_path)
                else:
                    missing.append(schema_path)

        return {"missing": list(set(missing)), "found": list(set(found))}

    def get_registry_info(self) -> dict[str, Any]:
        """Get registry metadata and statistics"""
        return {
            "version": self.registry.get("version", "unknown"),
            "last_updated": self.registry.get("last_updated", "unknown"),
            "total_dasv_commands": len(
                [phase for domain in self.registry.get("command_mappings", {}).values() for phase in domain.keys()]
            ),
            "total_domains": len(self.registry.get("command_mappings", {})),
            "total_twitter_commands": len(self.registry.get("twitter_commands", {})),
            "total_cli_services": len(self.registry.get("cli_services", {})),
            "validation": self.registry.get("validation", {}),
        }


def main():
    """CLI interface for testing the resolver"""
    import argparse

    parser = argparse.ArgumentParser(description="Command Script Resolver CLI")
    parser.add_argument("--domain", help="Analysis domain")
    parser.add_argument("--phase", help="DASV phase")
    parser.add_argument("--twitter-command", help="Twitter command name")
    parser.add_argument("--cli-service", help="CLI service name")
    parser.add_argument("--validate", action="store_true", help="Validate all paths")
    parser.add_argument("--info", action="store_true", help="Show registry info")
    parser.add_argument("--list-domains", action="store_true", help="List available domains")

    args = parser.parse_args()

    resolver = CommandScriptResolver()

    if args.info:
        info = resolver.get_registry_info()
        print(json.dumps(info, indent=2))

    elif args.validate:
        print("Validating script paths...")
        script_validation = resolver.validate_script_paths_exist()
        print("Found: {len(script_validation['found'])} scripts")
        print("Missing: {len(script_validation['missing'])} scripts")

        if script_validation["missing"]:
            print("\nMissing scripts:")
            for script in script_validation["missing"]:
                print("  - {script}")

        print("\nValidating schema paths...")
        schema_validation = resolver.validate_schema_paths_exist()
        print("Found: {len(schema_validation['found'])} schemas")
        print("Missing: {len(schema_validation['missing'])} schemas")

        if schema_validation["missing"]:
            print("\nMissing schemas:")
            for schema in schema_validation["missing"]:
                print("  - {schema}")

    elif args.list_domains:
        domains = resolver.list_available_domains()
        print("Available domains:")
        for domain in domains:
            phases = resolver.list_available_phases(domain)
            print("  - {domain}: {', '.join(phases)}")

    elif args.domain and args.phase:
        mapping = resolver.get_scripts_for_command(args.domain, args.phase)
        if mapping:
            print(
                json.dumps(
                    {
                        "domain": mapping.domain,
                        "phase": mapping.phase,
                        "sub_agent": mapping.sub_agent,
                        "primary_script": mapping.primary_script,
                        "cli_services": mapping.cli_services,
                        "schema": mapping.schema,
                        "template": mapping.template,
                        "output_dir": mapping.output_dir,
                        "file_pattern": mapping.file_pattern,
                        "supporting_scripts": mapping.supporting_scripts,
                    },
                    indent=2,
                )
            )
        else:
            print("No mapping found for {args.domain}/{args.phase}")

    elif args.twitter_command:
        mapping = resolver.get_twitter_command(args.twitter_command)
        if mapping:
            print(
                json.dumps(
                    {
                        "command_name": mapping.command_name,
                        "sub_agent": mapping.sub_agent,
                        "primary_script": mapping.primary_script,
                        "script_class": mapping.script_class,
                        "registry_name": mapping.registry_name,
                        "templates": mapping.templates,
                        "output_dir": mapping.output_dir,
                    },
                    indent=2,
                )
            )
        else:
            print("No Twitter command found: {args.twitter_command}")

    elif args.cli_service:
        mapping = resolver.get_cli_service(args.cli_service)
        if mapping:
            print(
                json.dumps(
                    {
                        "service_name": mapping.service_name,
                        "script_path": mapping.script_path,
                        "service_class": mapping.service_class,
                        "capabilities": mapping.capabilities,
                        "common_commands": mapping.common_commands,
                    },
                    indent=2,
                )
            )
        else:
            print("No CLI service found: {args.cli_service}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
