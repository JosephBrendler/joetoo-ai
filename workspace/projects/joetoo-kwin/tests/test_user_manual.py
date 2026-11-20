# Copyright 2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Check copyable syntax and complete reference coverage without executing effects."""
import ast
from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
MANUAL = ROOT / 'docs/joetoo-kwin_user_manual.md'


class UserManualTests(unittest.TestCase):
    def test_every_public_broker_method_has_exact_wire_signature(self):
        expected = {}
        tree = ast.parse((ROOT / 'libexec/joetoo-kwind').read_text())
        broker = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Broker')
        for fn in broker.body:
            if not isinstance(fn, ast.FunctionDef): continue
            for dec in fn.decorator_list:
                if isinstance(dec, ast.Call) and getattr(dec.func, 'attr', '') == 'method':
                    kw = {k.arg: ast.literal_eval(k.value) for k in dec.keywords}
                    expected[fn.name] = (kw['in_signature'] or '∅', kw['out_signature'] or '∅')
        table = MANUAL.read_text().split('### Complete exposed')[1].split('### Structured transaction')[0]
        rows = re.findall(r'^\| `([A-Za-z]+)` \| `([^`]+)` → `([^`]+)` \|', table, re.M)
        self.assertEqual(len(rows), len(expected))
        self.assertEqual({name: (ins, outs) for name, ins, outs in rows}, expected)
    def test_all_four_native_methods_match_cpp_declarations(self):
        source = (ROOT / 'native/managed-close/adapter.cpp').read_text()
        expected = {}
        for name, args in re.findall(r'Q_SCRIPTABLE QString (\w+)\(([^)]*)\)', source):
            expected[name] = ''.join('i' if arg.strip().startswith('int ') else 's' for arg in args.split(','))
        section = MANUAL.read_text().split('### Native service and owner diagnostics')[1].split('Safe owner/introspection diagnostics:')[0]
        rows = re.findall(r'^\| `(\w+)` \| `([^`]+)` → `s` \|', section, re.M)
        self.assertEqual(dict(rows), expected)
    def test_bash_examples_parse_only_and_end_with_copy_safety_comment(self):
        blocks = re.findall(r'```bash\n(.*?)```', MANUAL.read_text(), re.S)
        self.assertGreater(len(blocks), 5)
        for block in blocks:
            self.assertTrue(block.endswith('# End of commands\n\n'))
            run = subprocess.run(['bash', '-n'], input=block, text=True, capture_output=True)
            self.assertEqual(run.returncode, 0, run.stderr)
    def test_local_markdown_links_resolve_and_no_generated_pdf_html(self):
        for link in re.findall(r'\]\(([^)]+)\)', MANUAL.read_text()):
            self.assertTrue((MANUAL.parent / link.split('#')[0]).exists(), link)
        self.assertFalse(MANUAL.with_suffix('.pdf').exists())
        self.assertFalse(MANUAL.with_suffix('.html').exists())
    def test_cli_flags_and_safety_distinctions_are_documented(self):
        text = MANUAL.read_text()
        for flag in ('-c','-o','-L','-l','-d','-x','-S','-r','-m','-f','-v','-q','-h','-s','-i'):
            self.assertIn(flag, text)
        self.assertIn('separate `qdbus6` processes', text)
        self.assertIn('same original authenticated', text)
        self.assertIn('not ProcessFD-pinned', text)
        self.assertIn('not ProcessFD/UID/PID/start-time', text.replace('**', ''))


if __name__ == '__main__': unittest.main()
