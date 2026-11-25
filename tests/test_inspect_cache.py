import json
import os
import shutil
import tempfile
import unittest
from types import SimpleNamespace

from tools import inspect_cache as ic


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
            for_final=False,
            allow_non_thorough=False,
        )

    def test_fingerprint_changes_with_mode(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as vf:
            vf.write(b"\x00" * 2000)
            vpath = vf.name
        try:
            a = ic.fingerprint(vpath, self._args(vpath, "default"))
            b = ic.fingerprint(vpath, self._args(vpath, "thorough"))
            self.assertNotEqual(a, b)
        finally:
            os.remove(vpath)

    def test_store_restore_roundtrip(self):
        with tempfile.TemporaryDirectory() as td:
            proj = os.path.join(td, "p")
            os.makedirs(proj)
            video = os.path.join(proj, "out.mp4")
            open(video, "wb").write(b"video-bytes")
            insp = os.path.join(proj, "work", "inspect", "out")
            os.makedirs(insp, exist_ok=True)
            open(os.path.join(insp, "report.json"), "w").write("{}")
            open(os.path.join(insp, "contact_sheet.jpg"), "wb").write(b"jpeg")
            args = SimpleNamespace(
                project=proj,
                video=video,
                mode="thorough",
                start=None,
                end=None,
                inspect_script=None,
                ocr_script=None,
                config_hash="",
            )
            ic.cmd_store(SimpleNamespace(**{**args.__dict__, "inspect_dir": insp}))
            dest = os.path.join(proj, "work", "inspect", "restored")
            ic.cmd_restore(
                SimpleNamespace(
                    **{
                        **args.__dict__,
                        "out_dir": dest,
                        "for_final": False,
                        "force": True,
                    }
                )
            )
            self.assertTrue(os.path.isfile(os.path.join(dest, "report.json")))

    def test_lookup_miss(self):
        with tempfile.TemporaryDirectory() as td:
            proj = os.path.join(td, "p")
            os.makedirs(proj)
            video = os.path.join(proj, "v.mp4")
            open(video, "wb").write(b"x")
            args = SimpleNamespace(
                project=proj,
                video=video,
                mode="default",
                start=None,
                end=None,
                inspect_script=None,
                ocr_script=None,
                config_hash="",
                for_final=False,
                allow_non_thorough=False,
            )
            with self.assertRaises(SystemExit) as cm:
                ic.cmd_lookup(args)
            self.assertEqual(cm.exception.code, 1)

    def test_final_lookup_rejects_non_thorough_bundle(self):
        with tempfile.TemporaryDirectory() as td:
            proj = os.path.join(td, "p")
            os.makedirs(proj)
            video = os.path.join(proj, "v.mp4")
            open(video, "wb").write(b"same")
            insp = os.path.join(proj, "work", "inspect", "v")
            os.makedirs(insp)
            open(os.path.join(insp, "report.json"), "w").write("{}")
            open(os.path.join(insp, "contact_sheet.jpg"), "wb").write(b"1")
            store_args = SimpleNamespace(
                project=proj,
                video=video,
                mode="default",
                start=None,
                end=None,
                inspect_script=None,
                ocr_script=None,
                config_hash="",
                inspect_dir=insp,
            )
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
                for_final=True,
                allow_non_thorough=False,
            )
            with self.assertRaises(SystemExit):
                ic.cmd_lookup(lookup_args)


if __name__ == "__main__":
    unittest.main()