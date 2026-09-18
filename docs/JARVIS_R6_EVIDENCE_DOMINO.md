# Jarvis Tristan R6 - Evidence Foundry + Domino Engine

Status: PROVISIONAL ENGINEERING IMPLEMENTATION.

R6 extends the public Jarvis runtime with a dependency-light scientific evidence planning layer. It does not retrieve data or claim scientific validation by itself.

## New components

- scientific_connectors.py: bounded source registry and intent router for HEPData, CERN Open Data, MAST/JWST, Gaia Archive, Planck Legacy Archive, NASA Earthdata CMR and Copernicus Data Space.
- evidence_foundry.py: explicit theory-to-observable evidence contracts, falsification criteria, uncertainty obligations, replication requirements and fail-closed evidence receipts.
- domino_engine.py: bounded evidence-consequence propagation with causal/provenance/confidence gating, thresholding, cycle rejection and maximum propagation depth.
- jarvis_runtime.py: R6 integrates the new source/evidence layer into the canonical tristan jarvis entrypoint.

## Scientific boundaries

Generated != Verified.
SourceSelection != DataRetrieved.
DataRetrieved != CorrectAnalysis.
CorrectAnalysis != ScientificTruth.
Propagation != NewEvidence.
Correlation != Causality.
LocalEvidence != GlobalTheoryValidation.
PredictionGenerated != PredictionConfirmed.

A future network executor may retrieve public scientific data, but promotion remains an explicit OAK/evidence operation and never follows automatically from source availability or Domino propagation.
