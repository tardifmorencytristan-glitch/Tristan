from tristan.epistemic_ir import ScientificContract, evaluate_contract, formula_ir, implementation_ir


def test_formula_ir_preserves_coefficient_difference():
    assert formula_ir("4*epsilon") != formula_ir("epsilon")


def test_formula_ir_preserves_power_difference():
    assert formula_ir("(1-z)**2") != formula_ir("1-z")


def test_commutative_addition_is_canonicalized():
    assert formula_ir("x+y") == formula_ir("y+x")


def test_required_normalization_detected_when_present():
    facts = implementation_ir("y = F.normalize(x, p=2)\nout = decoder(y)")
    finding = evaluate_contract(ScientificContract("latent", "normalization", "normalize"), facts)
    assert finding.status == "SUPPORTED"


def test_missing_normalization_is_hold():
    facts = implementation_ir("out = decoder(latent)")
    finding = evaluate_contract(ScientificContract("latent", "normalization", "normalize"), facts)
    assert finding.status == "POTENTIAL_MISMATCH"


def test_undocumented_relu_is_extractable():
    facts = implementation_ir("score = F.relu(cosine_similarity(x, y))")
    assert any(f.kind == "nonlinearity" and "relu" in str(f.value).lower() for f in facts)


def test_clamp_is_extractable():
    facts = implementation_ir("w = torch.clamp(functionality, min=0.3)")
    assert any(f.kind == "bound" for f in facts)
    assert any(f.kind == "constant" and f.value == 0.3 for f in facts)


def test_loss_term_is_extractable():
    facts = implementation_ir("loss = F.cross_entropy(logits, target)")
    assert any(f.kind == "loss_term" for f in facts)


def test_dataset_identity_contract():
    good = implementation_ir("ds = torchvision.datasets.CIFAR10(root='.')")
    bad = implementation_ir("ds = torchvision.datasets.CIFAR100(root='.')")
    c = ScientificContract("dataset", "dataset", "CIFAR10")
    assert evaluate_contract(c, good).status == "SUPPORTED"
    assert evaluate_contract(c, bad).status == "POTENTIAL_MISMATCH"
