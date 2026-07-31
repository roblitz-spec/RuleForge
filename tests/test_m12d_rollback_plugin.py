"""Tests for M12-D RollbackPlugin — first capability plugin."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

from plugins.plugin_capability import PluginCapability
from plugins.plugin_registry import PluginRegistry
from plugins.rollback_plugin import (
    RollbackEntry,
    RollbackPlugin,
    RollbackResult,
)


# ── Helpers ───────────────────────────────────────────────────────

def _temp_file(dir_path: str, name: str, content: str = "x") -> str:
    p = Path(dir_path) / name
    p.write_text(content)
    return str(p)


# ── Plugin metadata & lifecycle ───────────────────────────────────


class TestRollbackPluginMetadata:
    def test_name(self) -> None:
        p = RollbackPlugin()
        assert p.name == "ruleforge.rollback"

    def test_version(self) -> None:
        p = RollbackPlugin()
        assert p.version == "1.0.0"

    def test_capability(self) -> None:
        p = RollbackPlugin()
        assert PluginCapability.EXECUTION_HOOK in p.metadata.capabilities

    def test_dependencies(self) -> None:
        p = RollbackPlugin()
        assert p.metadata.dependencies == ()


class TestRollbackPluginLifecycle:
    def test_full_lifecycle_in_registry(self) -> None:
        reg = PluginRegistry()
        p = RollbackPlugin()
        reg.register(p)
        assert reg.state("ruleforge.rollback") == "LOADED"
        reg.enable("ruleforge.rollback")
        assert reg.state("ruleforge.rollback") == "ENABLED"
        reg.activate("ruleforge.rollback")
        assert reg.state("ruleforge.rollback") == "ACTIVE"
        reg.deactivate("ruleforge.rollback")
        assert reg.state("ruleforge.rollback") == "ENABLED"
        reg.disable("ruleforge.rollback")
        assert reg.state("ruleforge.rollback") == "LOADED"

    def test_discovery_via_capability(self) -> None:
        reg = PluginRegistry()
        reg.register(RollbackPlugin())
        reg.enable("ruleforge.rollback")
        plugins = reg.list_by_capability(PluginCapability.EXECUTION_HOOK)
        assert len(plugins) == 1
        assert plugins[0].name == "ruleforge.rollback"

    def test_not_found_when_loaded_only(self) -> None:
        reg = PluginRegistry()
        reg.register(RollbackPlugin())
        assert (
            reg.list_by_capability(PluginCapability.EXECUTION_HOOK) == []
        )


# ── RollbackResult ────────────────────────────────────────────────


class TestRollbackResult:
    def test_empty_result(self) -> None:
        r = RollbackResult()
        assert r.total == 0
        assert r.success_rate == 1.0

    def test_all_restored(self) -> None:
        r = RollbackResult(restored=["a", "b"])
        assert r.total == 2
        assert r.success_rate == 1.0

    def test_mixed(self) -> None:
        r = RollbackResult(
            restored=["a"],
            failed=[("b", "permission denied")],
            skipped=1,
        )
        assert r.total == 3
        assert r.success_rate == 0.5

    def test_all_failed(self) -> None:
        r = RollbackResult(failed=[("a", "err")])
        assert r.success_rate == 0.0


# ── RollbackEntry ─────────────────────────────────────────────────


class TestRollbackEntry:
    def test_frozen(self) -> None:
        e = RollbackEntry(old_path="/old", new_path="/new")
        assert e.old_path == "/old"
        assert e.new_path == "/new"
        with pytest.raises(Exception):
            e.old_path = "/other"  # type: ignore[misc]


# ── Rollback: empty / no-op ───────────────────────────────────────


class TestRollbackEmpty:
    def test_empty_history_rollback(self) -> None:
        p = RollbackPlugin()
        result = p.rollback()
        assert result.restored == []
        assert result.failed == []
        assert result.total == 0

    def test_history_size_zero_initially(self) -> None:
        p = RollbackPlugin()
        assert p.history_size == 0

    def test_clear_empty_history(self) -> None:
        p = RollbackPlugin()
        p.clear_history()
        assert p.history_size == 0


# ── Rollback: success ─────────────────────────────────────────────


class TestRollbackSuccess:
    def test_single_rename_rollback(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            src = _temp_file(d, "old.txt", "hello")
            dst = str(Path(d) / "new.txt")

            os.rename(src, dst)
            assert not Path(src).exists()
            assert Path(dst).exists()

            p = RollbackPlugin()
            p.record_rename(old_path=src, new_path=dst)
            assert p.history_size == 1

            result = p.rollback()
            assert result.restored == [src]
            assert result.total == 1
            assert Path(src).exists()
            assert not Path(dst).exists()
            assert p.history_size == 0

    def test_multiple_renames_rollback_lifo(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            a = _temp_file(d, "a.txt", "a")
            b = _temp_file(d, "b.txt", "b")
            c = _temp_file(d, "c.txt", "c")

            a2 = str(Path(d) / "a2.txt")
            b2 = str(Path(d) / "b2.txt")
            c2 = str(Path(d) / "c2.txt")

            os.rename(a, a2)
            os.rename(b, b2)
            os.rename(c, c2)

            p = RollbackPlugin()
            p.record_rename(a, a2)
            p.record_rename(b, b2)
            p.record_rename(c, c2)
            assert p.history_size == 3

            result = p.rollback()
            assert result.restored == [c, b, a]  # LIFO order
            assert result.total == 3
            assert Path(a).exists()
            assert Path(b).exists()
            assert Path(c).exists()
            assert not Path(a2).exists()
            assert not Path(b2).exists()
            assert not Path(c2).exists()

    def test_history_cleared_after_rollback(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            src = _temp_file(d, "old.txt")
            dst = str(Path(d) / "new.txt")
            os.rename(src, dst)

            p = RollbackPlugin()
            p.record_rename(src, dst)
            p.rollback()
            assert p.history_size == 0


# ── Rollback: failure modes ───────────────────────────────────────


class TestRollbackFailure:
    def test_file_missing_skipped(self) -> None:
        p = RollbackPlugin()
        p.record_rename("/nonexistent/old.txt", "/nonexistent/new.txt")
        result = p.rollback()
        assert result.restored == []
        assert result.skipped == 1
        assert result.total == 1
        assert p.history_size == 0

    def test_target_already_exists_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            src = _temp_file(d, "old.txt", "hello")
            dst = str(Path(d) / "new.txt")

            os.rename(src, dst)
            # Recreate a file at the old path
            _temp_file(d, "old.txt", "blocker")

            p = RollbackPlugin()
            p.record_rename(src, dst)
            result = p.rollback()

            assert result.restored == []
            assert result.skipped == 1
            # new file should still exist
            assert Path(dst).exists()

    def test_partial_rollback_mixed_results(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            a = _temp_file(d, "a.txt", "a")
            b = _temp_file(d, "b.txt", "b")

            a2 = str(Path(d) / "a2.txt")
            b2 = str(Path(d) / "b2.txt")

            os.rename(a, a2)
            os.rename(b, b2)

            # Delete b2 to simulate missing file
            os.remove(b2)

            p = RollbackPlugin()
            p.record_rename(a, a2)
            p.record_rename(b, b2)

            result = p.rollback()
            # b2 missing → skipped, a2 present → restored
            assert "a.txt" in str(result.restored)
            assert result.skipped >= 1
            assert result.total == 2


# ── Integration with registry ─────────────────────────────────────


class TestRollbackRegistryIntegration:
    def test_activate_record_rollback_deactivate(self) -> None:
        reg = PluginRegistry()
        reg.register(RollbackPlugin())

        with tempfile.TemporaryDirectory() as d:
            src = _temp_file(d, "old.txt", "data")
            dst = str(Path(d) / "new.txt")
            os.rename(src, dst)

            reg.enable("ruleforge.rollback")
            reg.activate("ruleforge.rollback")

            plugin = reg.get("ruleforge.rollback")
            assert plugin is not None
            plugin.record_rename(src, dst)

            reg.deactivate("ruleforge.rollback")

            # Rollback still works after deactivation
            result = plugin.rollback()
            assert len(result.restored) == 1

    def test_history_persists_after_deactivate(self) -> None:
        reg = PluginRegistry()
        reg.register(RollbackPlugin())
        reg.enable("ruleforge.rollback")
        reg.activate("ruleforge.rollback")

        plugin = reg.get("ruleforge.rollback")
        assert plugin is not None
        plugin.record_rename("/x/y", "/x/z")
        assert plugin.history_size == 1

        reg.deactivate("ruleforge.rollback")
        # History survives deactivation
        assert plugin.history_size == 1

    def test_clear_history(self) -> None:
        p = RollbackPlugin()
        p.record_rename("/x/a", "/x/b")
        p.record_rename("/x/c", "/x/d")
        assert p.history_size == 2
        p.clear_history()
        assert p.history_size == 0


# ── Plugin independence ───────────────────────────────────────────


class TestPluginIndependence:
    def test_no_engine_imports(self) -> None:
        """RollbackPlugin must not import from engine/."""
        import plugins.rollback_plugin as rp

        source = rp.__file__
        assert source is not None
        with open(source) as f:
            content = f.read()
        assert "from engine" not in content
        assert "import engine" not in content

    def test_standalone_usage_without_registry(self) -> None:
        """Plugin works without a registry."""
        p = RollbackPlugin()
        assert p.history_size == 0
        p.record_rename("/a", "/b")
        assert p.history_size == 1
