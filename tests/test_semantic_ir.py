from tristan.semantic_ir import architecture_ir, dataflow_ir, protocol_ir, has_path


def test_dataflow_normalization_path_present():
    src = """
def f(latent, decoder, F):
    normed = F.normalize(latent, p=2)
    out = decoder(normed)
    return out
"""
    edges = dataflow_ir(src)
    assert has_path(edges, "latent", "normed", "normalize")
    assert has_path(edges, "normed", "out", "decoder")


def test_dataflow_negative_control_no_fake_normalize():
    src = """
def f(latent, decoder):
    out = decoder(latent)
    return out
"""
    edges = dataflow_ir(src)
    assert not has_path(edges, "latent", "out", "normalize")


def test_architecture_positive_control():
    src = "m = nn.Sequential(nn.Linear(8,16), nn.ReLU(), nn.Linear(16,4))"
    names = [n.name for n in architecture_ir(src)]
    assert "nn.Linear" in names and "nn.ReLU" in names


def test_architecture_negative_control_no_pool():
    src = "m = nn.Sequential(nn.Linear(8,4), nn.ReLU())"
    names = [n.name.lower() for n in architecture_ir(src)]
    assert not any("pool" in n for n in names)


def test_protocol_dataset_identity_positive():
    p = protocol_ir("ds = torchvision.datasets.CIFAR10(root='.')")
    assert any("cifar10" in x.lower() for x in p.datasets)


def test_protocol_dataset_identity_negative():
    p = protocol_ir("ds = torchvision.datasets.CIFAR100(root='.')")
    assert not any("cifar10" in x.lower() for x in p.datasets)


def test_protocol_seed_and_optimizer():
    p = protocol_ir("torch.manual_seed(7)\nopt = torch.optim.Adam(model.parameters(), lr=1e-3)")
    assert 7 in p.seeds
    assert any("adam" in x.lower() for x in p.optimizers)
