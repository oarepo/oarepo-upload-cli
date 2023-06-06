from flask import Blueprint


def create_blueprint_from_app(app):
    """Create  blueprint."""
    if app.config.get("MODEL_REGISTER_BLUEPRINT", True):
        blueprint = app.extensions["model"].resource.as_blueprint()
    else:
        blueprint = Blueprint("model", __name__, url_prefix="/empty/model")
    blueprint.record_once(init)
    return blueprint


def init(state):
    """Init app."""
    app = state.app
    ext = app.extensions["model"]

    # register service
    sregistry = app.extensions["invenio-records-resources"].registry
    sregistry.register(ext.service, service_id="model")

    # Register indexer
    iregistry = app.extensions["invenio-indexer"].registry
    iregistry.register(ext.service.indexer, indexer_id="model")
