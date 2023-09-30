# with thanks taken from https://github.com/inveniosoftware/pytest-invenio/blob/master/pytest_invenio/fixtures.py
import importlib_metadata
import pkg_resources
import pytest


class MockDistribution(pkg_resources.Distribution):
    """A mocked distribution that we can inject entry points with."""

    def __init__(self, extra_entry_points):
        """Initialise the extra entry point."""
        self._ep_map = {}
        # Create the entry point group map (which eventually will be used to
        # iterate over entry points). See source code for Distribution,
        # EntryPoint and WorkingSet in pkg_resources module.
        for group, entries in extra_entry_points.items():
            group_map = {}
            for ep_str in entries:
                ep = pkg_resources.EntryPoint.parse(ep_str)
                ep.require = self._require_noop
                group_map[ep.name] = ep
            self._ep_map[group] = group_map
        # Note location must have a non-empty string value, as it is used as a
        # key into a dictionary.
        super().__init__(location="unknown")

    def _require_noop(self, *args, **kwargs):
        """Do nothing on entry point require."""


class MockImportlibDistribution(importlib_metadata.Distribution):
    """A mocked distribution where we can inject entry points."""

    def __init__(self, extra_entry_points):
        """Entry points for the distribution."""
        self._entry_points = extra_entry_points

    @property
    def name(self):
        """Return the 'Name' metadata for the distribution package."""
        return "MockDistribution"

    @property
    def entry_points(self):
        """Iterate over entry points."""
        for group, eps_lines in self._entry_points.items():
            for ep_line in eps_lines:
                name, value = ep_line.split("=", maxsplit=1)
                yield importlib_metadata.EntryPoint(
                    # strip possible white space due to split on "="
                    name=name.strip(),
                    value=value.strip(),
                    group=group,
                )


@pytest.fixture(scope="module")
def entry_points(extra_entry_points):
    """Entry points fixture.

    Scope: module

    Invenio relies heavily on Python entry points for constructing an
    application and it can be rather cumbersome to try to register database
    models, search mappings etc yourself afterwards.

    This fixture allows you to inject extra entry points into the application
    loading, so that you can load e.g. a testing module or test mapping.

    To use the fixture simply define the ``extra_entry_points()`` fixture,
    and then depend on the ``entry_points()`` fixture in your ``create_app``
    fixture:

    .. code-block:: python

        @pytest.fixture(scope="module")
        def extra_entry_points():
            return {
                'invenio_db.models': [
                    'mock_module = mock_module.models',
                ]
            }

        @pytest.fixture(scope="module")
        def create_app(instance_path, entry_points):
            return _create_api
    """
    # Create mocked distributions
    pkg_resources_dist = MockDistribution(extra_entry_points)
    importlib_dist = MockImportlibDistribution(extra_entry_points)

    #
    # Patch importlib
    #
    old_distributions = importlib_metadata.distributions

    def distributions(**kwargs):
        for dist in old_distributions(**kwargs):
            yield dist
        yield importlib_dist

    importlib_metadata.distributions = distributions

    #
    # Patch pkg_resources
    #
    # First make a copy of the working_set state, so that we can restore the
    # state.
    workingset_state = pkg_resources.working_set.__getstate__()
    # Next, make a fake distribution that will yield the extra entry points and
    # add them to the global working_set.
    pkg_resources.working_set.add(pkg_resources_dist)

    yield pkg_resources_dist

    # Last, we restore the original workingset state and old importlib.
    pkg_resources.working_set.__setstate__(workingset_state)
    importlib_metadata.distributions = old_distributions


@pytest.fixture(scope="module")
def extra_entry_points():
    return {
        "oarepo_upload_cli.dependencies": [
            "source=tests.model_tests.test_source:TestSource",
            "repository=tests.model_tests.repository:TestRepositoryClient",
        ]
    }
