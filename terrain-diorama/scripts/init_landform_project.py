#!/usr/bin/env python3
"""Create a namespaced planning draft, without running any GIS or publishing."""

import argparse
import json
import math
from pathlib import Path
import re
import sys


def positive_number(value):
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("value must be a finite positive number")
    return number


def build_draft(args):
    root = Path(args.workspace).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("workspace must be an existing directory")
    if not re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", args.slug) or len(args.slug) > 48:
        raise ValueError("slug must be lowercase hyphen-case, start with a letter, and be at most 48 characters")
    if not re.fullmatch(r"v[0-9]+", args.version) or int(args.version[1:]) < 1:
        raise ValueError("version must be v followed by a positive integer, for example v01")
    if not args.title.strip():
        raise ValueError("title must not be empty")
    if args.style == "smooth" and args.height_step_m is not None:
        raise ValueError("height-step-m applies only to voxel style")
    if args.bbox:
        west, south, east, north = args.bbox
        if not all(math.isfinite(n) for n in args.bbox) or not (-180 <= west < east <= 180 and -90 <= south < north <= 90):
            raise ValueError("bbox must be W S E N in valid lon/lat order; dateline crossing needs a custom profile")

    run_id = args.slug.replace("-", "_") + "_" + args.version
    scene_root = f"projects/blender/{run_id}"
    namespaces = [f"work/{run_id}", f"renders/{run_id}", scene_root,
                  f"projects/web/public/data/{args.slug}", f"projects/web/public/models/{args.slug}",
                  f"projects/web/public/gallery/{args.slug}", f"deliverables/{args.slug}-{args.version}"]
    for relative in namespaces:
        candidate = root / relative
        if not candidate.resolve().is_relative_to(root):
            raise ValueError(f"namespace leaves the workspace: {relative}")
        if candidate.exists() or candidate.is_symlink():
            raise ValueError(f"namespace already exists; inspect it or select a new area/version: {relative}")

    catalog_path = root / "projects/web/public/data/areas.json"
    if catalog_path.exists():
        catalog = json.loads(catalog_path.read_text(encoding="utf-8-sig"))
        areas = catalog.get("areas") if isinstance(catalog, dict) else None
        if not isinstance(areas, list) or any(not isinstance(a, dict) for a in areas):
            raise ValueError("existing area catalog has an unexpected schema; inspect it before initialization")
        if any(area.get("id") == args.slug for area in areas):
            raise ValueError(f"area is already registered: {args.slug}")

    pending = ["sources", "projectedCrs", "displayOutline", "coreFeatures", "orbitLonLat", "palette", "views"]
    for key, value in [("bboxLonLat", args.bbox), ("cellSizeM", args.cell_m),
                       ("defaultExaggeration", args.exaggeration)]:
        if value is None:
            pending.append(key)
    if args.style == "voxel" and args.height_step_m is None:
        pending.append("heightStepM")

    draft = {
        "schema": "terrain-diorama-draft/v1", "status": "draft", "id": run_id,
        "area": args.slug, "title": args.title.strip(), "landform": args.landform,
        "style": args.style, "workRoot": f"work/{run_id}/views", "renderRoot": f"renders/{run_id}",
        "sceneRoot": scene_root, "galleryRoot": f"gallery/{args.slug}",
        "manifest": f"data/{args.slug}/manifest.json", "models": f"data/{args.slug}/models.json",
        "sources": {"dem": {"path": None, "resolutionM": None},
                    "imagery": {"path": None, "resolutionM": None}, "vectors": {"path": None}},
        "projectedCrs": None, "bboxLonLat": args.bbox,
        "displayOutline": {"kind": "terrain-guided-organic", "status": "pending",
                           "path": f"{scene_root}/display_outline.geojson", "boundaryGridM": args.cell_m},
        "coreFeatures": [], "cellSizeM": args.cell_m, "heightStepM": args.height_step_m,
        "defaultExaggeration": args.exaggeration,
        "exaggerations": sorted({1, args.exaggeration} if args.exaggeration is not None else {1}),
        "orbitLonLat": None, "seed": args.seed, "defaultPalette": None,
        "lodCandidatesM": [args.cell_m * stride for stride in (1, 2, 4, 8)] if args.cell_m else [],
        "triangleBudgets": {"desktop": 500000, "mobile": 150000}, "views": [],
        "pendingDecisions": pending,
    }
    if args.style == "voxel":
        draft["visualization"] = {"kind": "voxel", "cellSizeM": args.cell_m,
                                  "heightStepM": args.height_step_m, "decorativeElements": "schematic"}
    return root / scene_root / "config.draft.json", draft


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True, help="Existing workspace root")
    parser.add_argument("--slug", required=True, help="New web area ID, e.g. dawashan-jinkou")
    parser.add_argument("--title", required=True)
    parser.add_argument("--landform", required=True,
                        choices=["plateau-canyon", "river-confluence", "riverside-cliff", "other"])
    parser.add_argument("--style", choices=["voxel", "smooth"], default="voxel")
    parser.add_argument("--version", default="v01")
    parser.add_argument("--bbox", type=float, nargs=4, metavar=("W", "S", "E", "N"))
    parser.add_argument("--cell-m", type=positive_number)
    parser.add_argument("--height-step-m", type=positive_number)
    parser.add_argument("--exaggeration", type=positive_number)
    parser.add_argument("--seed", type=int, default=1, help="Recorded deterministic decoration seed (default: 1)")
    parser.add_argument("--dry-run", action="store_true", help="Print the draft without writing files")
    args = parser.parse_args()
    destination, draft = build_draft(args)
    if args.dry_run:
        result = {"destination": str(destination), "writes": False, "draft": draft}
    else:
        destination.parent.mkdir(parents=True, exist_ok=False)
        with destination.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(draft, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
        result = {"destination": str(destination), "status": "draft", "readyToRender": False,
                  "pendingDecisions": draft["pendingDecisions"]}
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(2)
