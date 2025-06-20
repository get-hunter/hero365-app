"""
Infrastructure Layer

This layer contains implementations of the interfaces defined in the domain and application layers.
It handles external concerns like databases, web APIs, file systems, and third-party services.

The infrastructure layer depends on the domain and application layers, but they don't depend on it,
following the dependency inversion principle of clean architecture.
""" 