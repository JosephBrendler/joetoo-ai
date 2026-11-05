from pathlib import Path
p=Path('tests/test_step1_5a_plan.py');s=p.read_text().replace('''        shutil.copyfile(ROOT / 'libexec/joetoo-kwin-plan-functions',
''','''        shutil.copyfile(ROOT / 'libexec/joetoo-kwin-exposure.py', self.folder / 'libexec/joetoo-kwin-exposure.py')
        shutil.copyfile(ROOT / 'libexec/joetoo-kwin-plan-functions',
''',1).replace("['1|konsole|direct'], ['1|konsole|direct||'],", "['1|konsole|direct'], ['1|konsole|direct||invalid'],")
s=s.replace("'config=/etc/joetoo-kwin/joetoo-kwin.conf', f'config=\"{self.config}\"'", "'/etc/joetoo-kwin/joetoo-kwin.conf', str(self.config)")
p.write_text(s)
p=Path('tests/test_step1_5c_launch.py');s=p.read_text().replace("'placement_transaction': {'state': 'IDLE'}})", "'placement_transaction': {'state': 'IDLE'}, 'initial_layout_protocol': 1, 'initial_layout_active': False})",1)
s=s.replace('''    *.Status) printf '%s\\\\n' "${PLACEMENT_STATE:-OK}" ;;''','''    *.Status) printf '%s\\\\n' "${PLACEMENT_STATE:-OK}" ;;
    *.SubmitInitialLayout) printf 'initial-layout-id\\\\n' ;;
    *.InitialLayoutStatus) printf '{"state":"SUCCEEDED","stacking":"verified","focus":"verified"}\\\\n' ;;''')
p.write_text(s)
