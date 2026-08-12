import myproject.views as views


def test_views_public_exports_are_importable_and_callable():
    """Keep the views package export contract synchronized with its modules."""
    assert "render_weekly_digest_view" in views.__all__

    for name in views.__all__:
        assert hasattr(views, name), f"myproject.views does not export {name}"
        assert callable(getattr(views, name)), f"myproject.views.{name} is not callable"
