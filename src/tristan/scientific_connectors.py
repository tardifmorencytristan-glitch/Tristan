from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ScientificSource:
    source_id: str
    provider: str
    domain: str
    access_mode: str
    base_url: str
    capabilities: tuple[str, ...]
    boundaries: tuple[str, ...]

    def validate(self) -> list[str]:
        errors: list[str] = []
        for name, value in (
            ("source_id", self.source_id),
            ("provider", self.provider),
            ("domain", self.domain),
            ("access_mode", self.access_mode),
            ("base_url", self.base_url),
        ):
            if not value.strip():
                errors.append(f"{name} required")
        if not self.capabilities:
            errors.append("capabilities required")
        if not self.boundaries:
            errors.append("boundaries required")
        return errors

    def to_dict(self) -> dict:
        return asdict(self)


SOURCES: dict[str, ScientificSource] = {
    "hepdata": ScientificSource(
        "hepdata",
        "HEPData",
        "high-energy-physics published measurements",
        "HTTP/API export metadata",
        "https://www.hepdata.net",
        ("published-binned-data", "uncertainties", "covariance-when-published", "machine-readable-exports"),
        ("PublishedMeasurement != RawEventData", "DatasetAvailability != ClaimSupport"),
    ),
    "cern_open_data": ScientificSource(
        "cern_open_data",
        "CERN Open Data",
        "high-energy-physics event data and simulation",
        "HTTP portal/API metadata",
        "https://opendata.cern.ch",
        ("event-data", "simulation", "software-environments", "provenance"),
        ("OpenData != ReanalysisCorrectness", "Simulation != Measurement"),
    ),
    "jwst_mast": ScientificSource(
        "jwst_mast",
        "MAST / JWST",
        "astronomy imaging and spectroscopy",
        "MAST service/API metadata; prefer documented astroquery or generated curl retrieval",
        "https://mast.stsci.edu",
        ("observation-search", "products", "spectroscopy", "calibrated-products", "astroquery", "curl-retrieval"),
        ("CalibratedProduct != TheoryValidation", "SelectionFunctionRequired", "RetrievalMethodMustBeCurrent"),
    ),
    "desi_data": ScientificSource(
        "desi_data",
        "DESI Data",
        "large-scale structure redshifts dark energy and cosmology",
        "public data portal and documented machine-readable products",
        "https://data.desi.lbl.gov",
        ("spectra", "redshifts", "bao", "lyman-alpha", "cosmology-results", "catalogs"),
        ("CosmologyResult != FundamentalLaw", "SelectionFunctionRequired", "CovarianceRequired"),
    ),
    "gwosc": ScientificSource(
        "gwosc",
        "Gravitational Wave Open Science Center",
        "gravitational-wave strain events and catalogs",
        "read-only REST API v2 and downloadable strain products",
        "https://gwosc.org/api/v2/",
        ("strain-data", "event-catalogs", "detector-data", "parameter-estimation", "provenance"),
        ("EventCandidate != TheoryValidation", "DetectorSystematicsRequired", "SelectionFunctionRequired"),
    ),
    "gaia_archive": ScientificSource(
        "gaia_archive",
        "ESA Gaia Archive",
        "astrometry photometry spectroscopy",
        "TAP/ADQL metadata",
        "https://gea.esac.esa.int/archive/",
        ("astrometry", "photometry", "radial-velocity", "catalog-query"),
        ("CatalogCorrelation != Causality", "SelectionFunctionRequired"),
    ),
    "planck_legacy": ScientificSource(
        "planck_legacy",
        "ESA Planck Legacy Archive",
        "cosmic microwave background and cosmology",
        "archive metadata",
        "https://pla.esac.esa.int",
        ("maps", "catalogs", "cosmology-products", "instrument-products"),
        ("ProcessedMap != FundamentalLaw", "ForegroundModelRequired"),
    ),
    "nasa_cmr": ScientificSource(
        "nasa_cmr",
        "NASA Earthdata CMR",
        "Earth observation discovery",
        "REST/GraphQL metadata",
        "https://cmr.earthdata.nasa.gov",
        ("collection-search", "granule-search", "temporal-spatial-discovery"),
        ("DiscoveryMetadata != MeasurementValidation", "DataVintageRequired"),
    ),
    "copernicus": ScientificSource(
        "copernicus",
        "Copernicus Data Space Ecosystem",
        "Earth observation",
        "STAC/OData/openEO/Sentinel Hub metadata",
        "https://dataspace.copernicus.eu",
        ("sentinel-discovery", "stac", "odata", "cloud-processing"),
        ("RemoteSensingProxy != GroundTruth", "ProcessingChainRequired"),
    ),
}


def source_catalog() -> dict[str, dict]:
    return {source_id: source.to_dict() for source_id, source in SOURCES.items()}


def select_scientific_sources(intent: str) -> tuple[str, ...]:
    text = intent.lower()
    selected: set[str] = set()

    if any(token in text for token in ("cern", "lhc", "atlas", "cms", "alice", "lhcb", "collision", "particle physics")):
        selected.update(("hepdata", "cern_open_data"))
    if any(token in text for token in ("jwst", "james webb", "webb telescope", "mast", "spectroscopy", "spectre", "spectral")):
        selected.add("jwst_mast")
    if any(token in text for token in ("desi", "dark energy", "bao", "baryon acoustic", "lyman-alpha", "lyman alpha", "large-scale structure", "large scale structure")):
        selected.add("desi_data")
    if any(token in text for token in ("ligo", "virgo", "kagra", "gwosc", "gravitational wave", "gravitational-wave", "strain data", "gwtc")):
        selected.add("gwosc")
    if any(token in text for token in ("gaia dr", "gaia archive", "astrometry", "astrometr", "parallax", "proper motion")):
        selected.add("gaia_archive")
    if any(token in text for token in ("planck", "cmb", "cosmic microwave", "microwave background")):
        selected.add("planck_legacy")
    if any(token in text for token in ("earthdata", "nasa cmr", "satellite", "earth observation", "ceres")):
        selected.add("nasa_cmr")
    if any(token in text for token in ("copernicus", "sentinel", "stac", "openeo", "open eo")):
        selected.add("copernicus")

    if any(token in text for token in ("all scientific data", "all observatories", "multi-instrument", "multi instrument")):
        selected.update(SOURCES)

    return tuple(sorted(selected))


def build_source_plan(intent: str) -> dict:
    source_ids = select_scientific_sources(intent)
    return {
        "schema_version": "jarvis-scientific-source-plan-r2",
        "selected_sources": source_ids,
        "sources": [SOURCES[source_id].to_dict() for source_id in source_ids],
        "network_executed": False,
        "status": "READY_FOR_BOUNDED_RETRIEVAL" if source_ids else "NO_SCIENTIFIC_SOURCE_SELECTED",
        "boundaries": (
            "SourceSelection != DataRetrieved",
            "DataRetrieved != CorrectAnalysis",
            "CorrectAnalysis != ScientificTruth",
            "QueryFirst != BulkDownload",
            "RetrievalMethodMustBeCurrent",
        ),
    }
