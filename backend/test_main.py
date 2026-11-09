"""Import and route checks that do not need a live database."""
from backend.app.main import app


def test_routes_registered():
    paths = {r.path for r in app.routes}
    for p in ["/health", "/experiments", "/experiments/{exp_id}/results",
              "/experiments/{exp_id}/heatmap", "/experiments/{exp_id}/capability"]:
        assert p in paths
