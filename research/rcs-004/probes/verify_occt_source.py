#!/usr/bin/env python3
"""Verify source/API markers used by the RCS-004 OCCT 8.0.1 audit."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

EXPECTED_COMMIT = "b8f597c677811d1f9f4d8a97f5ae2825c0353a42"

CHECKS: dict[str, tuple[str, ...]] = {
    "adm/cmake/version.cmake": (
        "set (OCC_VERSION_MAJOR 8 )",
        "set (OCC_VERSION_MINOR 0 )",
        "set (OCC_VERSION_MAINTENANCE 1 )",
    ),
    "src/ModelingAlgorithms/TKBO/BOPAlgo/BOPAlgo_Options.hxx": (
        "SetFuzzyValue",
        "SetRunParallel",
        "GetParallelMode",
    ),
    "src/ModelingAlgorithms/TKBO/BOPAlgo/BOPAlgo_Builder.hxx": (
        "SetNonDestructive",
        "Images()",
        "Origins()",
        "ShapesSD()",
    ),
    "src/ModelingAlgorithms/TKBO/BOPAlgo/BOPAlgo_CellsBuilder.hxx": (
        "RemoveInternalBoundaries",
        "GetAllParts",
    ),
    "src/ModelingAlgorithms/TKShHealing/ShapeUpgrade/ShapeUpgrade_UnifySameDomain.hxx": (
        "SetLinearTolerance",
        "SetAngularTolerance",
        "SetSafeInputMode",
    ),
    "src/ModelingAlgorithms/TKTopAlgo/BRepCheck/BRepCheck_Analyzer.hxx": (
        "SetExactMethod",
        "SetParallel",
        "IsValid",
    ),
    "src/ModelingData/TKBRep/BRepTools/BRepTools_History.hxx": (
        "AddGenerated",
        "AddModified",
        "Remove",
        "Merge",
    ),
    "src/ModelingAlgorithms/TKOffset/BRepOffsetAPI/BRepOffsetAPI_MakePipeShell.hxx": (
        "SetTolerance",
        "SetTransitionMode",
        "ErrorOnSurface",
    ),
    "src/ModelingAlgorithms/TKMesh/BRepMesh/BRepMesh_IncrementalMesh.hxx": (
        "isInParallel",
        "SetParallelDefault",
    ),
    "src/DataExchange/TKDESTEP/STEPControl/STEPControl_Writer.hxx": (
        "DESTEP_Parameters",
        "SetShapeFixParameters",
        "SetTolerance",
    ),
    "src/DataExchange/TKDESTEP/DESTEP/DESTEP_Parameters.hxx": (
        "WriteSchema",
        "WriteUnit",
        "WritePrecisionMode",
    ),
    "src/DataExchange/TKXSBase/Interface/Interface_Static.hxx": (
        'used as "global" parameters',
        "SetCVal",
    ),
    "src/FoundationClasses/TKernel/Standard/Standard_Transient.hxx": (
        "std::atomic_int",
        "IncrementRefCounter",
        "DecrementRefCounter",
    ),
    "src/ModelingData/TKBRep/BRep/BRep_TFace.hxx": ("Tolerance() const",),
    "src/ModelingData/TKBRep/BRep/BRep_TEdge.hxx": (
        "Tolerance() const",
        "SameParameter",
        "SameRange",
    ),
    "src/ModelingData/TKBRep/BRep/BRep_TVertex.hxx": ("Tolerance() const",),
    "src/ModelingData/TKBRep/TopoDS/TopoDS_Shape.hxx": (
        "IsPartner",
        "IsSame",
        "IsEqual",
    ),
    "CMakeLists.txt": (
        'set (BUILD_CPP_STANDARD "C++17"',
        'set (BUILD_LIBRARY_TYPE "Shared"',
        "limitations on static linking with proprietary software",
    ),
    "OCCT_LGPL_EXCEPTION.txt": ("prominent notice",),
    "LICENSE_LGPL_21.txt": (
        'Use a suitable shared library mechanism for linking with the',
    ),
}


def fail(message: str) -> None:
    print(f"RCS-004 OCCT source verification failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    if len(sys.argv) != 2:
        fail("usage: verify_occt_source.py <path-to-OCCT-checkout>")

    root = Path(sys.argv[1]).resolve()
    if not root.is_dir():
        fail(f"not a directory: {root}")

    if (root / ".git").exists():
        try:
            head = subprocess.check_output(
                ["git", "-C", str(root), "rev-parse", "HEAD"],
                text=True,
                stderr=subprocess.STDOUT,
            ).strip()
        except (OSError, subprocess.CalledProcessError) as exc:
            fail(f"cannot resolve checkout revision: {exc}")
        if head != EXPECTED_COMMIT:
            fail(f"checkout is {head}, expected {EXPECTED_COMMIT}")
    else:
        print("note: no .git directory; verifying source markers without revision check")

    missing: list[str] = []
    for rel, markers in CHECKS.items():
        path = root / rel
        if not path.is_file():
            missing.append(f"missing file {rel}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for marker in markers:
            if marker not in text:
                missing.append(f"{rel}: missing marker {marker!r}")

    if missing:
        for item in missing:
            print(f" - {item}", file=sys.stderr)
        fail(f"{len(missing)} source marker check(s) failed")

    print(
        "RCS-004 OCCT source verification passed "
        f"({len(CHECKS)} source files checked against {EXPECTED_COMMIT})"
    )


if __name__ == "__main__":
    main()
