#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

TASK = Path(__file__).resolve().parent
DEFAULT_CONTRACT = TASK / "final-challenge-contract-v1.json"
DEFAULT_FROZEN = TASK / "frozen-challenges-v1.json"
FORBIDDEN_GENERATOR_KEYS = {
    "candidate",
    "candidate_id",
    "candidate_name",
    "candidate_source_sha",
    "candidate_config",
    "candidate_configuration",
    "candidate_output",
    "candidate_result",
    "observed_result",
    "achieved_error",
}
REQUIRED_CLASSES = ["baseline", "boundary", "metamorphic", "corruption"]


def _reject_float_and_bad_keys(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise ValueError(f"binary floating-point authority is forbidden at {path}")
    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str):
                raise ValueError(f"non-string key at {path}")
            if key.lower() in FORBIDDEN_GENERATOR_KEYS:
                raise ValueError(f"candidate-derived generator input is forbidden: {path}.{key}")
            _reject_float_and_bad_keys(child, f"{path}.{key}")
    elif isinstance(value, list):
        for i, child in enumerate(value):
            _reject_float_and_bad_keys(child, f"{path}[{i}]")


def canonical_bytes(value: Any) -> bytes:
    _reject_float_and_bad_keys(value)
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_contract(contract: dict[str, Any]) -> None:
    _reject_float_and_bad_keys(contract)
    if contract.get("schema") != "radicadsac-mc049-final-challenge-contract/1.0":
        raise ValueError("wrong MC-049 contract schema")
    if contract.get("task") != "MC-049" or contract.get("issue") != 111:
        raise ValueError("wrong task or issue binding")
    if contract.get("status") != "FROZEN_PRESELECTION":
        raise ValueError("challenge contract is not frozen pre-selection")

    freeze = contract["freeze"]
    if freeze.get("must_precede") != "MC-026":
        raise ValueError("freeze must precede MC-026")
    if freeze.get("candidate_selection_observed_at_freeze") is not False:
        raise ValueError("freeze was not established before candidate selection")
    if freeze.get("candidate_identity_is_generator_input") is not False:
        raise ValueError("candidate identity cannot influence challenge generation")
    if freeze.get("candidate_feedback_may_change_cases") is not False:
        raise ValueError("candidate feedback cannot change frozen cases")

    custody = contract["custody"]
    if custody.get("classification") != "PUBLIC_PRESELECTION_PREREGISTRATION":
        raise ValueError("unsupported or overstated custody classification")
    if custody.get("independent_custodian") is not False:
        raise ValueError("MC-049 has no independent custodian")
    if custody.get("held_out") is not False or custody.get("secret_seed") is not False:
        raise ValueError("public MC-049 material must not be labelled held-out/secret")
    if custody.get("later_independent_execution_owner") != "MC-057":
        raise ValueError("independent challenge execution must remain routed to MC-057")

    gen = contract["generator"]
    seed = gen.get("seed_utf8")
    if not isinstance(seed, str) or not seed:
        raise ValueError("missing deterministic public seed")
    if sha256_hex(seed.encode("utf-8")) != gen.get("seed_sha256"):
        raise ValueError("seed commitment mismatch")
    if gen.get("algorithm_id") != "mc049-candidate-blind-final-challenge-v1":
        raise ValueError("generator algorithm/version drift")
    if gen.get("challenges_per_family") != 4:
        raise ValueError("challenge denominator drift")

    dependency_tasks = [x["task"] for x in contract["dependency_artifacts"]]
    if dependency_tasks != [
        "MC-005", "MC-009", "MC-010", "MC-011",
        "MC-012", "MC-013", "MC-014", "MC-015",
    ]:
        raise ValueError("MC-049 dependency set/order drift")
    for item in contract["dependency_artifacts"] + contract["source_pins"]:
        sha = item["blob_sha"]
        if not isinstance(sha, str) or len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
            raise ValueError(f"invalid Git blob pin: {item.get('path')}")

    if contract["required_families"] != [f"F{i:02d}" for i in range(1, 17)]:
        raise ValueError("mandatory F01-F16 denominator drift")
    if contract["required_challenge_classes"] != REQUIRED_CLASSES:
        raise ValueError("challenge class denominator drift")

    families = contract["families"]
    if [f["id"] for f in families] != contract["required_families"]:
        raise ValueError("family records do not match mandatory denominator")
    for family in families:
        if family.get("mandatory") is not True:
            raise ValueError(f"{family['id']} was optionalized")
        slots = family.get("challenge_slots")
        if not isinstance(slots, list) or len(slots) != 4:
            raise ValueError(f"{family['id']} must have four frozen challenge slots")
        if [s.get("class") for s in slots] != REQUIRED_CLASSES:
            raise ValueError(f"{family['id']} challenge class drift")
        if any(not isinstance(s.get("procedure"), str) or not s["procedure"] for s in slots):
            raise ValueError(f"{family['id']} has an empty procedure")
        if family.get("accuracy_profiles") != [
            "A-SEMANTIC", "A-ENGINEERING", "A-PRECISION-BOUNDARY"
        ]:
            raise ValueError(f"{family['id']} accuracy request drift")

    protected = contract["protected_semantics"]
    required_true = [
        "historical_rcs_sources_immutable",
        "source_audio_provenance_preserved",
        "canonical_journal_preserved",
        "positive_volume_material_noncompensating",
        "durable_body_identity_and_lineage_noncompensating",
    ]
    if any(protected.get(key) is not True for key in required_true):
        raise ValueError("protected semantics weakened")
    if protected.get("native_or_paid_execution_authorized") is not False:
        raise ValueError("MC-049 cannot authorize native/paid execution")

    verdict = contract["verdict_policy"]
    for key in (
        "timeout_is_pass",
        "resource_exhaustion_is_pass",
        "pending_or_refusal_is_pass",
        "candidate_success_is_oracle",
        "missing_mandatory_family_is_pass",
        "candidate_may_rewrite_expected_truth",
    ):
        if verdict.get(key) is not False:
            raise ValueError(f"invalid verdict policy: {key}")

    guard = contract["capability_guard"]
    if guard != {
        "MC-A": "ACCEPTED",
        "MC-B": "NOT_ESTABLISHED",
        "MC-C": "NOT_ESTABLISHED",
        "MC-D": "NOT_ESTABLISHED",
        "MC-E": "NOT_ESTABLISHED",
        "MC-F": "NOT_ESTABLISHED",
        "MC-1": "NOT_ESTABLISHED",
    }:
        raise ValueError("capability guard drift")


def _challenge_digest(seed: str, family: str, challenge_class: str, procedure: str) -> str:
    payload = "\0".join((seed, family, challenge_class, procedure)).encode("utf-8")
    return sha256_hex(payload)


def materialize(contract: dict[str, Any], contract_bytes: bytes) -> dict[str, Any]:
    validate_contract(contract)
    seed = contract["generator"]["seed_utf8"]
    records: list[dict[str, Any]] = []
    for family in contract["families"]:
        for slot in family["challenge_slots"]:
            digest = _challenge_digest(
                seed, family["id"], slot["class"], slot["procedure"]
            )
            records.append(
                {
                    "challenge_id": f"MC049-{family['id']}-{slot['class'].upper()}-{digest[:16]}",
                    "order_digest_sha256": digest,
                    "family": family["id"],
                    "class": slot["class"],
                    "procedure": slot["procedure"],
                    "corpus_path": family["corpus_path"],
                    "corpus_blob_sha": family["corpus_blob_sha"],
                    "oracle_path": family["oracle_path"],
                    "oracle_blob_sha": family["oracle_blob_sha"],
                    "accuracy_profiles": family["accuracy_profiles"],
                    "required_stages": family["required_stages"],
                    "execution_state": "FROZEN_NOT_EXECUTED",
                }
            )
    records.sort(key=lambda r: r["order_digest_sha256"])
    output = {
        "schema": "radicadsac-mc049-frozen-challenges/1.0",
        "task": "MC-049",
        "source_baseline": contract["source_baseline"],
        "contract_sha256": sha256_hex(contract_bytes),
        "generator_algorithm_id": contract["generator"]["algorithm_id"],
        "seed_sha256": contract["generator"]["seed_sha256"],
        "custody_classification": contract["custody"]["classification"],
        "held_out": False,
        "independent_custodian": False,
        "candidate_inputs": [],
        "mandatory_family_count": 16,
        "challenge_count": 64,
        "execution_authorized": False,
        "challenges": records,
    }
    _reject_float_and_bad_keys(output)
    return output


def adversarial_self_test(contract: dict[str, Any]) -> None:
    validate_contract(contract)

    mutations = []

    bad = copy.deepcopy(contract)
    bad["candidate_id"] = "preferred-provider"
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["generator"]["seed_utf8"] += "-changed"
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["required_families"].pop()
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["families"][0]["mandatory"] = False
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["families"][0]["challenge_slots"].pop()
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["families"][1]["accuracy_profiles"] = ["A-SEMANTIC"]
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["custody"]["held_out"] = True
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["custody"]["independent_custodian"] = True
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["verdict_policy"]["timeout_is_pass"] = True
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["protected_semantics"]["positive_volume_material_noncompensating"] = False
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["capability_guard"]["MC-B"] = "ACCEPTED"
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["families"][0]["tolerance"] = 0.001
    mutations.append(bad)

    rejected = 0
    for mutation in mutations:
        try:
            validate_contract(mutation)
        except (ValueError, KeyError, TypeError):
            rejected += 1
    if rejected != len(mutations):
        raise AssertionError(f"only {rejected}/{len(mutations)} adversarial mutations rejected")

    a = materialize(contract, canonical_bytes(contract))
    b = materialize(copy.deepcopy(contract), canonical_bytes(contract))
    if a != b:
        raise AssertionError("generator is not deterministic")
    if len(a["challenges"]) != 64:
        raise AssertionError("frozen denominator is not 64")
    if {c["family"] for c in a["challenges"]} != set(contract["required_families"]):
        raise AssertionError("not every mandatory family is represented")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify-materialized", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    raw = args.contract.read_bytes()
    contract = json.loads(raw.decode("utf-8"))
    validate_contract(contract)

    if args.self_test:
        adversarial_self_test(contract)

    generated = materialize(contract, raw)
    if args.verify_materialized:
        actual = load_json(args.verify_materialized)
        if canonical_bytes(actual) != canonical_bytes(generated):
            raise SystemExit("materialized challenge freeze differs from deterministic generator output")
    if args.output:
        args.output.write_text(json.dumps(generated, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if not (args.output or args.verify_materialized or args.self_test):
        print(json.dumps(generated, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
