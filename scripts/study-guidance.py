#!/usr/bin/env python3
"""Validate and derive StudySyndicate study material from portable guidance packets."""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "content/learning/study-guidance.v1.json"
TRIGGERS = {"requirements-gap", "application-iteration", "interview-feedback", "learning-event", "cascade", "manual"}
RESOURCE_KINDS = {"book", "documentation", "article", "course", "video", "repository", "problem-set"}
RELATIONS = {"primary", "reference", "remediation", "stretch"}
STATUSES = {"queued", "active", "completed", "superseded"}

class GuidanceError(ValueError):
    pass

def load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GuidanceError(f"{path}: {exc}") from exc

def req(obj, required, allowed, where):
    if not isinstance(obj, dict):
        raise GuidanceError(f"{where} must be object")
    missing = [key for key in required if key not in obj]
    extra = [key for key in obj if key not in allowed]
    if missing:
        raise GuidanceError(f"{where} missing: {', '.join(missing)}")
    if extra:
        raise GuidanceError(f"{where} unknown: {', '.join(extra)}")

def validate_packet(packet):
    req(packet, ("guidanceId", "origin", "trigger", "iteration", "concepts", "resources", "status"),
        ("guidanceId", "origin", "trigger", "iteration", "concepts", "resources", "status"), "packet")
    if not isinstance(packet["guidanceId"], str) or not packet["guidanceId"]:
        raise GuidanceError("guidanceId invalid")
    req(packet["origin"], ("system", "recordType", "recordId"), ("system", "recordType", "recordId"), "origin")
    if any(not isinstance(packet["origin"][key], str) or not packet["origin"][key] for key in ("system", "recordType", "recordId")):
        raise GuidanceError("origin values must be non-empty strings")
    req(packet["trigger"], ("kind", "reason"), ("kind", "reason", "cascadeConceptIds"), "trigger")
    if packet["trigger"]["kind"] not in TRIGGERS:
        raise GuidanceError("trigger.kind invalid")
    if not isinstance(packet["trigger"]["reason"], str) or not packet["trigger"]["reason"]:
        raise GuidanceError("trigger.reason invalid")
    casc = packet["trigger"].get("cascadeConceptIds", [])
    if not isinstance(casc, list) or any(not isinstance(x, str) or not x for x in casc):
        raise GuidanceError("trigger.cascadeConceptIds invalid")
    if not isinstance(packet["iteration"], int) or isinstance(packet["iteration"], bool) or packet["iteration"] < 1:
        raise GuidanceError("iteration must be integer >= 1")
    if packet["status"] not in STATUSES:
        raise GuidanceError("status invalid")
    if not isinstance(packet["concepts"], list) or not packet["concepts"]:
        raise GuidanceError("concepts must be non-empty array")
    concept_ids = set()
    for i, concept in enumerate(packet["concepts"]):
        req(concept, ("conceptId", "reason", "priority"), ("conceptId", "reason", "priority"), f"concepts[{i}]")
        if not isinstance(concept["conceptId"], str) or not concept["conceptId"]:
            raise GuidanceError(f"concepts[{i}].conceptId invalid")
        if concept["conceptId"] in concept_ids:
            raise GuidanceError("concept ids must be unique")
        concept_ids.add(concept["conceptId"])
        if not isinstance(concept["reason"], str) or not concept["reason"]:
            raise GuidanceError(f"concepts[{i}].reason invalid")
        if not isinstance(concept["priority"], int) or isinstance(concept["priority"], bool) or not 1 <= concept["priority"] <= 5:
            raise GuidanceError(f"concepts[{i}].priority must be 1..5")
    if not isinstance(packet["resources"], list):
        raise GuidanceError("resources must be array")
    for i, resource in enumerate(packet["resources"]):
        req(resource, ("kind", "title", "relation"), ("kind", "title", "relation", "author", "locator", "conceptIds", "note"), f"resources[{i}]")
        if resource["kind"] not in RESOURCE_KINDS:
            raise GuidanceError(f"resources[{i}].kind invalid")
        if resource["relation"] not in RELATIONS:
            raise GuidanceError(f"resources[{i}].relation invalid")
        if not isinstance(resource["title"], str) or not resource["title"]:
            raise GuidanceError(f"resources[{i}].title invalid")
        for key in ("author", "locator", "note"):
            if key in resource and (not isinstance(resource[key], str) or not resource[key]):
                raise GuidanceError(f"resources[{i}].{key} invalid")
        ids = resource.get("conceptIds", [])
        if not isinstance(ids, list) or any(x not in concept_ids for x in ids):
            raise GuidanceError(f"resources[{i}].conceptIds must reference packet concepts")
    return packet

def derive(packet):
    validate_packet(packet)
    materials = []
    for concept in sorted(packet["concepts"], key=lambda x: (-x["priority"], x["conceptId"])):
        materials.append({
            "materialKind": "generated-target",
            "conceptId": concept["conceptId"],
            "priority": concept["priority"],
            "reason": concept["reason"],
            "derivedFrom": "direct-guidance",
        })
    for concept_id in packet["trigger"].get("cascadeConceptIds", []):
        materials.append({
            "materialKind": "cascade-target",
            "conceptId": concept_id,
            "reason": packet["trigger"]["reason"],
            "derivedFrom": "cascade",
            "countsTowardMastery": False,
        })
    for resource in packet["resources"]:
        item = {
            "materialKind": "book-guidance" if resource["kind"] == "book" else "source-guidance",
            "resourceKind": resource["kind"],
            "title": resource["title"],
            "relation": resource["relation"],
            "conceptIds": resource.get("conceptIds", []),
            "derivedFrom": "resource",
            "countsTowardMastery": False,
        }
        for key in ("author", "locator", "note"):
            if key in resource:
                item[key] = resource[key]
        materials.append(item)
    return {
        "schema": "study-syndicate/derived-study-material/v1",
        "guidanceId": packet["guidanceId"],
        "origin": packet["origin"],
        "iteration": packet["iteration"],
        "status": packet["status"],
        "materials": materials,
    }

def validate_contract():
    contract = load(CONTRACT)
    if contract.get("schema") != "study-syndicate/study-guidance/v1" or contract.get("version") != 1:
        raise GuidanceError("study guidance contract identity mismatch")
    validate_packet(contract["examplePacket"])

def main():
    try:
        if len(sys.argv) == 2 and sys.argv[1] == "validate-contract":
            validate_contract()
            print("STUDY_GUIDANCE_CONTRACT: PASS")
            return 0
        if len(sys.argv) == 3 and sys.argv[1] == "validate":
            validate_contract(); validate_packet(load(Path(sys.argv[2])))
            print("STUDY_GUIDANCE_PACKET: PASS")
            return 0
        if len(sys.argv) == 3 and sys.argv[1] == "derive":
            validate_contract(); print(json.dumps(derive(load(Path(sys.argv[2]))), indent=2, sort_keys=True))
            return 0
        raise GuidanceError("usage: study-guidance.py validate-contract | validate PACKET.json | derive PACKET.json")
    except GuidanceError as exc:
        print(f"STUDY_GUIDANCE: FAIL: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
