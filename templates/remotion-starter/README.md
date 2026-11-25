# Remotion starter (toolkit)

Maintained scaffold for `projects/<name>/work/remotion/`. Version: Remotion **4.0.541** (`components/code/REMOTION_VERSION`).

**Apply after rough-cut approval:**

```bash
vt-python tools/scaffold_remotion.py projects/<name> --aspect 9:16
# or --aspect 16:9 for long-form main
```

Creates:

- `remotion.config.ts` with symlink/webpack overrides
- `tsconfig.json` with `preserveSymlinks`
- Symlinks `public/icons` → repo `icons/`, `src/shared` → `components/code/`
- `src/theme.ts` stub (fill from `brand.md`)
- `src/lib/layout.ts` — rect/constants stub (`components/specs/layout-states.md`)
- `src/Root.tsx` + `src/index.ts` — minimal Remotion registration
- `package.json` with scripts and Remotion version from `components/code/REMOTION_VERSION`
- `public/data/.gitkeep`

Does not copy scenes or timeline; `pipeline/composition.md` still owns storyboard and data build scripts.

**Upgrade:** bump version in `package.json` to match `REMOTION_VERSION`, re-render component `preview.png` files per `CLAUDE.md`.