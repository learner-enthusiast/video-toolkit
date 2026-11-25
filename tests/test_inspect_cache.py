import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

from tools import inspect_cache as ic

FAKE_PROBE = {"size": 2000, "duration": 1.0, "probe": "ok"}


def _patch_probe():
    return mock.patch.object(ic, "probe_meta", return_value=FAKE_PROBE.copy())


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
            allow_non_thorough=False,
        )

    def test_probe_meta_without_ffprobe(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as vf:
            vf.write(b"\x00" * 100)
            path = vf.name
        try:
            with mock.patch("subprocess.check_output", side_effect=FileNotFoundError):
                meta = ic.probe_meta(path)
            self.assertEqual(meta["probe"], "unavailable")
            self.assertEqual(meta["size"], 100)
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
            with open(os.path.join(insp, "contact_sheet.jpg"), "wb") as f:
                f.write(b"jpeg")
            args = SimpleNamespace(
                project=proj,
                video=video,
                mode="thorough",
                start=None,
                end=None,
                inspect_script=None,
                ocr_script=None,
                config_hash="",
                model_id="",
            )
            with mock.patch("sys.stdout", io.StringIO()):
                ic.cmd_store(SimpleNamespace(**{**args.__dict__, "inspect_dir": insp}))
            dest = os.path.join(proj, "work", "inspect", "restored")
            with mock.patch("sys.stdout", io.StringIO()):
                ic.cmd_restore(
                    SimpleNamespace(**{**args.__dict__, "out_dir": dest, "for_final": False, "force": True})
                )
            self.assertTrue(os.path.isfile(os.path.join(dest, "report.json")))
            self.assertTrue(os.path.isfile(os.path.join(dest, "contact_sheet.jpg")))

    @_patch_probe()
    def test_lookup_miss(self, _p):
        with tempfile.TemporaryDirectory() as td:
            proj = os.path.join(td, "p")
            os.makedirs(proj)
            video = os.path.join(proj, "v.mp4")
            with open(video, "wb") as f:
                f.write(b"x")
            args = SimpleNamespace(
                project=proj,
                video=video,
                mode="default",
                start=None,
                end=None,
                inspect_script=None,
                ocr_script=None,
                config_hash="",
                model_id="",
                for_final=False,
            )
            buf = io.StringIO()
            with mock.patch("sys.stdout", buf):
                with self.assertRaises(SystemExit) as cm:
                    ic.cmd_lookup(args)
            self.assertEqual(cm.exception.code, 1)
            out = json.loads(buf.getvalue())
            self.assertEqual(out["reason"], "miss")

    @_patch_probe()
    def test_final_lookup_always_miss_even_with_thorough_bundle(self, _p):
        with tempfile.TemporaryDirectory() as td:
            proj = os.path.join(td, "p")
            os.makedirs(proj)
            video = os.path.join(proj, "v.mp4")
            with open(video, "wb") as f:
                f.write(b"same")
            insp = os.path.join(proj, "work", "inspect", "v")
            os.makedirs(insp)
            with open(os.path.join(insp, "report.json"), "w") as f:
                f.write("{}")
            with open(os.path.join(insp, "contact_sheet.jpg"), "wb") as f:
                f.write(b"1")
            store_args = SimpleNamespace(
                project=proj,
                video=video,
                mode="thorough",
                start=None,
                end=None,
                inspect_script=None,
                ocr_script=None,
                config_hash="",
                model_id="",
                inspect_dir=insp,
            )
            with mock.patch("sys.stdout", io.StringIO()):
                ic.cmd_store(store_args)
            lookup_args = SimpleNamespace(
                project=proj,
                video=video,
                mode="thorough",
                start=None,
                end=None,
                inspect_script=None,
                ocr_script=None,
                config_hash="",
                model_id="",
                for_final=True,
            )
            buf = io.StringIO()
            with mock.patch("sys.stdout", buf):
                with self.assertRaises(SystemExit) as cm:
                    ic.cmd_lookup(lookup_args)
            self.assertEqual(cm.exception.code, 1)
            out = json.loads(buf.getvalue())
            self.assertEqual(out["reason"], "final_qa_requires_fresh_run")
            self.assertFalse(out["hit"])

    @_patch_probe()
    def test_final_restore_refused(self, _p):
        with tempfile.TemporaryDirectory() as td:
            proj = os.path.join(td, "p")
            os.makedirs(proj)
            video = os.path.join(proj, "v.mp4")
            with open(video, "wb") as f:
                f.write(b"x")
            insp = os.path.join(proj, "work", "inspect", "v")
            os.makedirs(insp)
            with open(os.path.join(insp, "report.json"), "w") as f:
                f.write("{}")
            with open(os.path.join(insp, "contact_sheet.jpg"), "wb") as f:
                f.write(b"j")
            with mock.patch("sys.stdout", io.StringIO()):
                ic.cmd_store(
                    SimpleNamespace(
                        project=proj,
                        video=video,
                        mode="thorough",
                        start=None,
                        end=None,
                        inspect_script=None,
                        ocr_script=None,
                        config_hash="",
                        model_id="",
                        inspect_dir=insp,
                    )
                )
            buf = io.StringIO()
            with mock.patch("sys.stdout", buf):
                with self.assertRaises(SystemExit) as cm:
                    ic.cmd_restore(
                        SimpleNamespace(
                            project=proj,
                            video=video,
                            mode="thorough",
                            start=None,
                            end=None,
                            inspect_script=None,
                            ocr_script=None,
                            config_hash="",
                            model_id="",
                            for_final=True,
                            force=True,
                            out_dir=None,
                        )
                    )
            self.assertEqual(cm.exception.code, 3)
            self.assertEqual(json.loads(buf.getvalue())["reason"], "final_qa_requires_fresh_run")

    @_patch_probe()
    def test_checksum_mismatch_rejected(self, _p):
        with tempfile.TemporaryDirectory() as td:
            proj = os.path.join(td, "p")
            os.makedirs(proj)
            video = os.path.join(proj, "v.mp4")
            with open(video, "wb") as f:
                f.write(b"v")
            insp = os.path.join(proj, "work", "inspect", "v")
            os.makedirs(insp)
            with open(os.path.join(insp, "report.json"), "w") as f:
                f.write("{}")
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
            key = ic.fingerprint(video, self._args(video, "default"))
            bundle = ic.bundle_dir(proj, key)
            with open(os.path.join(bundle, "report.json"), "w") as f:
                f.write('{"tampered": true}')
            buf = io.StringIO()
            with mock.patch("sys.stdout", buf):
                with self.assertRaises(SystemExit):
                    ic.cmd_lookup(
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
                            for_final=False,
                        )
                    )
            out = json.loads(buf.getvalue())
            self.assertTrue("checksum" in out["reason"] or "size_mismatch" in out["reason"])


if __name__ == "__main__":
    unittest.main()