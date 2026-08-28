def classFactory(iface):
    """Load InaRiskToQgis class from file InaRiskToQgis."""
    from .inarisk_to_qgis import InaRiskToQgis
    return InaRiskToQgis(iface)
