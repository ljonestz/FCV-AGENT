"""Unit tests for Zone 2 compact label logic."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def build_s1_label(is_impl, doc_parts):
    """Mirrors the compact label logic to be added to app.py."""
    primary_names = [dp['name'] for dp in doc_parts if dp['label'] == 'PROJECT DOCUMENT']
    package_names = [dp['name'] for dp in doc_parts if dp['label'] == 'PACKAGE INSTRUMENT']
    context_names = [dp['name'] for dp in doc_parts if dp['label'] == 'CONTEXT DOCUMENT']
    base = "[Stage 1 — implementation documents and FCV context analysed]" if is_impl \
           else "[Stage 1 — project documents and FCV context analysed]"
    parts = [f"Primary: {primary_names[0]}" if primary_names else ""]
    if package_names:
        parts.append(f"Package: {', '.join(package_names)}")
    if context_names:
        parts.append(f"Country context: {', '.join(context_names)}")
    suffix = ". ".join(p for p in parts if p)
    return f"{base} {suffix}".strip() if suffix else base

def test_label_with_all_zones():
    doc_parts = [
        {'label': 'PROJECT DOCUMENT', 'name': 'PAD.pdf'},
        {'label': 'PACKAGE INSTRUMENT', 'name': 'ESCP.pdf'},
        {'label': 'PACKAGE INSTRUMENT', 'name': 'SORT.pdf'},
        {'label': 'CONTEXT DOCUMENT', 'name': 'RRA.pdf'},
    ]
    label = build_s1_label(False, doc_parts)
    assert 'PAD.pdf' in label
    assert 'ESCP.pdf' in label
    assert 'SORT.pdf' in label
    assert 'RRA.pdf' in label

def test_label_primary_only():
    doc_parts = [{'label': 'PROJECT DOCUMENT', 'name': 'PID.pdf'}]
    label = build_s1_label(False, doc_parts)
    assert 'PID.pdf' in label
    assert 'Package:' not in label
    assert 'Country context:' not in label

def test_label_no_package():
    doc_parts = [
        {'label': 'PROJECT DOCUMENT', 'name': 'PAD.pdf'},
        {'label': 'CONTEXT DOCUMENT', 'name': 'CPF.pdf'},
    ]
    label = build_s1_label(False, doc_parts)
    assert 'Package:' not in label
    assert 'CPF.pdf' in label
