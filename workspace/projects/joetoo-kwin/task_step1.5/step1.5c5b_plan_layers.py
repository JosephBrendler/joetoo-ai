from pathlib import Path
p=Path('libexec/joetoo-kwin-plan-functions');s=p.read_text().replace('    desktop_limit=20','    desktop_limit=20\n    dt_win_limit=4\n    min_window_exposure_px=32',1)
s=s.replace('''    local _vp_desktop _vp_program _vp_mode _vp_target''','''    local _vp_desktop _vp_program _vp_mode _vp_target _vp_layer _vp_explicit _vp_total''',1)
s=s.replace('''    declare -gA terminal_counts=() terminal_slots=() next_slot=()''','''    declare -ga planned_explicit=() desktop_groups=()
    declare -gA implicit_counts=() total_counts=() terminal_counts=() terminal_slots=() next_slot=()''',1)
s=s.replace('''    _vp_declaration=$(declare -p desktop_session_list''','''    if [[ ! $dt_win_limit =~ ^[1-9][0-9]{0,2}$ || ! $min_window_exposure_px =~ ^[1-9][0-9]{0,4}$ ]] ||
        (( dt_win_limit > 256 || min_window_exposure_px > 32768 )); then
        plan_error 'invalid dt_win_limit (1..256) or min_window_exposure_px (1..32768)'; return 2
    fi
    _vp_declaration=$(declare -p desktop_session_list''',1)
s=s.replace('''if (( ${#_vp_delimiters} != 3 ))''','''if (( ${#_vp_delimiters} != 3 && ${#_vp_delimiters} != 4 ))''',1).replace("expected four single-line pipe-delimited fields", "expected four or five single-line pipe-delimited fields",1)
s=s.replace('''read -r _vp_desktop _vp_program _vp_mode _vp_target <<<''','''read -r _vp_desktop _vp_program _vp_mode _vp_target _vp_layer <<<''',1)
a=s.index('''        if [[ $_vp_program == konsole ]]; then''');b=s.index('''        planned_desktop+=''');s=s[:a]+'''        # A blank fifth field is an implicit panel, as in the approved example.
        _vp_explicit=0
        if [[ -n $_vp_layer ]]; then _vp_explicit=1; else _vp_layer=panel; fi
        case $_vp_layer in panel|under|over) ;; *) plan_error 'invalid layer'; return 2 ;; esac
        [[ -v total_counts[$_vp_desktop] ]] || desktop_groups+=("$_vp_desktop")
        total_counts[$_vp_desktop]=$(( ${total_counts[$_vp_desktop]:-0} + 1 ))
        implicit_counts[$_vp_desktop]=$(( ${implicit_counts[$_vp_desktop]:-0} + 1 - _vp_explicit ))
        if [[ $_vp_layer == panel ]]; then
            terminal_counts[$_vp_desktop]=$(( ${terminal_counts[$_vp_desktop]:-0} + 1 ))
        fi
        planned_layer+=("$_vp_layer"); planned_explicit+=("$_vp_explicit")
''' +s[b:]
s=s.replace('''    done
    return 0
}

# Shared terminal policy''','''    done
    for _vp_desktop in "${desktop_groups[@]}"; do
        _vp_total=${total_counts[$_vp_desktop]}
        if (( ${implicit_counts[$_vp_desktop]} > dt_win_limit )); then
            plan_error "desktop [$_vp_desktop] implicit entries exceed dt_win_limit"; return 2
        fi
        if (( _vp_total > dt_win_limit )); then
            j_msg "-${warn}" -p "Desktop [$_vp_desktop]: explicit layers exceed ordinary layout budget [$_vp_total/$dt_win_limit]"
        fi
        if (( ${terminal_counts[$_vp_desktop]:-0} > 4 )); then
            plan_error "desktop [$_vp_desktop] has more than four panel windows; allocator limit"; return 2
        fi
    done
    return 0
}

# Shared terminal policy''',1)
s=s.replace('''    local _cp_i _cp_desktop _cp_slot _cp_terminal_slot''','''    local _cp_i _cp_desktop _cp_slot _cp_terminal_slot _cp_key _cp_offset _cp_warning _cp_dir
    local -A _cp_cascade=()''',1)
s=s.replace('''        if [[ ${planned_program[$_cp_i]} == konsole ]]; then''','''        if [[ ${planned_layer[$_cp_i]} == panel ]]; then''',1).replace('''            planned_layer+=(terminal)
''','',1).replace('''            planned_layer+=(underlay-proposed)''','''            _cp_key=$_cp_desktop:${planned_layer[$_cp_i]}
            _cp_offset=$(( ${_cp_cascade[$_cp_key]:-0} * min_window_exposure_px ))
            _cp_cascade[$_cp_key]=$(( ${_cp_cascade[$_cp_key]:-0} + 1 ))
            geometry_x=$(( geometry_x + _cp_offset )); geometry_y=$(( geometry_y + _cp_offset ))
            (( geometry_x + geometry_width <= screen_width )) || geometry_x=$(( screen_width - geometry_width ))
            (( geometry_y + geometry_height <= screen_height )) || geometry_y=$(( screen_height - geometry_height ))''',1)
needle='''    done
    return 0
}

print_plan()''';s=s.replace(needle,'''    done
    _cp_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P) || return 1
    _cp_warning=$(
        for ((_cp_i=0; _cp_i<${#planned_desktop[@]}; _cp_i++)); do
            printf '%s %s %s %s %s %s %s\\n' "${planned_desktop[$_cp_i]}" "${planned_layer[$_cp_i]}" "${planned_slot[$_cp_i]}" \\
                "${planned_x[$_cp_i]}" "${planned_y[$_cp_i]}" "${planned_width[$_cp_i]}" "${planned_height[$_cp_i]}"
        done | python3 "$_cp_dir/joetoo-kwin-exposure.py" "$min_window_exposure_px"
    ) || return 1
    while IFS= read -r _cp_warning; do
        [[ -z $_cp_warning ]] || j_msg "-${warn}" -p "$_cp_warning (frame prediction; compositor/decorations may differ)"
    done <<< "$_cp_warning"
    return 0
}

print_plan()''',1)
p.write_text(s)
