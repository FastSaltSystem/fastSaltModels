"""Entry point for dedicated sector-to-maintenance-tank heated bundles."""
def build_fuel_services(b,layout,services):
    from .installation_bundles import build_fuel_services as build
    return build(b,layout,services)
