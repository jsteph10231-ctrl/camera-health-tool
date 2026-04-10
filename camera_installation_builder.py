import hashlib
import io
import json
import os
import re
import zipfile
import xml.etree.ElementTree as ET

from typing import Any

import pandas as pd  # type: ignore[import-untyped]
import streamlit as st  # type: ignore[import-untyped]
import streamlit.components.v1 as components  # type: ignore[import-untyped]


# Replace the workbook later by uploading a newer .xlsx on the builder tab or
# by pointing the workbook path at the new file. The parser below detects sheets
# and columns dynamically so routine workbook refreshes should not require code changes.
DEFAULT_WORKBOOK_NAME = "avigilon_camera_ordering_starter_updated.xlsx"
DEFAULT_WORKBOOK_PATHS = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", DEFAULT_WORKBOOK_NAME),
    os.path.join(os.path.expanduser("~"), "Downloads", DEFAULT_WORKBOOK_NAME),
]
FILTER_TAGS = [
    "Indoor",
    "Outdoor",
    "Corner",
    "Pole",
    "Wall",
    "Pendant",
    "Surface",
    "In-Ceiling",
    "Recessed",
    "Direct",
    "Conduit",
    "Wedge",
]
STATE_KEYS = [
    "cib_family",
    "cib_model",
    "cib_scenario",
    "cib_mount_type",
    "cib_environment",
    "cib_tags",
    "cib_quantity",
    "cib_required_only",
    "cib_debug_mode",
    "cib_result",
    "cib_result_context",
    "cib_last_workbook_hash",
]


def _clean(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        if pd.isna(value):
            return ""
        if value.is_integer():
            return str(int(value))
    text = str(value).strip()
    if text.lower() in {"nan", "none"}:
        return ""
    return re.sub(r"\s+", " ", text)


def _norm(value: Any) -> str:
    text = _clean(value).lower().replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def _tokens(value: Any) -> set[str]:
    return {token for token in _norm(value).split("_") if token}


def _unique_headers(headers: list[str]) -> list[str]:
    counts: dict[str, int] = {}
    output: list[str] = []
    for index, header in enumerate(headers, start=1):
        base_name = _norm(header) or f"column_{index}"
        count = counts.get(base_name, 0)
        counts[base_name] = count + 1
        output.append(base_name if count == 0 else f"{base_name}_{count + 1}")
    return output


def _excel_ref_to_index(cell_ref: str) -> int:
    match = re.match(r"([A-Z]+)", cell_ref or "")
    if not match:
        return 0
    value = 0
    for character in match.group(1):
        value = (value * 26) + (ord(character) - 64)
    return max(0, value - 1)


def _pick_column(columns: list[str], aliases: list[str]) -> str:
    alias_set = [_norm(alias) for alias in aliases]
    for alias in alias_set:
        for column in columns:
            if _norm(column) == alias:
                return column
    return ""


def _find_sheet_by_role(sheet_names: list[str], role: str) -> str:
    role_keywords = {
        "models": [("camera", "models"), ("camera", "model"), ("models",)],
        "accessories": [("accessories",), ("accessory", "library")],
        "bundles": [("mounting", "bundles"), ("bundle",), ("mount", "bundle")],
        "rules": [("family", "rules"), ("rules",)],
        "search_helper": [("search", "helper"), ("dropdown", "helper"), ("helper",)],
        "lists": [("lists",), ("scenario", "list")],
    }
    best_name = ""
    best_score = -1
    for sheet_name in sheet_names:
        score = 0
        sheet_tokens = _tokens(sheet_name)
        for keyword_group in role_keywords.get(role, []):
            if all(_norm(keyword) in sheet_tokens for keyword in keyword_group):
                score += 10 + len(keyword_group)
        if _norm(sheet_name) == role:
            score += 25
        if score > best_score:
            best_score = score
            best_name = sheet_name
    return best_name


@st.cache_data(show_spinner=False)
def load_workbook(workbook_bytes: bytes, workbook_name: str) -> dict[str, Any]:
    ns = {
        "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
        "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
    }
    workbook_hash = hashlib.sha1(workbook_bytes).hexdigest()[:12]
    workbook_errors: list[str] = []
    workbook_warnings: list[str] = []
    parsed_frames: dict[str, pd.DataFrame] = {}

    try:
        with zipfile.ZipFile(io.BytesIO(workbook_bytes)) as workbook_zip:
            shared_strings: list[str] = []
            if "xl/sharedStrings.xml" in workbook_zip.namelist():
                shared_root = ET.fromstring(workbook_zip.read("xl/sharedStrings.xml"))
                for string_item in shared_root.findall("main:si", ns):
                    shared_strings.append("".join(node.text or "" for node in string_item.findall(".//main:t", ns)))

            workbook_root = ET.fromstring(workbook_zip.read("xl/workbook.xml"))
            relationship_root = ET.fromstring(workbook_zip.read("xl/_rels/workbook.xml.rels"))
            relationship_map = {
                relation.attrib["Id"]: relation.attrib["Target"].lstrip("/")
                for relation in relationship_root.findall("{http://schemas.openxmlformats.org/package/2006/relationships}Relationship")
            }

            for sheet in workbook_root.findall("main:sheets/main:sheet", ns):
                sheet_name = sheet.attrib.get("name", "Sheet")
                relation_id = sheet.attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id", "")
                target = relationship_map.get(relation_id)
                if not target:
                    workbook_warnings.append(f"Could not resolve worksheet XML for sheet '{sheet_name}'.")
                    continue
                sheet_root = ET.fromstring(workbook_zip.read(target))
                raw_rows: list[list[str]] = []
                for row in sheet_root.findall(".//main:sheetData/main:row", ns):
                    row_values: dict[int, str] = {}
                    for cell in row.findall("main:c", ns):
                        cell_index = _excel_ref_to_index(cell.attrib.get("r", "A1"))
                        cell_type = cell.attrib.get("t")
                        cell_value = ""
                        if cell_type == "inlineStr":
                            cell_value = "".join(node.text or "" for node in cell.findall(".//main:t", ns))
                        else:
                            value_node = cell.find("main:v", ns)
                            if value_node is not None and value_node.text is not None:
                                cell_value = value_node.text
                                if cell_type == "s":
                                    try:
                                        cell_value = shared_strings[int(cell_value)]
                                    except Exception:
                                        pass
                        row_values[cell_index] = _clean(cell_value)
                    if row_values:
                        raw_rows.append([row_values.get(index, "") for index in range(max(row_values) + 1)])
                if not raw_rows:
                    parsed_frames[sheet_name] = pd.DataFrame()
                    continue
                header_index = next((i for i, row in enumerate(raw_rows[:10]) if len([cell for cell in row if _clean(cell)]) >= 2), 0)
                header_row = raw_rows[header_index]
                normalized_headers = _unique_headers([_clean(cell) for cell in header_row])
                width = len(normalized_headers)
                records: list[list[str]] = []
                source_rows: list[int] = []
                for source_row_number, row in enumerate(raw_rows[header_index + 1 :], start=header_index + 2):
                    padded = [_clean(row[index]) if index < len(row) else "" for index in range(width)]
                    if any(padded):
                        records.append(padded)
                        source_rows.append(source_row_number)
                sheet_df = pd.DataFrame(records, columns=normalized_headers)
                if not sheet_df.empty:
                    sheet_df = sheet_df.apply(lambda column: column.map(_clean))
                    sheet_df["_source_sheet"] = sheet_name
                    sheet_df["_source_row"] = source_rows
                parsed_frames[sheet_name] = sheet_df
    except Exception as exc:
        workbook_errors.append(f"Unable to read workbook '{workbook_name}': {exc}")

    sheet_names = list(parsed_frames.keys())
    return {
        "workbook_name": workbook_name,
        "workbook_hash": workbook_hash,
        "frames": parsed_frames,
        "sheet_roles": {
            "models": _find_sheet_by_role(sheet_names, "models"),
            "accessories": _find_sheet_by_role(sheet_names, "accessories"),
            "bundles": _find_sheet_by_role(sheet_names, "bundles"),
            "rules": _find_sheet_by_role(sheet_names, "rules"),
            "search_helper": _find_sheet_by_role(sheet_names, "search_helper"),
            "lists": _find_sheet_by_role(sheet_names, "lists"),
        },
        "errors": workbook_errors,
        "warnings": workbook_warnings,
    }


def _default_workbook_path() -> str:
    for candidate in DEFAULT_WORKBOOK_PATHS:
        if os.path.exists(candidate):
            return candidate
    return DEFAULT_WORKBOOK_PATHS[-1]


def _load_workbook_source(uploaded_workbook: Any, workbook_path: str) -> tuple[bytes | None, str, list[str]]:
    messages: list[str] = []
    if uploaded_workbook is not None:
        try:
            return uploaded_workbook.getvalue(), uploaded_workbook.name, messages
        except Exception as exc:
            messages.append(f"Uploaded workbook could not be read: {exc}")
            return None, "", messages
    normalized_path = _clean(workbook_path)
    if not normalized_path:
        messages.append("Provide a workbook path or upload an .xlsx file.")
        return None, "", messages
    if not os.path.exists(normalized_path):
        messages.append(f"Workbook file not found: {normalized_path}")
        return None, normalized_path, messages
    try:
        with open(normalized_path, "rb") as workbook_file:
            return workbook_file.read(), normalized_path, messages
    except Exception as exc:
        messages.append(f"Workbook file could not be opened: {exc}")
        return None, normalized_path, messages


def _apply_aliases(df: pd.DataFrame, alias_map: dict[str, list[str]]) -> pd.DataFrame:
    resolved_df = df.copy()
    current_columns = list(resolved_df.columns)
    for canonical_name, aliases in alias_map.items():
        matched_column = _pick_column(current_columns, [canonical_name] + aliases)
        if matched_column:
            resolved_df[canonical_name] = resolved_df[matched_column].map(_clean)
        elif canonical_name not in resolved_df.columns:
            resolved_df[canonical_name] = ""
    return resolved_df


def _join_notes(*values: Any) -> str:
    notes: list[str] = []
    for value in values:
        text = _clean(value)
        if text and text not in notes:
            notes.append(text)
    return " | ".join(notes)


def _model_description(model_row: pd.Series) -> str:
    pieces = [
        _clean(model_row.get("family", "")),
        _clean(model_row.get("camera_type", "")),
        _clean(model_row.get("resolution_mp", "")),
        "MP" if _clean(model_row.get("resolution_mp", "")) else "",
        _clean(model_row.get("lens_or_optics", "")),
        "IR" if _clean(model_row.get("ir", "")).lower() == "yes" else "",
    ]
    return re.sub(r"\s+", " ", " ".join(piece for piece in pieces if piece)).strip()


def _extract_tags(*values: Any) -> list[str]:
    combined = " ".join(_clean(value) for value in values if _clean(value)).lower()
    tag_rules = {
        "Indoor": ["indoor"],
        "Outdoor": ["outdoor"],
        "Corner": ["corner"],
        "Pole": ["pole"],
        "Wall": ["wall"],
        "Pendant": ["pendant", "npt"],
        "Surface": ["surface"],
        "In-Ceiling": ["in ceiling", "in-ceiling", "ceiling"],
        "Recessed": ["recessed"],
        "Direct": ["direct"],
        "Conduit": ["conduit"],
        "Wedge": ["wedge"],
    }
    tags = [tag for tag, markers in tag_rules.items() if any(marker in combined for marker in markers)]
    return sorted(set(tags), key=lambda tag: FILTER_TAGS.index(tag) if tag in FILTER_TAGS else 999)


def build_catalog(workbook_payload: dict[str, Any]) -> dict[str, Any]:
    frames: dict[str, pd.DataFrame] = workbook_payload.get("frames", {})
    sheet_roles: dict[str, str] = workbook_payload.get("sheet_roles", {})
    errors = list(workbook_payload.get("errors", []))
    warnings = list(workbook_payload.get("warnings", []))

    role_aliases = {
        "models": {
            "make": ["manufacturer"],
            "family": ["camera_family"],
            "series": [],
            "camera_type": ["type"],
            "indoor_outdoor": ["environment", "indoor_outdoor_use"],
            "base_mount": ["mount", "base_mount_type"],
            "model_number": ["model", "camera_model", "part_number"],
            "resolution_mp": ["resolution", "resolution_megapixels"],
            "lens_or_optics": ["lens", "optics"],
            "ir": [],
            "analytics": [],
            "microphone": ["audio"],
            "corner_mount_supported": ["corner_mount", "corner_mount_support"],
            "source_ref": ["source", "reference"],
        },
        "accessories": {
            "family": ["camera_family"],
            "accessory_part": ["part_number", "part"],
            "description": ["accessory_description"],
            "accessory_type": ["part_type", "type"],
            "applicable_to": ["applies_to"],
            "source_ref": ["source", "reference"],
        },
        "bundles": {
            "bundle_key": ["bundle", "key"],
            "model_number": ["model", "camera_model"],
            "family": ["camera_family"],
            "scenario": ["installation_scenario"],
            "notes": ["note", "warnings"],
            "required_parts_joined": ["required_parts"],
        },
        "rules": {
            "family": ["camera_family"],
            "supported_scenarios": ["scenario_list"],
            "rule": ["notes", "guidance"],
            "source_ref": ["source", "reference"],
        },
    }

    standardized_frames: dict[str, pd.DataFrame] = {}
    for role_name, aliases in role_aliases.items():
        sheet_name = sheet_roles.get(role_name, "")
        frame = frames.get(sheet_name, pd.DataFrame()).copy() if sheet_name else pd.DataFrame()
        if frame.empty and role_name in {"models", "accessories", "bundles"}:
            errors.append(f"Required workbook sheet for '{role_name}' was not found. Detected sheets: {', '.join(frames.keys()) or 'none'}.")
        standardized_frames[role_name] = _apply_aliases(frame, aliases) if not frame.empty else pd.DataFrame()

    models_df = standardized_frames["models"].copy()
    accessories_df = standardized_frames["accessories"].copy()
    bundles_df = standardized_frames["bundles"].copy()
    rules_df = standardized_frames["rules"].copy()

    if not models_df.empty:
        models_df["model_number"] = models_df["model_number"].map(_clean)
        models_df = models_df[models_df["model_number"].ne("")].copy()
        models_df["family"] = models_df["family"].map(_clean)
        models_df["make"] = models_df["make"].map(_clean).replace("", "Avigilon")
        models_df["camera_description"] = models_df.apply(_model_description, axis=1)
        models_df = models_df.drop_duplicates(subset=["model_number"], keep="first").reset_index(drop=True)

    if not accessories_df.empty:
        accessories_df["accessory_part"] = accessories_df["accessory_part"].map(_clean)
        accessories_df = accessories_df[accessories_df["accessory_part"].ne("")].copy()
        accessories_df["manufacturer"] = "Avigilon"
        accessories_df = accessories_df.drop_duplicates(subset=["family", "accessory_part", "description"], keep="first").reset_index(drop=True)

    if not bundles_df.empty:
        bundles_df["model_number"] = bundles_df["model_number"].map(_clean)
        bundles_df["family"] = bundles_df["family"].map(_clean)
        bundles_df["scenario"] = bundles_df["scenario"].map(_clean)
        bundles_df = bundles_df[(bundles_df["model_number"].ne("")) & (bundles_df["scenario"].ne(""))].copy()
        required_columns = sorted([column for column in bundles_df.columns if re.fullmatch(r"required_\d+", column)])
        optional_columns = sorted([column for column in bundles_df.columns if re.fullmatch(r"optional_\d+", column)])
        if not required_columns:
            errors.append("Mounting bundle sheet is missing required part columns such as Required_1.")
        bundles_df["required_columns"] = [required_columns] * len(bundles_df)
        bundles_df["optional_columns"] = [optional_columns] * len(bundles_df)
        bundles_df["scenario_tags"] = bundles_df.apply(lambda row: _extract_tags(row.get("scenario", ""), row.get("notes", "")), axis=1)
        bundles_df["mount_type"] = bundles_df["scenario_tags"].apply(
            lambda tags: next((tag for tag in tags if tag in {"Pendant", "Wall", "Pole", "Corner", "Surface", "In-Ceiling", "Recessed", "Direct", "Wedge"}), "")
        )
        bundles_df = bundles_df.drop_duplicates(
            subset=["model_number", "scenario", "required_parts_joined", "notes"] + required_columns + optional_columns,
            keep="first",
        ).reset_index(drop=True)

    if not rules_df.empty:
        rules_df["family"] = rules_df["family"].map(_clean)
        rules_df = rules_df[rules_df["family"].ne("")].copy()
        rules_df = rules_df.drop_duplicates(subset=["family", "supported_scenarios", "rule"], keep="first").reset_index(drop=True)

    if not bundles_df.empty and not models_df.empty:
        bundle_enrichment = models_df[["model_number", "make", "family", "camera_description", "indoor_outdoor", "base_mount"]].rename(columns={"family": "model_family"})
        bundles_df = bundles_df.merge(bundle_enrichment, on="model_number", how="left")
        bundles_df["family"] = bundles_df["family"].where(bundles_df["family"].ne(""), bundles_df["model_family"])

    return {
        "workbook_name": workbook_payload.get("workbook_name", ""),
        "workbook_hash": workbook_payload.get("workbook_hash", ""),
        "sheet_roles": sheet_roles,
        "models_df": models_df,
        "accessories_df": accessories_df,
        "bundles_df": bundles_df,
        "rules_df": rules_df,
        "errors": errors,
        "warnings": warnings,
    }


def filter_bundle_candidates(
    catalog: dict[str, Any],
    family: str = "",
    model_number: str = "",
    scenario: str = "",
    mount_type: str = "",
    environment: str = "",
    tags: list[str] | None = None,
) -> pd.DataFrame:
    bundles_df = catalog.get("bundles_df", pd.DataFrame()).copy()
    if bundles_df.empty:
        return bundles_df
    filtered = bundles_df.copy()
    selected_tags = [_clean(tag) for tag in tags or [] if _clean(tag)]
    if family:
        filtered = filtered[filtered["family"].eq(family)]
    if model_number:
        filtered = filtered[filtered["model_number"].eq(model_number)]
    if scenario:
        filtered = filtered[filtered["scenario"].eq(scenario)]
    if mount_type:
        filtered = filtered[filtered["mount_type"].eq(mount_type)]
    if environment:
        filtered = filtered[filtered["indoor_outdoor"].fillna("").str.contains(re.escape(environment), case=False, na=False)]
    if selected_tags:
        filtered = filtered[filtered["scenario_tags"].apply(lambda row_tags: all(tag in row_tags for tag in selected_tags))]
    return filtered


def _merge_bom_parts(parts: list[dict[str, Any]], quantity_multiplier: int) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    merged_parts: dict[tuple[str, str], dict[str, Any]] = {}
    debug_rows: list[dict[str, Any]] = []
    for part in parts:
        part_number = _clean(part.get("part_number", ""))
        requirement = _clean(part.get("required_optional", "Required")) or "Required"
        merge_key = (part_number, requirement)
        base_quantity = max(1, int(part.get("base_quantity", 1) or 1))
        effective_quantity = base_quantity * quantity_multiplier
        if merge_key not in merged_parts:
            merged_parts[merge_key] = {
                "Part Type": _clean(part.get("part_type", "")),
                "Manufacturer": _clean(part.get("manufacturer", "")),
                "Part Number": part_number,
                "Description": _clean(part.get("description", "")),
                "Required Qty": effective_quantity,
                "Required/Optional": requirement,
                "Notes": _clean(part.get("notes", "")),
            }
        else:
            merged_parts[merge_key]["Required Qty"] += effective_quantity
            merged_parts[merge_key]["Notes"] = _join_notes(merged_parts[merge_key]["Notes"], part.get("notes", ""))
        debug_rows.extend(part.get("debug_rows", []))
    bom_df = pd.DataFrame(list(merged_parts.values()))
    if not bom_df.empty:
        bom_df = bom_df.sort_values(by=["Required/Optional", "Part Type", "Part Number"]).reset_index(drop=True)
    return bom_df, debug_rows


def _resolve_part_details(
    part_reference: str,
    requirement: str,
    model_row: pd.Series,
    accessories_df: pd.DataFrame,
    bundle_row: pd.Series,
) -> dict[str, Any]:
    family = _clean(model_row.get("family", "")) or _clean(bundle_row.get("family", ""))
    if part_reference == "CAMERA":
        return {
            "part_type": "Camera",
            "manufacturer": _clean(model_row.get("make", "")) or "Avigilon",
            "part_number": _clean(model_row.get("model_number", "")),
            "description": _clean(model_row.get("camera_description", "")) or _clean(model_row.get("family", "")),
            "required_optional": requirement,
            "notes": _join_notes(_clean(model_row.get("source_ref", ""))),
            "base_quantity": 1,
            "debug_rows": [{
                "Match Type": "Camera model",
                "Sheet": _clean(model_row.get("_source_sheet", "")),
                "Row": _clean(model_row.get("_source_row", "")),
                "Reason": f"Matched model {_clean(model_row.get('model_number', ''))}",
            }],
        }

    accessory_matches = accessories_df[accessories_df["accessory_part"].eq(part_reference)].copy()
    family_matches = accessory_matches[accessory_matches["family"].eq(family)] if not accessory_matches.empty else accessory_matches
    selected_matches = family_matches if not family_matches.empty else accessory_matches
    if selected_matches.empty:
        return {
            "part_type": "Accessory",
            "manufacturer": "Avigilon",
            "part_number": part_reference,
            "description": "Referenced by mounting bundle but not found in accessory library.",
            "required_optional": requirement,
            "notes": "Verify workbook accessory library entry for this part.",
            "base_quantity": 1,
            "debug_rows": [{
                "Match Type": "Missing accessory metadata",
                "Sheet": _clean(bundle_row.get("_source_sheet", "")),
                "Row": _clean(bundle_row.get("_source_row", "")),
                "Reason": f"Bundle references {part_reference} but accessory sheet match was not found.",
            }],
        }

    accessory_row = selected_matches.iloc[0]
    ambiguity_note = ""
    descriptions = {_clean(value) for value in selected_matches["description"].tolist() if _clean(value)}
    if len(descriptions) > 1:
        ambiguity_note = "Workbook contains multiple accessory descriptions for this part; first matching row shown."
    return {
        "part_type": _clean(accessory_row.get("accessory_type", "")) or "Accessory",
        "manufacturer": _clean(accessory_row.get("manufacturer", "")) or "Avigilon",
        "part_number": _clean(accessory_row.get("accessory_part", "")),
        "description": _clean(accessory_row.get("description", "")),
        "required_optional": requirement,
        "notes": _join_notes(_clean(accessory_row.get("applicable_to", "")), ambiguity_note, _clean(accessory_row.get("source_ref", ""))),
        "base_quantity": 1,
        "debug_rows": [{
            "Match Type": f"{requirement} accessory",
            "Sheet": _clean(accessory_row.get("_source_sheet", "")),
            "Row": _clean(accessory_row.get("_source_row", "")),
            "Reason": f"Matched accessory part {part_reference}",
        }],
    }


def build_installation_package(catalog: dict[str, Any], model_number: str, scenario: str, quantity: int) -> dict[str, Any]:
    models_df = catalog.get("models_df", pd.DataFrame())
    bundles_df = catalog.get("bundles_df", pd.DataFrame())
    accessories_df = catalog.get("accessories_df", pd.DataFrame())
    rules_df = catalog.get("rules_df", pd.DataFrame())
    debug_rows: list[dict[str, Any]] = []
    notes: list[str] = []
    warnings: list[str] = []

    if models_df.empty or bundles_df.empty:
        return {"status": "error", "message": "Workbook did not load the required camera model and mounting bundle sheets.", "debug_df": pd.DataFrame()}

    model_matches = models_df[models_df["model_number"].eq(model_number)].copy()
    if model_matches.empty:
        return {"status": "error", "message": f"Camera model '{model_number}' was not found in the current workbook.", "debug_df": pd.DataFrame()}
    model_row = model_matches.iloc[0]
    debug_rows.append({
        "Match Type": "Camera model",
        "Sheet": _clean(model_row.get("_source_sheet", "")),
        "Row": _clean(model_row.get("_source_row", "")),
        "Reason": f"Selected model {model_number}",
    })

    matching_bundles = bundles_df[(bundles_df["model_number"].eq(model_number)) & (bundles_df["scenario"].eq(scenario))].copy()
    if matching_bundles.empty:
        family_rule_matches = rules_df[rules_df["family"].eq(_clean(model_row.get("family", "")))].copy() if not rules_df.empty else pd.DataFrame()
        for _, rule_row in family_rule_matches.iterrows():
            notes.append(_join_notes(rule_row.get("supported_scenarios", ""), rule_row.get("rule", ""), rule_row.get("source_ref", "")))
            debug_rows.append({
                "Match Type": "Family rule",
                "Sheet": _clean(rule_row.get("_source_sheet", "")),
                "Row": _clean(rule_row.get("_source_row", "")),
                "Reason": f"No bundle found; surfaced family rule for {_clean(rule_row.get('family', ''))}",
            })
        return {
            "status": "no_bundle",
            "message": "No defined installation bundle found for this combination in the current workbook.",
            "camera_summary": {
                "make": _clean(model_row.get("make", "")),
                "family": _clean(model_row.get("family", "")),
                "model_number": _clean(model_row.get("model_number", "")),
                "description": _clean(model_row.get("camera_description", "")),
            },
            "notes": [note for note in notes if note],
            "debug_df": pd.DataFrame(debug_rows),
        }

    if len(matching_bundles) > 1:
        unique_signatures = {
            tuple(_clean(bundle_row.get(column, "")) for column in bundle_row.index if column.startswith("required_") or column.startswith("optional_") or column in {"notes", "required_parts_joined"})
            for _, bundle_row in matching_bundles.iterrows()
        }
        if len(unique_signatures) > 1:
            for _, bundle_row in matching_bundles.iterrows():
                debug_rows.append({
                    "Match Type": "Ambiguous bundle",
                    "Sheet": _clean(bundle_row.get("_source_sheet", "")),
                    "Row": _clean(bundle_row.get("_source_row", "")),
                    "Reason": f"Multiple bundle rows matched {model_number} + {scenario}",
                })
            return {
                "status": "ambiguous",
                "message": "Multiple bundle rows matched this model/scenario combination. Review the debug details instead of using a guessed package.",
                "debug_df": pd.DataFrame(debug_rows),
            }
    bundle_row = matching_bundles.iloc[0]
    debug_rows.append({
        "Match Type": "Mounting bundle",
        "Sheet": _clean(bundle_row.get("_source_sheet", "")),
        "Row": _clean(bundle_row.get("_source_row", "")),
        "Reason": f"Matched scenario {scenario}",
    })

    family_rule_matches = rules_df[rules_df["family"].eq(_clean(model_row.get("family", "")))].copy() if not rules_df.empty else pd.DataFrame()
    for _, rule_row in family_rule_matches.iterrows():
        supported = _clean(rule_row.get("supported_scenarios", ""))
        notes.append(_join_notes(supported, rule_row.get("rule", ""), rule_row.get("source_ref", "")))
        debug_rows.append({
            "Match Type": "Family rule",
            "Sheet": _clean(rule_row.get("_source_sheet", "")),
            "Row": _clean(rule_row.get("_source_row", "")),
            "Reason": f"Applied family note for {_clean(rule_row.get('family', ''))}",
        })
        if supported and scenario not in supported:
            warnings.append(f"Scenario '{scenario}' is not listed in family supported scenarios: {supported}")

    if _clean(bundle_row.get("notes", "")):
        notes.append(_clean(bundle_row.get("notes", "")))

    raw_parts: list[dict[str, Any]] = []
    for requirement, columns in [("Required", bundle_row.get("required_columns", []) or []), ("Optional", bundle_row.get("optional_columns", []) or [])]:
        for column_name in columns:
            part_reference = _clean(bundle_row.get(column_name, ""))
            if part_reference:
                raw_parts.append(_resolve_part_details(part_reference, requirement, model_row, accessories_df, bundle_row))

    bom_df, part_debug_rows = _merge_bom_parts(raw_parts, max(1, int(quantity or 1)))
    debug_rows.extend(part_debug_rows)
    return {
        "status": "ok",
        "message": "",
        "camera_summary": {
            "make": _clean(model_row.get("make", "")),
            "family": _clean(model_row.get("family", "")),
            "model_number": _clean(model_row.get("model_number", "")),
            "description": _clean(model_row.get("camera_description", "")),
            "environment": _clean(model_row.get("indoor_outdoor", "")),
            "base_mount": _clean(model_row.get("base_mount", "")),
            "scenario": _clean(bundle_row.get("scenario", "")),
        },
        "required_df": bom_df[bom_df["Required/Optional"].eq("Required")].reset_index(drop=True) if not bom_df.empty else pd.DataFrame(),
        "optional_df": bom_df[bom_df["Required/Optional"].eq("Optional")].reset_index(drop=True) if not bom_df.empty else pd.DataFrame(),
        "bom_df": bom_df,
        "notes": [note for note in notes if note],
        "warnings": [warning for warning in warnings if warning],
        "debug_df": pd.DataFrame(debug_rows),
    }


def _render_copy_button(text: str, key: str, label: str = "Copy BOM") -> None:
    payload = json.dumps(text)
    message_id = f"{key}_copy_message"
    components.html(
        f"""
        <div style="display:flex; align-items:center; gap:12px; margin:0.2rem 0 0.8rem 0;">
            <button
                style="background:#5d8667; color:#f7fbf7; border:none; border-radius:8px; padding:0.55rem 0.9rem; font-weight:700; cursor:pointer;"
                onclick='navigator.clipboard.writeText({payload}).then(function(){{document.getElementById("{message_id}").innerText="Copied to clipboard";}}).catch(function(){{document.getElementById("{message_id}").innerText="Clipboard copy failed";}});'
            >{label}</button>
            <span id="{message_id}" style="font-family:sans-serif; font-size:0.9rem; color:#d8dfeb;"></span>
        </div>
        """,
        height=60,
    )


def _format_export_text(camera_summary: dict[str, str], bom_df: pd.DataFrame, notes: list[str]) -> str:
    output_lines = [
        "Camera Installation Builder BOM",
        f"Camera: {_clean(camera_summary.get('model_number', ''))}",
        f"Family: {_clean(camera_summary.get('family', ''))}",
        f"Scenario: {_clean(camera_summary.get('scenario', ''))}",
        "",
    ]
    if not bom_df.empty:
        output_lines.append("Required/Optional | Qty | Part Number | Description")
        for _, row in bom_df.iterrows():
            output_lines.append(
                f"{_clean(row.get('Required/Optional', ''))} | {_clean(row.get('Required Qty', ''))} | "
                f"{_clean(row.get('Part Number', ''))} | {_clean(row.get('Description', ''))}"
            )
    if notes:
        output_lines.extend(["", "Notes:"])
        output_lines.extend([f"- {note}" for note in notes])
    return "\n".join(output_lines).strip()


def reset_builder_state() -> None:
    widget_defaults = {
        "cib_workbook_path": _default_workbook_path(),
        "cib_family": "",
        "cib_model": "",
        "cib_scenario": "",
        "cib_mount_type": "",
        "cib_environment": "",
        "cib_tags": [],
        "cib_quantity": 1,
        "cib_required_only": False,
        "cib_debug_mode": False,
    }
    for state_key in STATE_KEYS:
        st.session_state.pop(state_key, None)
    for state_key, default_value in widget_defaults.items():
        st.session_state[state_key] = default_value
    st.session_state.pop("cib_workbook_upload", None)
    st.session_state.pop("cib_reset_pending", None)


def _sync_single_select_state(key: str, options: list[str]) -> str:
    current_value = _clean(st.session_state.get(key, ""))
    valid_options = [""] + [option for option in options if _clean(option)]
    if current_value not in valid_options:
        st.session_state[key] = ""
        return ""
    return current_value


def _sync_multi_select_state(key: str, options: list[str]) -> list[str]:
    valid_option_set = {option for option in options if _clean(option)}
    current_values = [_clean(value) for value in st.session_state.get(key, []) if _clean(value)]
    filtered_values = [value for value in current_values if value in valid_option_set]
    if filtered_values != current_values:
        st.session_state[key] = filtered_values
    return filtered_values


def render_builder() -> None:
    st.markdown("## Camera Installation Builder")
    st.caption("Build workbook-backed Avigilon installation packages in four steps: choose a workbook, choose a camera, choose an install scenario, then review the generated BOM.")
    components.html(
        """
        <style>
        .cib-shell {
            --cib-field-bg: rgba(250, 252, 253, 0.99);
            --cib-field-border: rgba(84, 110, 122, 0.24);
            --cib-field-focus: rgba(53, 126, 155, 0.42);
            --cib-copy: #5c6d77;
            --cib-heading: #31414a;
        }
        .cib-shell .cib-step-title {
            margin: 0.16rem 0 0.12rem 0 !important;
            color: var(--cib-heading);
            font-size: 0.92rem;
            font-weight: 760;
            line-height: 1.1;
        }
        .cib-shell .cib-step-copy {
            margin: 0 0 0.18rem 0 !important;
            color: var(--cib-copy);
            font-size: 0.75rem;
            line-height: 1.22;
        }
        .cib-shell .cib-muted-caption {
            margin: 0.05rem 0 0.08rem 0 !important;
            color: #6b7e88;
            font-size: 0.71rem;
            line-height: 1.18;
        }
        .cib-shell h3,
        .cib-shell h4,
        .cib-shell h5,
        .cib-shell p,
        .cib-shell label,
        .cib-shell span {
            color: inherit;
        }
        .cib-shell div[data-testid="stAlert"] {
            border: 1px solid rgba(84, 110, 122, 0.18);
        }
        .cib-shell div[data-testid="stTextInput"] input,
        .cib-shell div[data-testid="stSelectbox"] [data-baseweb="select"] > div,
        .cib-shell div[data-testid="stMultiSelect"] [data-baseweb="select"] > div,
        .cib-shell div[data-testid="stNumberInput"] input {
            background: var(--cib-field-bg) !important;
            border: 1px solid var(--cib-field-border) !important;
            color: #33424b !important;
        }
        .cib-shell div[data-testid="stTextInput"] input::placeholder,
        .cib-shell div[data-testid="stNumberInput"] input::placeholder {
            color: #84939c !important;
        }
        .cib-shell div[data-testid="stTextInput"] input:focus,
        .cib-shell div[data-testid="stNumberInput"] input:focus,
        .cib-shell div[data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within,
        .cib-shell div[data-testid="stMultiSelect"] [data-baseweb="select"] > div:focus-within {
            border-color: var(--cib-field-focus) !important;
        }
        .cib-shell div[data-testid="stButton"] > button,
        .cib-shell div[data-testid="stDownloadButton"] > button {
            border: 1px solid rgba(84, 110, 122, 0.22) !important;
            background: linear-gradient(180deg, rgba(255,255,255,0.99), rgba(238,244,247,0.99)) !important;
            color: #325061 !important;
        }
        .cib-shell div[data-testid="stButton"] > button:hover,
        .cib-shell div[data-testid="stDownloadButton"] > button:hover {
            border-color: rgba(53, 126, 155, 0.42) !important;
            background: linear-gradient(180deg, rgba(244,250,252,0.99), rgba(225,236,241,0.99)) !important;
            color: #284759 !important;
        }
        .cib-shell .st-key-cib_build button {
            background: linear-gradient(180deg, #4a859d, #357e9b) !important;
            color: #ffffff !important;
            border-color: #357e9b !important;
        }
        .cib-shell .st-key-cib_workbook_upload [data-testid="stFileUploader"] section {
            background: linear-gradient(180deg, rgba(250,252,253,0.99), rgba(236,242,245,0.99));
            border: 1px dashed rgba(84, 110, 122, 0.3);
        }
        .cib-shell .st-key-cib_workbook_upload [data-testid="stFileUploaderDropzone"] {
            background: transparent;
            border: none;
        }
        .cib-shell .st-key-cib_workbook_upload [data-testid="stFileUploaderDropzoneInstructions"] span,
        .cib-shell .st-key-cib_workbook_upload [data-testid="stFileUploaderDropzoneInstructions"] small,
        .cib-shell .st-key-cib_workbook_upload [data-testid="stFileUploader"] button {
            color: #4e6470 !important;
        }
        .cib-shell div[data-testid="stCheckbox"] label,
        .cib-shell div[data-testid="stCheckbox"] p,
        .cib-shell .stCaptionContainer,
        .cib-shell div[data-testid="stMarkdownContainer"] p {
            color: var(--cib-copy);
        }
        .cib-shell div[data-testid="stDataFrame"] {
            border: 1px solid rgba(84, 110, 122, 0.16);
            background: rgba(255, 255, 255, 0.98);
        }
        .cib-shell div[data-testid="stExpander"] {
            background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(239,244,247,0.98));
            border: 1px solid rgba(84, 110, 122, 0.18);
        }
        .cib-shell div[data-testid="stExpander"] details summary p,
        .cib-shell div[data-testid="stExpander"] details summary span {
            color: #40525c !important;
        }
        .st-key-cib_workbook_upload,
        .st-key-cib_workbook_path,
        .st-key-cib_family,
        .st-key-cib_model,
        .st-key-cib_scenario,
        .st-key-cib_mount_type,
        .st-key-cib_environment,
        .st-key-cib_tags,
        .st-key-cib_quantity,
        .st-key-cib_required_only,
        .st-key-cib_debug_mode {
            margin-bottom: 0.04rem !important;
        }
        .st-key-cib_workbook_upload label[data-testid="stWidgetLabel"],
        .st-key-cib_workbook_path label[data-testid="stWidgetLabel"],
        .st-key-cib_family label[data-testid="stWidgetLabel"],
        .st-key-cib_model label[data-testid="stWidgetLabel"],
        .st-key-cib_scenario label[data-testid="stWidgetLabel"],
        .st-key-cib_mount_type label[data-testid="stWidgetLabel"],
        .st-key-cib_environment label[data-testid="stWidgetLabel"],
        .st-key-cib_tags label[data-testid="stWidgetLabel"],
        .st-key-cib_quantity label[data-testid="stWidgetLabel"] {
            margin-bottom: 0.02rem !important;
        }
        .st-key-cib_workbook_upload label[data-testid="stWidgetLabel"] p,
        .st-key-cib_workbook_path label[data-testid="stWidgetLabel"] p,
        .st-key-cib_family label[data-testid="stWidgetLabel"] p,
        .st-key-cib_model label[data-testid="stWidgetLabel"] p,
        .st-key-cib_scenario label[data-testid="stWidgetLabel"] p,
        .st-key-cib_mount_type label[data-testid="stWidgetLabel"] p,
        .st-key-cib_environment label[data-testid="stWidgetLabel"] p,
        .st-key-cib_tags label[data-testid="stWidgetLabel"] p,
        .st-key-cib_quantity label[data-testid="stWidgetLabel"] p {
            font-size: 0.74rem !important;
            line-height: 1.05 !important;
            margin: 0 !important;
        }
        .st-key-cib_workbook_path input,
        .st-key-cib_family [data-baseweb="select"] > div,
        .st-key-cib_model [data-baseweb="select"] > div,
        .st-key-cib_scenario [data-baseweb="select"] > div,
        .st-key-cib_mount_type [data-baseweb="select"] > div,
        .st-key-cib_environment [data-baseweb="select"] > div,
        .st-key-cib_tags [data-baseweb="select"] > div,
        .st-key-cib_quantity input {
            min-height: 1.95rem !important;
            height: 1.95rem !important;
            font-size: 0.81rem !important;
        }
        .st-key-cib_workbook_upload [data-testid="stFileUploader"] {
            margin-bottom: 0.08rem !important;
        }
        .st-key-cib_workbook_upload [data-testid="stFileUploaderDropzone"] {
            padding-top: 0.32rem !important;
            padding-bottom: 0.32rem !important;
            min-height: 3.55rem !important;
        }
        .st-key-cib_workbook_upload [data-testid="stFileUploaderDropzoneInstructions"] span,
        .st-key-cib_workbook_upload [data-testid="stFileUploaderDropzoneInstructions"] small {
            font-size: 0.74rem !important;
            line-height: 1.1 !important;
        }
        .st-key-cib_workbook_upload button {
            min-height: 1.85rem !important;
            height: 1.85rem !important;
        }
        .st-key-cib_required_only,
        .st-key-cib_debug_mode {
            padding-top: 0.05rem !important;
            margin-top: -0.02rem !important;
        }
        .st-key-cib_required_only label,
        .st-key-cib_debug_mode label {
            min-height: 1.2rem !important;
        }
        .st-key-cib_required_only p,
        .st-key-cib_debug_mode p {
            font-size: 0.78rem !important;
            margin: 0 !important;
            line-height: 1.12 !important;
        }
        .st-key-cib_build button,
        .st-key-cib_clear button {
            min-height: 2rem !important;
            height: 2rem !important;
            padding-top: 0.18rem !important;
            padding-bottom: 0.18rem !important;
        }
        </style>
        """,
        height=0,
    )
    st.markdown('<div class="cib-shell">', unsafe_allow_html=True)

    if st.session_state.get("cib_reset_pending"):
        reset_builder_state()

    st.session_state.setdefault("cib_workbook_path", _default_workbook_path())
    st.session_state.setdefault("cib_quantity", 1)
    st.session_state.setdefault("cib_tags", [])
    st.session_state.setdefault("cib_required_only", False)
    st.session_state.setdefault("cib_debug_mode", False)

    left_col, right_col = st.columns([1.06, 1.34], gap="small")

    with left_col:
        st.markdown('<div class="cib-step-title">Step 1 · Workbook</div>', unsafe_allow_html=True)
        st.markdown('<div class="cib-step-copy">Choose the ordering workbook that powers the builder. Repo-local <code>data/</code> is the best long-term location on this machine.</div>', unsafe_allow_html=True)
        uploaded_workbook = st.file_uploader(
            "Upload workbook",
            type=["xlsx"],
            key="cib_workbook_upload",
            help="Optional: upload a newer Avigilon workbook without changing code.",
        )
        workbook_path = st.text_input("Workbook path", key="cib_workbook_path")
        workbook_bytes, workbook_label, source_messages = _load_workbook_source(uploaded_workbook, workbook_path)
        for message in source_messages:
            st.error(message)

        if workbook_bytes is None:
            st.info(
                "Builder workbook not loaded yet. Upload the Avigilon ordering workbook or point the workbook path at a local .xlsx file to enable this feature."
            )

        catalog: dict[str, Any] = {}
        if workbook_bytes is not None:
            catalog = build_catalog(load_workbook(workbook_bytes, workbook_label))
            if st.session_state.get("cib_last_workbook_hash") != catalog.get("workbook_hash"):
                st.session_state["cib_result"] = None
                st.session_state["cib_result_context"] = None
                st.session_state["cib_last_workbook_hash"] = catalog.get("workbook_hash")

            if catalog.get("workbook_name"):
                st.markdown(f'<div class="cib-muted-caption">Loaded workbook: {catalog["workbook_name"]}</div>', unsafe_allow_html=True)
            for warning in catalog.get("warnings", []):
                st.warning(warning)
            for error in catalog.get("errors", []):
                st.error(error)

            models_df = catalog.get("models_df", pd.DataFrame())
            bundles_df = catalog.get("bundles_df", pd.DataFrame())

            if not models_df.empty and not bundles_df.empty:
                st.markdown('<div class="cib-step-title">Step 2 · Camera</div>', unsafe_allow_html=True)
                families = sorted(family for family in models_df["family"].dropna().astype(str).unique().tolist() if family)
                selected_family = _sync_single_select_state("cib_family", families)
                family_col, model_col = st.columns(2, gap="small")
                with family_col:
                    selected_family = st.selectbox("Camera family", options=[""] + families, key="cib_family")

                models_scope = filter_bundle_candidates(catalog, family=selected_family)
                model_options = (
                    sorted(models_scope["model_number"].dropna().astype(str).unique().tolist())
                    if not models_scope.empty
                    else sorted(models_df["model_number"].dropna().astype(str).unique().tolist())
                )
                _sync_single_select_state("cib_model", model_options)
                with model_col:
                    selected_model = st.selectbox("Camera model", options=[""] + model_options, key="cib_model")

                st.markdown('<div class="cib-step-title">Step 3 · Installation Scenario</div>', unsafe_allow_html=True)
                scenarios_scope = filter_bundle_candidates(catalog, family=selected_family, model_number=selected_model)
                scenario_options = (
                    sorted(scenarios_scope["scenario"].dropna().astype(str).unique().tolist())
                    if not scenarios_scope.empty
                    else sorted(bundles_df["scenario"].dropna().astype(str).unique().tolist())
                )
                _sync_single_select_state("cib_scenario", scenario_options)
                scenario_col, mount_col = st.columns(2, gap="small")
                with scenario_col:
                    selected_scenario = st.selectbox("Installation scenario", options=[""] + scenario_options, key="cib_scenario")

                mount_scope = filter_bundle_candidates(
                    catalog,
                    family=selected_family,
                    model_number=selected_model,
                    scenario=selected_scenario,
                )
                mount_type_options = (
                    sorted(mount_scope["mount_type"].dropna().astype(str).unique().tolist())
                    if not mount_scope.empty
                    else sorted(bundles_df["mount_type"].dropna().astype(str).unique().tolist())
                )
                _sync_single_select_state("cib_mount_type", mount_type_options)
                with mount_col:
                    selected_mount_type = st.selectbox("Mount type", options=[""] + mount_type_options, key="cib_mount_type")

                environment_scope = filter_bundle_candidates(
                    catalog,
                    family=selected_family,
                    model_number=selected_model,
                    scenario=selected_scenario,
                    mount_type=selected_mount_type,
                )
                environment_options = (
                    sorted(environment_scope["indoor_outdoor"].dropna().astype(str).unique().tolist())
                    if not environment_scope.empty
                    else sorted(models_df["indoor_outdoor"].dropna().astype(str).unique().tolist())
                )
                _sync_single_select_state("cib_environment", environment_options)
                environment_col, tags_col = st.columns(2, gap="small")
                with environment_col:
                    selected_environment = st.selectbox("Environment", options=[""] + environment_options, key="cib_environment")

                tag_scope = filter_bundle_candidates(
                    catalog,
                    family=selected_family,
                    model_number=selected_model,
                    scenario=selected_scenario,
                    mount_type=selected_mount_type,
                    environment=selected_environment,
                )
                tag_options = sorted(
                    {
                        tag
                        for row_tags in tag_scope.get("scenario_tags", pd.Series(dtype=object)).tolist()
                        for tag in (row_tags or [])
                        if _clean(tag)
                    },
                    key=lambda tag: FILTER_TAGS.index(tag) if tag in FILTER_TAGS else 999,
                ) if not tag_scope.empty else FILTER_TAGS
                _sync_multi_select_state("cib_tags", tag_options)
                with tags_col:
                    st.multiselect("Optional filters", options=tag_options, key="cib_tags")

                st.markdown('<div class="cib-step-title">Step 4 · Output Options</div>', unsafe_allow_html=True)
                output_col, option_col = st.columns(2, gap="small")
                with output_col:
                    st.number_input("Camera quantity", min_value=1, step=1, key="cib_quantity")
                    st.checkbox("Show only required parts in results", key="cib_required_only")
                with option_col:
                    st.checkbox("Debug / provenance mode", key="cib_debug_mode")

                build_col, clear_col = st.columns(2)
                with build_col:
                    if st.button("Build Installation Package", key="cib_build", use_container_width=True):
                        requested_model = _clean(st.session_state.get("cib_model", ""))
                        requested_scenario = _clean(st.session_state.get("cib_scenario", ""))
                        if not requested_model or not requested_scenario:
                            st.session_state["cib_result"] = {
                                "status": "error",
                                "message": "Select both a camera model and an installation scenario before building the package.",
                                "debug_df": pd.DataFrame(),
                            }
                        else:
                            st.session_state["cib_result"] = build_installation_package(
                                catalog,
                                requested_model,
                                requested_scenario,
                                int(st.session_state.get("cib_quantity", 1) or 1),
                            )
                            st.session_state["cib_result_context"] = {
                                "workbook_name": catalog.get("workbook_name", ""),
                                "workbook_hash": catalog.get("workbook_hash", ""),
                                "sheet_roles": catalog.get("sheet_roles", {}),
                            }
                with clear_col:
                    if st.button("Clear", key="cib_clear", use_container_width=True):
                        st.session_state["cib_reset_pending"] = True
                        st.rerun()

                st.caption(
                    "Detected workbook sheets: "
                    + ", ".join(f"{role} -> {sheet_name or 'not found'}" for role, sheet_name in catalog.get("sheet_roles", {}).items())
                )
            else:
                st.info("The workbook loaded, but the required camera model or mounting bundle sheets were not detected yet.")

    with right_col:
        st.markdown("### Generated package")
        st.caption("Review the workbook-backed parts list, then copy or export the package details.")
        result = st.session_state.get("cib_result")
        result_context = st.session_state.get("cib_result_context") or {}
        if not result:
            st.info("Choose a model and scenario, then click Build Installation Package to generate the workbook-backed bill of materials.")
            return

        status = result.get("status", "")
        if status == "error":
            st.error(_clean(result.get("message", "Unable to build installation package.")))
        elif status == "no_bundle":
            st.warning(_clean(result.get("message", "No defined installation bundle found for this combination in the current workbook.")))
        elif status == "ambiguous":
            st.error(_clean(result.get("message", "Multiple workbook rows matched this combination.")))
        else:
            st.success("Installation package built from workbook data.")

        camera_summary = result.get("camera_summary", {}) or {}
        if camera_summary:
            st.caption("Package summary")
            info_col_1, info_col_2 = st.columns(2)
            with info_col_1:
                st.markdown("##### Camera Selection")
                st.write(f"Make: {_clean(camera_summary.get('make', '')) or 'Avigilon'}")
                st.write(f"Family: {_clean(camera_summary.get('family', ''))}")
                st.write(f"Model: {_clean(camera_summary.get('model_number', ''))}")
                st.write(f"Description: {_clean(camera_summary.get('description', ''))}")
            with info_col_2:
                st.markdown("##### Installation Context")
                st.write(f"Scenario: {_clean(camera_summary.get('scenario', ''))}")
                st.write(f"Environment: {_clean(camera_summary.get('environment', ''))}")
                st.write(f"Base Mount: {_clean(camera_summary.get('base_mount', ''))}")
                st.write(f"Camera Qty: {int(st.session_state.get('cib_quantity', 1) or 1)}")
            st.markdown("<div style='height:0.35rem'></div>", unsafe_allow_html=True)

        bom_df = result.get("bom_df", pd.DataFrame())
        if isinstance(bom_df, pd.DataFrame) and not bom_df.empty:
            display_df = bom_df.copy()
            if st.session_state.get("cib_required_only", False):
                display_df = display_df[display_df["Required/Optional"].eq("Required")].reset_index(drop=True)

            st.caption("Primary output")
            st.markdown("##### Final Bill Of Materials")
            st.dataframe(
                display_df,
                hide_index=True,
                use_container_width=True,
                column_config={"Required Qty": st.column_config.NumberColumn("Required Qty", step=1, format="%d")},
            )
            st.markdown("<div style='height:0.35rem'></div>", unsafe_allow_html=True)
            required_df = result.get("required_df", pd.DataFrame())
            optional_df = result.get("optional_df", pd.DataFrame())
            details_col, exports_col = st.columns([0.68, 0.32], gap="large")
            with details_col:
                if isinstance(required_df, pd.DataFrame) and not required_df.empty:
                    st.markdown("##### Required Parts")
                    st.dataframe(required_df, hide_index=True, use_container_width=True)
                if isinstance(optional_df, pd.DataFrame) and not optional_df.empty:
                    st.markdown("##### Optional Parts")
                    st.dataframe(optional_df, hide_index=True, use_container_width=True)

            export_text = _format_export_text(camera_summary, bom_df, result.get("notes", []))
            with exports_col:
                st.caption("Export")
                _render_copy_button(export_text, "cib")
                st.download_button(
                    "Download BOM CSV",
                    data=bom_df.to_csv(index=False).encode("utf-8"),
                    file_name=f"camera_installation_bom_{_clean(camera_summary.get('model_number', 'package'))}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
                st.download_button(
                    "Download Notes TXT",
                    data=export_text.encode("utf-8"),
                    file_name=f"camera_installation_bom_{_clean(camera_summary.get('model_number', 'package'))}.txt",
                    mime="text/plain",
                    use_container_width=True,
                )

        notes = result.get("notes", []) or []
        warnings = result.get("warnings", []) or []
        if notes:
            st.markdown("##### Notes / Limitations")
            for note in notes:
                st.write(f"- {note}")
        if warnings:
            st.markdown("##### Warnings")
            for warning in warnings:
                st.warning(warning)

        if result_context:
            st.caption(f"Workbook source: {_clean(result_context.get('workbook_name', ''))} ({_clean(result_context.get('workbook_hash', ''))})")

        if st.session_state.get("cib_debug_mode", False):
            debug_df = result.get("debug_df", pd.DataFrame())
            with st.expander("Debug / Workbook Match Log", expanded=True):
                if isinstance(debug_df, pd.DataFrame) and not debug_df.empty:
                    st.dataframe(debug_df, hide_index=True, use_container_width=True)
                else:
                    st.info("No debug match rows were recorded for this result.")
    st.markdown("</div>", unsafe_allow_html=True)
