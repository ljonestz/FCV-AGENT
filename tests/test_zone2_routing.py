"""Unit tests for Zone 2 document routing logic."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def route_docs(documents):
    """Mirrors the routing logic in app.py Stage 1 block."""
    project_docs = [d for d in documents if d.get('docRole') == 'primary'
                    or (not d.get('docRole') and not d.get('isContext'))]
    package_docs  = [d for d in documents if d.get('docRole') == 'package']
    context_docs  = [d for d in documents if d.get('docRole') == 'context'
                     or (not d.get('docRole') and d.get('isContext'))]
    return project_docs, package_docs, context_docs


def test_route_by_docRole():
    docs = [
        {'name': 'PAD.pdf',  'docRole': 'primary',  'isContext': False},
        {'name': 'ESCP.pdf', 'docRole': 'package',  'isContext': True},
        {'name': 'RRA.pdf',  'docRole': 'context',  'isContext': True},
    ]
    proj, pkg, ctx = route_docs(docs)
    assert [d['name'] for d in proj] == ['PAD.pdf']
    assert [d['name'] for d in pkg]  == ['ESCP.pdf']
    assert [d['name'] for d in ctx]  == ['RRA.pdf']


def test_backward_compat_no_docRole():
    docs = [
        {'name': 'PAD.pdf',  'isContext': False},
        {'name': 'RRA.pdf',  'isContext': True},
    ]
    proj, pkg, ctx = route_docs(docs)
    assert [d['name'] for d in proj] == ['PAD.pdf']
    assert pkg == []
    assert [d['name'] for d in ctx]  == ['RRA.pdf']


def test_package_docs_excluded_from_context():
    docs = [
        {'name': 'ESCP.pdf', 'docRole': 'package', 'isContext': True},
        {'name': 'RRA.pdf',  'docRole': 'context',  'isContext': True},
    ]
    proj, pkg, ctx = route_docs(docs)
    assert 'ESCP.pdf' not in [d['name'] for d in ctx]
    assert 'ESCP.pdf' in     [d['name'] for d in pkg]
