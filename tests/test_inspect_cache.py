import io
import json
import os
import shutil
import tempfile
import threading
import unittest
from types import SimpleNamespace
from unittest import mock

from tools import inspect_cache as ic

FAKE_PROBE = {"size": 2000, "duration": 1.0, "probe": "ok"}


def _patch_probe():
    return mock.patch.object(ic, "probe_meta", return_value=FAKE_PROBE.copy())


def _write_thorough_insp(base: str, *, with_sheet=True, with_kf=True, flags=None):
    os.makedirs(os.path.join(base, "keyframes"), exist_ok=True)
    report = {
        "scenes": [{"i": 0, "kf": "keyframes/scene_0.jpg"}] if with_kf else [{"i": 0}],
        "flags": flags or [],
    }
    with open(os.path.join(base, "report.json"), "w") as f:
        json.dump(report, f)
    with open(os.path.join(base, "contact_sheet.jpg"), "wb") as f:
        f.write(b"jpeg")
    if with_sheet:
        with open(os.path.join(base, "sheet_01.jpg"), "wb") as f:
            f.write(b"sheet")
    if with_kf:
        with open(os.path.join(base, "keyframes", "scene_0.jpg"), "wb") as f:
            f.write(b"kf")


class InspectCacheTest(unittest.TestCase):
    def _args(self, video, mode="default", **kw):
        return SimpleNamespace(
            video=video,
            mode=mode,
            start=kw.get("start"),
            end=kw.get("end"),
            inspect_script=kw.get("inspect_script"),
            ocr_script=kw.get("ocr_script"),
            config_hash=kw.get("config_hash", ""),
            model_id=kw.get("model_id", ""),
            for_final=kw.get("for_final", False),
        )

    def test_probe_meta_without_ffprobe(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as vf:
            vf.write(b"\x00" * 100)
            path = vf.name
        try:
            with mock.patch("subprocess.check_output", side_effect=FileNotFoundError):
                meta = ic.probe_meta(path)
            self.assertEqual(meta["probe"], "unavailable")
        finally:
            os.remove(path)

    @_patch_probe()
    def test_fingerprint_changes_with_mode(self, _p):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as vf:
            vf.write(b"\x00" * 2000)
            vpath = vf.name
        try:
            a = ic.fingerprint(vpath, self._args(vpath, "default"))
            b = ic.fingerprint(vpath, self._args(vpath, "thorough"))
            self.assertNotEqual(a, b)
        finally:
            os.remove(vpath)

    @_patch_probe()
    def test_store_restore_roundtrip_intermediate(self, _p):
        with tempfile.TemporaryDirectory() as td:
            proj = os.path.join(td, "p")
            os.makedirs(proj)
            video = os.path.join(proj, "out.mp4")
            with open(video, "wb") as f:
                f.write(b"video-bytes")
            insp = os.path.join(proj, "work", "inspect", "out")
            os.makedirs(insp, exist_ok=True)
            with open(os.path.join(insp, "report.json"), "w") as f:
                f.write("{}")
            args = self._store_args(proj, video, "default", insp)
            with mock.patch("sys.stdout", io.StringIO()):
                ic.cmd_store(args)
            dest = os.path.join(proj, "work", "inspect", "restored")
            with mock.patch("sys.stdout", io.StringIO()):
                ic.cmd_restore(self._restore_args(proj, video, "default", dest))
            self.assertTrue(os.path.isfile(os.path.join(dest, "report.json")))

    def _store_args(self, proj, video, mode, insp):
        return SimpleNamespace(
            project=proj,
            video=video,
            mode=mode,
            start=None,
            end=None,
            inspect_script=None,
            ocr_script=None,
            config_hash="",
            model_id="",
            inspect_dir=insp,
        )

    def _restore_args(self, proj, video, mode, dest, for_final=False):
        return SimpleNamespace(
            project=proj,
            video=video,
            mode=mode,
            start=None,
            end=None,
            inspect_script=None,
            ocr_script=None,
            config_hash="",
            model_id="",
            for_final=for_final,
            force=True,
            out_dir=dest,
        )

    @_patch_probe()
    def test_thorough_missing_sheet_rejected(self, _p):
        with tempfile.TemporaryDirectory() as td:
            proj = os.path.join(td, "p")
            os.makedirs(proj)
            video = os.path.join(proj, "v.mp4")
            with open(video, "wb") as f:
                f.write(b"v")
            insp = os.path.join(proj, "work", "inspect", "v")
            os.makedirs(insp)
            _write_thorough_insp(insp, with_sheet=False)
            with self.assertRaises(SystemExit):
                with mock.patch("sys.stdout", io.StringIO()):
                    ic.cmd_store(self._store_args(proj, video, "thorough", insp))

    @_patch_probe()
    def test_extra_unlisted_artifact_fails_lookup(self, _p):
        with tempfile.TemporaryDirectory() as td:
            proj, video, insp = self._thorough_project(td)
            with mock.patch("sys.stdout", io.StringIO()):
                ic.cmd_store(self._store_args(proj, video, "thorough", insp))
            key = ic.fingerprint(video, self._args(video, "thorough"))
            bundle = ic.bundle_dir(proj, key)
            with open(os.path.join(bundle, "extra.jpg"), "wb") as f:
                f.write(b"x")
            buf = io.StringIO()
            with mock.patch("sys.stdout", buf):
                with self.assertRaises(SystemExit):
                    ic.cmd_lookup(self._lookup_args(proj, video, "thorough"))
            self.assertIn("unlisted", json.loads(buf.getvalue())["reason"])

    def _thorough_project(self, td):
        proj = os.path.join(td, "p")
        os.makedirs(proj)
        video = os.path.join(proj, "v.mp4")
        with open(video, "wb") as f:
            f.write(b"v")
        insp = os.path.join(proj, "work", "inspect", "v")
        os.makedirs(insp)
        _write_thorough_insp(insp)
        return proj, video, insp

    def _lookup_args(self, proj, video, mode, for_final=False):
        return SimpleNamespace(
            project=proj,
            video=video,
            mode=mode,
            start=None,
            end=None,
            inspect_script=None,
            ocr_script=None,
            config_hash="",
            model_id="",
            for_final=for_final,
        )

    @_patch_probe()
    def test_path_traversal_in_report_rejected(self, _p):
        with tempfile.TemporaryDirectory() as td:
            proj = os.path.join(td, "p")
            video = os.path.join(proj, "v.mp4")
            os.makedirs(proj)
            with open(video, "wb") as f:
                f.write(b"v")
            insp = os.path.join(proj, "work", "inspect", "v")
            os.makedirs(insp)
            _write_thorough_insp(
                insp,
                flags=[{"t": 1, "type": "x", "frame": "../evil.jpg"}],
            )
            missing, reason = ic.validate_bundle(insp, True)
            self.assertEqual(reason, "unsafe_path_in_report")

    @_patch_probe()
    def test_symlink_escape_detected(self, _p):
        with tempfile.TemporaryDirectory() as td:
            outside = os.path.join(td, "outside")
            os.makedirs(outside)
            with open(os.path.join(outside, "secret"), "wb") as f:
                f.write(b"s")
            bundle = os.path.join(td, "bundle")
            os.makedirs(bundle)
            with open(os.path.join(bundle, "report.json"), "w") as f:
                json.dump({}, f)
            os.symlink(os.path.join(outside, "secret"), os.path.join(bundle, "leak"))
            with self.assertRaises(ValueError):
                ic.iter_bundle_artifact_paths(bundle)

    @_patch_probe()
    def test_concurrent_manifest_stores(self, _p):
        with tempfile.TemporaryDirectory() as td:
            proj, video, insp = self._thorough_project(td)
            keys = []
            errors = []

            def store_one(suffix):
                try:
                    v = os.path.join(proj, f"v_{suffix}.mp4")
                    with open(v, "wb") as f:
                        f.write(f"video-{suffix}".encode())
                    dinsp = os.path.join(proj, "work", "inspect", suffix)
                    shutil.copytree(insp, dinsp)
                    with mock.patch("sys.stdout", io.StringIO()):
                        ic.cmd_store(self._store_args(proj, v, "thorough", dinsp))
                    keys.append(ic.fingerprint(v, self._args(v, "thorough")))
                except Exception as exc:
                    errors.append(exc)

            threads = [threading.Thread(target=store_one, args=(str(i),)) for i in range(4)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            self.assertFalse(errors, errors)
            man = ic.load_manifest(proj)
            for k in keys:
                self.assertIn(k, man["entries"])

    @_patch_probe()
    def test_symlinked_directory_rejected(self, _p):
        with tempfile.TemporaryDirectory() as td:
            bundle = os.path.join(td, "bundle")
            sub = os.path.join(td, "realdir")
            os.makedirs(sub)
            with open(os.path.join(sub, "report.json"), "w") as f:
                json.dump({}, f)
            os.makedirs(bundle)
            os.symlink(sub, os.path.join(bundle, "nested"))
            with self.assertRaises(ValueError):
                ic.iter_bundle_artifact_paths(bundle)

    @_patch_probe()
    def test_integrity_json_wrong_top_level(self, _p):
        with tempfile.TemporaryDirectory() as td:
            bundle = os.path.join(td, "b")
            os.makedirs(bundle)
            with open(os.path.join(bundle, "integrity.json"), "w") as f:
                json.dump([1, 2, 3], f)
            ok, reason = ic.verify_integrity(bundle)
            self.assertFalse(ok)
            self.assertIn("corrupt_integrity", reason)

    @_patch_probe()
    def test_restore_malicious_bundle_dir(self, _p):
        with tempfile.TemporaryDirectory() as td:
            proj = os.path.join(td, "p")
            os.makedirs(proj)
            video = os.path.join(proj, "v.mp4")
            with open(video, "wb") as f:
                f.write(b"v")
            key = ic.fingerprint(video, self._args(video, "default"))
            good = ic.bundle_dir(proj, key)
            os.makedirs(good)
            with open(os.path.join(good, "report.json"), "w") as f:
                json.dump({}, f)
            ic.write_bundle_meta(good, {"key": key, "mode": "default"})
            ic.write_integrity_manifest(good, key, "default")
            man = {"schema": ic.CACHE_SCHEMA, "entries": {key: {"bundle_dir": "work/inspect/.cache/OTHER", "mode": "default", "fingerprint": key}}}
            os.makedirs(os.path.dirname(ic.manifest_path(proj)), exist_ok=True)
            with open(ic.manifest_path(proj), "w") as f:
                json.dump(man, f)
            with self.assertRaises(SystemExit) as ex:
                ic.cmd_restore(self._restore_args(proj, video, "default", os.path.join(proj, "out")))
            self.assertIn("bundle_dir_mismatch", str(ex.exception))

    @_patch_probe()
    def test_restore_preserves_dest_on_failure(self, _p):
        with tempfile.TemporaryDirectory() as td:
            proj = os.path.join(td, "p")
            outside = os.path.join(td, "outside")
            os.makedirs(outside)
            with open(os.path.join(outside, "secret"), "wb") as f:
                f.write(b"s")
            video = os.path.join(proj, "v.mp4")
            os.makedirs(proj)
            with open(video, "wb") as f:
                f.write(b"v")
            key = ic.fingerprint(video, self._args(video, "default"))
            bundle = ic.bundle_dir(proj, key)
            os.makedirs(bundle)
            with open(os.path.join(bundle, "report.json"), "w") as f:
                json.dump({}, f)
            os.symlink(outside, os.path.join(bundle, "leak"))
            dest = os.path.join(proj, "dest")
            os.makedirs(dest)
            with open(os.path.join(dest, "keep.txt"), "w") as f:
                f.write("stay")
            man = {
                "schema": ic.CACHE_SCHEMA,
                "entries": {key: {"bundle_dir": os.path.relpath(bundle, proj), "mode": "default", "fingerprint": key}},
            }
            with open(ic.manifest_path(proj), "w") as f:
                json.dump(man, f)
            with self.assertRaises(SystemExit):
                ic.cmd_restore(self._restore_args(proj, video, "default", dest))
            with open(os.path.join(dest, "keep.txt")) as f:
                self.assertEqual(f.read(), "stay")

    def test_manifest_entries_array_recovered_on_store(self, _p=None):
        with tempfile.TemporaryDirectory() as td:
            proj = os.path.join(td, "p")
            os.makedirs(proj)
            mp = ic.manifest_path(proj)
            os.makedirs(os.path.dirname(mp))
            with open(mp, "w") as f:
                json.dump({"schema": ic.CACHE_SCHEMA, "entries": []}, f)
            video = os.path.join(proj, "v.mp4")
            with open(video, "wb") as f:
                f.write(b"v")
            insp = os.path.join(proj, "work", "inspect", "v")
            os.makedirs(insp)
            with open(os.path.join(insp, "report.json"), "w") as f:
                json.dump({}, f)
            with mock.patch.object(ic, "probe_meta", return_value=FAKE_PROBE.copy()):
                with mock.patch("sys.stdout", io.StringIO()):
                    ic.cmd_store(
                        SimpleNamespace(
                            project=proj,
                            video=video,
                            mode="default",
                            start=None,
                            end=None,
                            inspect_script=None,
                            ocr_script=None,
                            config_hash="",
                            model_id="",
                            inspect_dir=insp,
                        )
                    )
            self.assertTrue(os.path.isfile(mp + ".corrupt"))
            man = ic.load_manifest(proj)
            self.assertIsInstance(man.get("entries"), dict)

    @_patch_probe()
    def test_final_lookup_and_restore_refused(self, _p):
        with tempfile.TemporaryDirectory() as td:
            proj, video, insp = self._thorough_project(td)
            with mock.patch("sys.stdout", io.StringIO()):
                ic.cmd_store(self._store_args(proj, video, "thorough", insp))
            buf = io.StringIO()
            with mock.patch("sys.stdout", buf):
                with self.assertRaises(SystemExit):
                    ic.cmd_lookup(self._lookup_args(proj, video, "thorough", for_final=True))
            self.assertEqual(json.loads(buf.getvalue())["reason"], "final_qa_requires_fresh_run")


if __name__ == "__main__":
    unittest.main()