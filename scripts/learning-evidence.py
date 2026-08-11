#!/usr/bin/env python3
"""Deterministic StudySyndicate learning-evidence scorer.

This engine awards bounded partial credit for demonstrated facets, records assistance
as provenance, and emits acknowledgment-only cascade credit. It never claims mastery
from one event.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "content" / "learning" / "learning-evidence.v1.json"


def load_contract() -> dict[str, Any]:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def _index(contract: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    facets = {item["id"]: item for item in contract["facets"]}
    assistance = {item["id"]: item for item in contract["assistanceBands"]}
    return facets, assistance


def validate_event(event: dict[str, Any], contract: dict[str, Any]) -> None:
    required = contract["eventContract"]["required"]
    missing = [key for key in required if key not in event]
    if missing:
        raise ValueError(f"event missing required fields: {missing}")
    facets, assistance = _index(contract)
    if event["assistance"] not in assistance:
        raise ValueError(f"unknown assistance band: {event['assistance']}")
    if not isinstance(event["evidence"], list) or not event["evidence"]:
        raise ValueError("event evidence must be a non-empty list")
    seen: set[str] = set()
    for item in event["evidence"]:
        facet = item.get("facet")
        if facet not in facets:
            raise ValueError(f"unknown evidence facet: {facet}")
        if facet in seen:
            raise ValueError(f"duplicate evidence facet: {facet}")
        seen.add(facet)
        quality = item.get("quality")
        if not isinstance(quality, (int, float)) or isinstance(quality, bool) or not 0 <= quality <= 1:
            raise ValueError(f"facet quality must be between 0 and 1: {facet}")
    seen_cascade: set[str] = set()
    for item in event.get("cascade", []):
        concept_id = item.get("conceptId")
        if not concept_id:
            raise ValueError("cascade conceptId is required")
        if concept_id in seen_cascade:
            raise ValueError(f"duplicate cascade conceptId: {concept_id}")
        seen_cascade.add(concept_id)
        weight = item.get("relationWeight")
        if not isinstance(weight, (int, float)) or isinstance(weight, bool) or not 0 <= weight <= 1:
            raise ValueError("cascade relationWeight must be between 0 and 1")


def score_event(event: dict[str, Any], contract: dict[str, Any] | None = None) -> dict[str, Any]:
    contract = contract or load_contract()
    validate_event(event, contract)
    facets, assistance = _index(contract)
    band = assistance[event["assistance"]]

    facet_credit: dict[str, float] = {}
    quality_by_facet: dict[str, float] = {}
    for item in event["evidence"]:
        facet = facets[item["facet"]]
        quality = float(item["quality"])
        quality_by_facet[facet["id"]] = quality
        facet_credit[facet["id"]] = round(float(facet["weight"]) * quality, 4)

    raw_credit = round(sum(facet_credit.values()), 4)
    credit = round(min(raw_credit, float(band["maxEventCredit"])), 4)

    acknowledgements = sorted(contract["acknowledgementBands"], key=lambda x: float(x["minCredit"]))
    acknowledgement = acknowledgements[0]
    for candidate in acknowledgements:
        if credit >= float(candidate["minCredit"]):
            acknowledgement = candidate

    max_factor = float(contract["cascade"]["maxFactor"])
    cascades = [
        {
            "conceptId": item["conceptId"],
            "recognitionCredit": round(credit * max_factor * float(item["relationWeight"]), 4),
            "countsTowardMastery": False,
        }
        for item in event.get("cascade", [])
    ]

    mastery = contract["mastery"]
    required_facets = mastery["requiredFacets"]
    event_mastery_signal = bool(band["masterySignalAllowed"]) and all(
        quality_by_facet.get(facet, 0.0) >= float(mastery["minimumFacetQuality"])
        for facet in required_facets
    )

    earned = [
        {
            "facet": item["facet"],
            "quality": float(item["quality"]),
            "credit": facet_credit[item["facet"]],
        }
        for item in event["evidence"]
        if float(item["quality"]) > 0
    ]
    weakest = sorted(
        ({"facet": facet_id, "quality": quality_by_facet.get(facet_id, 0.0)} for facet_id in facets),
        key=lambda item: (item["quality"], item["facet"]),
    )[0]

    return {
        "eventId": event["eventId"],
        "conceptId": event["conceptId"],
        "assistance": event["assistance"],
        "rawCredit": raw_credit,
        "eventCredit": credit,
        "creditCap": float(band["maxEventCredit"]),
        "earnedFacets": earned,
        "weakestFacet": weakest,
        "acknowledgement": {
            "band": acknowledgement["id"],
            "message": acknowledgement["message"],
        },
        "cascadeRecognition": cascades,
        "eventMasterySignal": event_mastery_signal,
        "masteryClaimAllowed": False,
        "masteryBoundary": "Aggregate direct reps and transfer are required; derived cascade credit never counts toward mastery.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["score", "validate-contract"])
    parser.add_argument("event", nargs="?")
    args = parser.parse_args(argv)
    contract = load_contract()

    if args.command == "validate-contract":
        score_event(contract["exampleEvent"], contract)
        print("learning evidence contract PASS")
        return 0

    if not args.event:
        parser.error("score requires an event JSON path")
    event = json.loads(Path(args.event).read_text(encoding="utf-8"))
    print(json.dumps(score_event(event, contract), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        print(f"learning evidence FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
