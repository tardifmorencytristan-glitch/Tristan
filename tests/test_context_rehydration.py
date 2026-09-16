from tristan.context_rehydration import ConceptIdentity, audit_registry_context, context_ci, rehydrate_context, resolve_concepts
from tristan.model import TristanObject
from tristan.registry import Registry


def obj(oid, title, *, deps=(), failures=(), memory=None, stale=False):
    return TristanObject(
        oid, "CAPABILITY", title, "SUPPORTED", title,
        dependencies=deps, failures=failures,
        metadata={"memory_state": memory, "stale": stale},
    )


def test_alias_resolution_does_not_create_new_concept():
    ids = (ConceptIdentity("scientific_consistency", "Scientific Consistency", ("Equation-Code Verifier", "Paper-Code Drift Detector")),)
    assert resolve_concepts("Improve the Equation-Code Verifier", ids) == ("scientific_consistency",)


def test_rehydration_closes_dependencies_and_referenced_negative_memory():
    reg = Registry([
        obj("core", "Scientific Consistency", deps=("semantic",), failures=("id:r05",)),
        obj("semantic", "Semantic IR"),
        obj("r05", "R0.5 holdout failure", memory="M-"),
    ])
    ctx = rehydrate_context("scientific consistency", reg, limit=1)
    assert ctx.seed_ids == ("core",)
    assert ctx.selected_ids == ("core", "r05", "semantic")
    assert ctx.memory_ids == ("r05",)
    assert context_ci(ctx) == ()


def test_inline_failure_is_retained_as_embedded_negative_memory():
    reg = Registry([obj("core", "Scientific Consistency", failures=("Simulation!=Measurement",))])
    ctx = rehydrate_context("scientific consistency", reg)
    assert ctx.inline_negative_memory == ("Simulation!=Measurement",)
    assert ctx.debt.missing_failures == ()
    assert audit_registry_context(reg).clean


def test_missing_referenced_negative_memory_is_context_debt():
    reg = Registry([obj("core", "Scientific Consistency", failures=("id:missing_r05",))])
    ctx = rehydrate_context("scientific consistency", reg)
    assert ctx.debt.missing_failures == ("missing_r05",)
    assert "MISSING_NEGATIVE_MEMORY" in context_ci(ctx)


def test_stale_memory_blocks_context_ci():
    reg = Registry([obj("core", "Scientific Consistency", stale=True)])
    ctx = rehydrate_context("scientific consistency", reg)
    assert context_ci(ctx) == ("STALE_CONTEXT",)


def test_empty_context_is_not_silently_accepted():
    ctx = rehydrate_context("unmatched", Registry([obj("x", "Something else")]))
    assert context_ci(ctx) == ("EMPTY_CONTEXT",)
