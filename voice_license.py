#!/usr/bin/env python3
"""Structural guard for the Talleyrand voice-license boundary.

The guard verifies that any quotation admitted to the voice record resolves to the
quotation-grade witness and a concrete page pin. It never certifies a complete or
correct reconstruction of Talleyrand's voice.
"""
from __future__ import annotations

from pathlib import Path
import yaml

PASS_STATUS = "STRUCTURAL_VOICE_PIN_PASS_NOT_VOICE_CERTIFICATION"


class VoiceLicenseError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise VoiceLicenseError(message)


def validate_voice_license(root: str | Path = ".") -> dict:
    root = Path(root)
    license_path = root / "speech/voice-license.yaml"
    _require(license_path.is_file(), "voice license missing")
    license_record = yaml.safe_load(license_path.read_text(encoding="utf-8"))
    _require(license_record.get("record_type") == "talleyrand_voice_license", "wrong voice record_type")
    _require(license_record.get("license", {}).get("granted") is False, "voice may not self-release")
    _require(license_record.get("status") == "READY_FOR_OWNER_RULING", "voice must remain at owner-ruling gate")
    _require(license_record.get("runtime") == "NOT_OPERATIONAL", "voice runtime must remain non-operational before owner ruling")

    formulation = license_record.get("single_preserved_formulation")
    _require(isinstance(formulation, dict), "single preserved formulation missing")
    _require(formulation.get("state") == "VERIFIED_PAGE_PINNED", "preserved formulation must be page-pinned")
    pin_rel = formulation.get("page_pin")
    _require(isinstance(pin_rel, str) and pin_rel, "page pin path missing")
    pin_path = root / pin_rel
    _require(pin_path.is_file(), "page pin record missing")
    pin = yaml.safe_load(pin_path.read_text(encoding="utf-8"))

    _require(pin.get("record_type") == "talleyrand_voice_page_pin", "wrong page-pin record_type")
    _require(pin.get("status") == "PAGE_PINNED_READY_FOR_OWNER_REVIEW", "page pin not ready for owner review")
    _require(pin.get("self_certification") == "PROHIBITED", "page pin may not self-certify")
    source = pin.get("source", {})
    _require(source.get("source_id") == "TAL-SRC-005", "voice pin must resolve to quotation-grade TAL-SRC-005")
    _require(source.get("letter", {}).get("number") == 4, "preserved formulation must resolve to Letter No. 4")
    _require(source.get("printed_page") == 35, "preserved formulation must resolve to printed page 35")
    image = pin.get("page_image_pin", {})
    _require(image.get("google_books", {}).get("volume_id") == "45YFAAAAQAAJ", "wrong Google Books page-image witness")
    _require(image.get("internet_archive", {}).get("item_id") == "correspondancei00louigoog", "wrong Internet Archive witness")
    _require(image.get("google_books", {}).get("page_label") == 35, "page-image label mismatch")

    french = pin.get("formulation", {}).get("french")
    _require(french == formulation.get("french"), "voice formulation differs from page-pin formulation")
    _require(pin.get("formulation", {}).get("modern_short_form_status") == "NOT_THE_VERBATIM_FORM", "popular short form must remain non-verbatim")
    _require(pin.get("license_effect", {}).get("releases_voice_license") is False, "page pin may not release the voice license")
    _require(pin.get("license_effect", {}).get("owner_ruling_still_required") is True, "owner ruling must remain required")

    return {"status": PASS_STATUS, "page_pin": pin.get("id"), "owner_ruling_required": True}
