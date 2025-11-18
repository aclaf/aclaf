"""Custom validators for integration tests demonstrating validator protocol.

This module contains domain-specific validators for complex parameter formats
used in Docker-like, kubectl-like, and Git-like CLIs. These validators serve as
examples of how to implement custom validation logic.
"""

import re
from typing import TYPE_CHECKING

from annotated_types import BaseMetadata

if TYPE_CHECKING:
    from collections.abc import Mapping

    from aclaf.types import ParameterValueType


class PortMapping(BaseMetadata):
    """Validates Docker-style port mapping format.

    Supports formats:
    - "8080:80" (host_port:container_port)
    - "127.0.0.1:8080:80" (host_ip:host_port:container_port)
    - "8080:80/tcp" (with protocol)
    - "127.0.0.1:8080:80/udp" (full format with protocol)
    """


class EnvVar(BaseMetadata):
    """Validates environment variable format: KEY=VALUE.

    KEY must start with letter or underscore, followed by alphanumeric/underscore.
    VALUE can be any string (including empty).
    """


class Label(BaseMetadata):
    """Validates label format: key=value.

    Key can contain alphanumeric, dots, hyphens, underscores.
    """


class ResourceLimit(BaseMetadata):
    """Validates resource limit format for memory/CPU.

    Supports formats:
    - "512m", "2g", "1024k" (memory)
    - "0.5", "2", "1.5" (CPU)
    """


def validate_port_mapping(
    value: "ParameterValueType | None",
    _other_parameters: "Mapping[str, ParameterValueType | None]",
    _metadata: BaseMetadata,
) -> tuple[str, ...] | None:
    """Validate port mapping format."""
    if not isinstance(value, str):
        return ("must be a string.",)

    # Pattern: [host_ip:]host_port:container_port[/protocol]
    # Examples: "8080:80", "127.0.0.1:8080:80", "8080:80/tcp"
    port_pattern = re.compile(
        r"^(?:(?P<host_ip>[\w.]+):)?(?P<host_port>\d+):(?P<container_port>\d+)"
        r"(?:/(?P<protocol>tcp|udp))?$"
    )

    port_match = port_pattern.match(value)
    if not port_match:
        msg = (
            "must be in format [host_ip:]host_port:container_port[/protocol] "
            '(e.g., "8080:80", "127.0.0.1:8080:80/tcp").'
        )
        return (msg,)

    # Validate port numbers are in valid range (1-65535)
    host_port = int(port_match.group("host_port"))
    container_port = int(port_match.group("container_port"))

    errors: list[str] = []
    if not 1 <= host_port <= 65535:
        errors.append(f"host port {host_port} must be between 1 and 65535.")
    if not 1 <= container_port <= 65535:
        errors.append(f"container port {container_port} must be between 1 and 65535.")

    if errors:
        return tuple(errors)

    return None


def validate_env_var(
    value: "ParameterValueType | None",
    _other_parameters: "Mapping[str, ParameterValueType | None]",
    _metadata: BaseMetadata,
) -> tuple[str, ...] | None:
    """Validate environment variable format."""
    if not isinstance(value, str):
        return ("must be a string.",)

    # Pattern: KEY=VALUE where KEY starts with letter/underscore
    env_pattern = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$")

    if not env_pattern.match(value):
        msg = (
            "must be in format KEY=VALUE where KEY starts with letter or "
            'underscore (e.g., "PATH=/usr/bin", "DEBUG=true").'
        )
        return (msg,)

    return None


def validate_label(
    value: "ParameterValueType | None",
    _other_parameters: "Mapping[str, ParameterValueType | None]",
    _metadata: BaseMetadata,
) -> tuple[str, ...] | None:
    """Validate label format."""
    if not isinstance(value, str):
        return ("must be a string.",)

    # Pattern: key=value where key can contain alphanumeric, dots, hyphens, underscores
    label_pattern = re.compile(r"^([a-zA-Z0-9._-]+)=(.*)$")

    if not label_pattern.match(value):
        msg = (
            "must be in format key=value where key contains only "
            'alphanumeric, dots, hyphens, or underscores (e.g., "app.version=1.0", '
            '"env=production").'
        )
        return (msg,)

    return None


def validate_resource_limit(
    value: "ParameterValueType | None",
    _other_parameters: "Mapping[str, ParameterValueType | None]",
    _metadata: BaseMetadata,
) -> tuple[str, ...] | None:
    """Validate resource limit format."""
    if not isinstance(value, str):
        return ("must be a string.",)

    # Pattern for memory: number followed by k, m, g (case insensitive)
    # Pattern for CPU: decimal number
    memory_pattern = re.compile(r"^(\d+(?:\.\d+)?)[kmg]$", re.IGNORECASE)
    cpu_pattern = re.compile(r"^(\d+(?:\.\d+)?)$")

    memory_match = memory_pattern.match(value)
    cpu_match = cpu_pattern.match(value)

    if memory_match:
        # Valid memory format
        return None
    if cpu_match:
        # Valid CPU format
        cpu_value = float(cpu_match.group(1))
        if cpu_value <= 0:
            return ("CPU value must be greater than 0.",)
        return None

    msg = (
        'must be in format like "512m", "2g", "1024k" for memory or '
        '"0.5", "2" for CPU count.'
    )
    return (msg,)
