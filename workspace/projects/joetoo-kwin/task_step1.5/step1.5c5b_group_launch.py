from pathlib import Path
p=Path('joetoo-kwin');s=p.read_text().replace('''    config=/etc/joetoo-kwin/joetoo-kwin.conf''','''    config=""''',1)
idx=s.index('\napply_cli_verbosity()');s=s[:idx]+'''
select_config() {
    [[ ! $CONFIG_SELECTED ]] || return 0
    local _sc_home=${XDG_CONFIG_HOME:-$HOME/.config} _sc_user _sc_system=/etc/joetoo-kwin/joetoo-kwin.conf
    [[ $_sc_home == /* ]] || _sc_home=$HOME/.config
    _sc_user=$_sc_home/joetoo-kwin/joetoo-kwin.conf
    if [[ -e $_sc_user || -L $_sc_user ]]; then config=$_sc_user
    elif [[ -e $_sc_system || -L $_sc_system ]]; then config=$_sc_system
    else
        j_msg "-${err}" -p "No configuration: create [$_sc_user] or select -f CONFIG; system fallback [$_sc_system] absent"
        return 2
    fi
}
''' +s[idx:];s=s.replace('''    plan_defaults
    if [[ ! -f $config''','''    plan_defaults
    select_config || return $?
    if [[ ! -f $config''',1)
s=s.replace('''        [[ -f $config && -r $config ]]''','''        select_config || return $?
        [[ -f $config && -r $config ]]''',1)
s=s.replace('''    varlist+=" terminal_width_percent''','''    varlist+=" dt_win_limit min_window_exposure_px"
    varlist+=" terminal_width_percent''',1)
s=s.replace('CONFIG defaults to /etc/joetoo-kwin/joetoo-kwin.conf;', 'CONFIG: XDG user configuration, then /etc/joetoo-kwin/joetoo-kwin.conf;')
p.write_text(s)
p=Path('libexec/joetoo-kwin-launch-functions');s=p.read_text().replace('''    _lp_managed=$(qdbus6''','''    jq -e '.initial_layout_protocol == 1 and .initial_layout_active == false' <<< "$_lp_status" >/dev/null || {
        plan_error 'compatible initial-layout resident/broker required, or initial layout Busy'; return 1; }
    _lp_managed=$(qdbus6''',1)
# Rechecks must skip groups already initialized, regardless of original indices.
s=s.replace('''    for ((_lp_i=${1:-0};''','''    for ((_lp_i=0;''',1).replace('''        _lp_conflicts=$(jq''','''        [[ ! ${launch_finished[${planned_desktop[$_lp_i]}]:-} ]] || continue
        _lp_conflicts=$(jq''',1)
s=s.replace('''    local _op_dir _op_i _op_failed=0 _op_rc _op_state _op_status''','''    local _op_dir _op_i _op_failed=0 _op_rc _op_state _op_status _op_group _op_payload _op_layout _op_try
    local -A launch_finished=()
    local -a _op_entries=()''',1)
s=s.replace('''    for ((_op_i=0; _op_i<${#planned_desktop[@]}; _op_i++)); do
        # Recheck''','''    for _op_group in "${desktop_groups[@]}"; do
      _op_entries=()
      for ((_op_i=0; _op_i<${#planned_desktop[@]}; _op_i++)); do
        [[ ${planned_desktop[$_op_i]} == "$_op_group" ]] || continue
        # Recheck''',1)
# prior individual entries need skip conflict but futureentries recheck; associate finished item index separate.
s=s.replace('''    local -A launch_finished=()''','''    local -A launch_finished=() launch_done_entry=()''',1)
s=s.replace('''        [[ ! ${launch_finished[${planned_desktop[$_lp_i]}]:-} ]] || continue''','''        [[ ! ${launch_finished[${planned_desktop[$_lp_i]}]:-} && ! ${launch_done_entry[$_lp_i]:-} ]] || continue''',1)
needle='''        case $_op_status in OK*|ERROR*) ;; *) j_msg "-${err}" -p 'Unresolved placement; stopping incomplete layout'; return 1 ;; esac
    done'''
s=s.replace(needle,'''        case $_op_status in OK*|ERROR*) ;; *) j_msg "-${err}" -p 'Unresolved placement; stopping incomplete layout'; return 1 ;; esac
        launch_done_entry[$_op_i]=1
        if (( _op_rc == 0 )); then
            _op_entries+=("$(jq -cn --arg id "$launch_registration_id" --arg layer "${planned_layer[$_op_i]}" \\
                '{registration_request_id:$id,layer:$layer}')")
        fi
      done
      if (( ${#_op_entries[@]} > 0 )); then
        _op_payload=$(printf '%s\\n' "${_op_entries[@]}" | jq -sc '{entries:.}') || return 1
        _op_layout=$(qdbus6 "$bus" "$path" "$iface.SubmitInitialLayout" "$_op_payload") || return 1
        qdbus6 org.kde.kglobalaccel /component/kwin org.kde.kglobalaccel.Component.invokeShortcut joetoo_bridge_initial_layout >/dev/null || return 1
        _op_state=""
        j_msg "-${notice}" -p "Initializing desktop [$_op_group] stack/focus; geometry remains separately verified"
        for ((_op_try=0; _op_try<100; _op_try++)); do
            _op_state=$(qdbus6 "$bus" "$path" "$iface.InitialLayoutStatus" "$_op_layout") || return 1
            _op_status=$(jq -er '.state' <<< "$_op_state") || return 1
            case $_op_status in SUCCEEDED|FAILED) break ;; PENDING|RUNNING) sleep .1 ;; *) return 1 ;; esac
        done
        j_msg "-${info}" -m "Initial layout: $_op_state"
        if [[ $_op_status != SUCCEEDED ]]; then
            j_msg "-${err}" -p "Initial stack/focus incomplete: $_op_state"
            [[ $_op_status == FAILED ]] || return 1
            _op_failed=$((_op_failed + 1))
        fi
      fi
      launch_finished[$_op_group]=1
    done''',1)
# Final summary should not subtract initialization failures from successful window count.
s=s.replace('''_op_failed=0 _op_rc''','''_op_failed=0 _op_initial_failed=0 _op_rc''',1).replace('''_op_failed=$((_op_failed + 1))
        fi
      fi''','''_op_initial_failed=$((_op_initial_failed + 1))
        fi
      fi''',1).replace('''if (( _op_failed == 0 )); then report_action''','''if (( _op_failed == 0 && _op_initial_failed == 0 )); then report_action''',1)
p.write_text(s)
