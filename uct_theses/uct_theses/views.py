from flask import Blueprint


def create_blueprint_from_app_uct_theses(app):
    """Create  blueprint."""
    blueprint = app.extensions["uct_theses"].resource.as_blueprint()
    blueprint.record_once(init_create_blueprint_from_app_uct_theses)

    # calls record_once for all other functions starting with "init_addons_"
    # https://stackoverflow.com/questions/58785162/how-can-i-call-function-with-string-value-that-equals-to-function-name
    funcs = globals()
    funcs = [
        v
        for k, v in funcs.items()
        if k.startswith("init_addons_uct_theses") and callable(v)
    ]
    for func in funcs:
        blueprint.record_once(func)

    return blueprint


def init_create_blueprint_from_app_uct_theses(state):
    """Init app."""
    app = state.app
    ext = app.extensions["uct_theses"]

    # register service
    sregistry = app.extensions["invenio-records-resources"].registry
    sregistry.register(ext.service, service_id="uct_theses")

    # Register indexer
    if hasattr(ext.service, "indexer"):
        iregistry = app.extensions["invenio-indexer"].registry
        iregistry.register(ext.service.indexer, indexer_id="uct_theses")


def create_blueprint_from_app_uct_thesesExt(app):
    """Create -ext blueprint."""
    blueprint = Blueprint("uct_theses-ext", __name__, url_prefix="uct_theses")
    blueprint.record_once(init_create_blueprint_from_app_uct_theses)

    # calls record_once for all other functions starting with "init_app_addons_"
    # https://stackoverflow.com/questions/58785162/how-can-i-call-function-with-string-value-that-equals-to-function-name
    funcs = globals()
    funcs = [
        v
        for k, v in funcs.items()
        if k.startswith("init_app_addons_uct_theses") and callable(v)
    ]
    for func in funcs:
        blueprint.record_once(func)

    return blueprint


def create_blueprint_from_app_uct_theses_file(app):
    """Create  blueprint."""
    blueprint = app.extensions["uct_theses_file"].resource.as_blueprint()
    blueprint.record_once(init_create_blueprint_from_app_uct_theses_file)

    # calls record_once for all other functions starting with "init_addons_"
    # https://stackoverflow.com/questions/58785162/how-can-i-call-function-with-string-value-that-equals-to-function-name
    funcs = globals()
    funcs = [
        v
        for k, v in funcs.items()
        if k.startswith("init_addons_uct_theses_file") and callable(v)
    ]
    for func in funcs:
        blueprint.record_once(func)

    return blueprint


def init_create_blueprint_from_app_uct_theses_file(state):
    """Init app."""
    app = state.app
    ext = app.extensions["uct_theses_file"]

    # register service
    sregistry = app.extensions["invenio-records-resources"].registry
    sregistry.register(ext.service, service_id="uct_theses_file")

    # Register indexer
    if hasattr(ext.service, "indexer"):
        iregistry = app.extensions["invenio-indexer"].registry
        iregistry.register(ext.service.indexer, indexer_id="uct_theses_file")


def create_blueprint_from_app_uct_theses_fileExt(app):
    """Create -ext blueprint."""
    blueprint = Blueprint("uct_theses_file-ext", __name__, url_prefix="uct_theses_file")
    blueprint.record_once(init_create_blueprint_from_app_uct_theses_file)

    # calls record_once for all other functions starting with "init_app_addons_"
    # https://stackoverflow.com/questions/58785162/how-can-i-call-function-with-string-value-that-equals-to-function-name
    funcs = globals()
    funcs = [
        v
        for k, v in funcs.items()
        if k.startswith("init_app_addons_uct_theses_file") and callable(v)
    ]
    for func in funcs:
        blueprint.record_once(func)

    return blueprint
