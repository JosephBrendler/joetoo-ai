#====[ joetoo Pseudo-boolean Framework ]=========================================

# Native shells have no boolean data types. This framework establishes a global
# convention for tracking truth values across variables using string characteristics.
# It begins with these assignments, made global for any script sourcing script_header_joetoo -
TRUE=0    # Evaluates to LOGICALLY TRUE inside [ and [[
FALSE=""  # Evaluates to LOGICALLY FALSE inside [ and [[
#
#----[ Usage, Idioms, and Architectural Principles ]-----------------------------
# Assignment:  VAR=$TRUE or VAR=$FALSE
# convention: all-capital variable names make pseudo-boolean variables conspicuous
# Rule 1: Always assign VAR=$TRUE or VAR=$FALSE (never any other value)
# Rule 2: Always use [...], [[...]], or case ... to evaluate pseudo-boolean variables
# Rule 3: Do not use if "$VAR"; instead use if [ "$VAR" ]
# Example truth tests:
#    [ "$VAR" ] && echo "true" || else echo
#
#    if [ "$VAR" ]; then echo "true"; else echo "false"; fi
#
#    case "$VAR" in "$TRUE") ... ;; "$FALSE") ... ;;  esac
#
# Note: $VAR will evaluate as expected in all of the examples above,
#    even if not quoted, as explained below.  However, linting tools like
#    shellcheck will complain about that (so quote them as shown above)
#
#----[ How it works ]------------------------------------------------------------
# 1. '[' and '[[' are COMMANDS designed to evaluate data values
#
#    The POSIX 1-argument rule for [ "$VAR" ] is:
#        return success if VAR is non-zero length (like $TRUE with TRUE=0)
#        return failure if VAR is zero length (like $FALSE with FALSE='')
#
#    In shells like Bash, [[ "$VAR" ]] semantically evaluates everything inside [[ ]]
#        returns are the same as for [ ], though the process differs
#
#    Thus, [ and [[ consume strings, perform a structural test, and then emit an
#        integer exit status code
#
# 2. 'if' is a CONTROL STRUCTURE that executes commands, reads exit codes, and
#        branches program flow. It does not evaluate the truth of a data value.
#        It evaluates the success or failure of an active execution process ($?).
#        As such, if [ $VAR ]; ... will always behave as expected,
#        but if $VAR; ... will not work (not what if is designed for)
#
# 3. Unlike if, a case statement does not run any processes to determine control flow.
#        Instead, it takes a raw string, performs literal string matching (using
#        shell globbing rules), and branches immediately to the first matching pattern.
#        As such, case "$VAR" in "$TRUE") ... ;; "$FALSE") ... ;;  esac will always
#        behave as expected.
#
#----[ Truth Testing Mechanics ]------------------------------------------------
# - [ $TRUE ]     -> [ 1-arg rule ] checks string-length of "0" (>0) -> True (0).
# - [ $FALSE ]    -> Unquoted, it vanishes to 0 args -> POSIX default -> False (1).
# - [ "$FALSE" ]  -> Quoted, [ 1-arg rule ] checks length of "" (==0) -> False (1).
# - [[ $TRUE ]]   -> Keyword preserves "0" internally -> Non-empty -> True (0).
# - [[ $FALSE ]]  -> Keyword preserves "" internally  -> Empty     -> False (1).
#
# Negation (!) behaves reliably across both implementation profiles:
# - [ ! $FALSE ]   -> Collapses to [ ! ] (1-arg string literal check) -> True (0).
# - [ ! "$FALSE" ] -> Utilizes 2-arg negation logic -> ! (False)      -> True (0).
# - [[ ! $FALSE ]] -> Keyword treats ! as a logical operator over ""  -> True (0).
#
#----[ Why the "Pseudo" in Pseudo-boolean ]--------------------------------------
# Pseudo-boolean variables fill a coding style gap that shell scripting otherwise
# does not accommodate.  They can be used with && or || operators to function just
# like actual boolean data types, but under the hood, they are still strings like
# all shell variables.
#
# In contrast, the bitwise operators available in shells do treat the actual bits
# in the bytes that are the content of shell variables as actual binary numbers.
# Thus operations like $var=$(( rc | 1 << n )) assign the 1/0 value of bit n of $rc
# to $var, making var mathematically binary (or actual boolean), though again under
# the hood, it is still a string consisting of at least one byte (0b000000 or 0b000001)
#
# However, shells area actually LESS well suited to use of this sor of binary/boolean
# variable to represent and test truth because it would require mathematical
# comparison like (( var > 0 )) or [ "$var" -eq 1 ]. I.e. it would still require
# brackets, it cannot be tested directly by if ... then, and it is a more complex
# and less readable way to express a truth test.
#
# Summary:
# Pseudo-boolean variables, actual binary/boolean variables, and command exit
# status values are all different things, in a separation of concerns and purposes.
#----[ Separation of Concerns: Framework vs. Bitwise vs. Exit Status ]---------
#
# +----------------+-------------------+--------------------+------------------+
# | Construct Type | Data Format       | Primary Evaluator  | Native Use Case  |
# +----------------+-------------------+--------------------+------------------+
# | Pseudo-Boolean | String ("0" / "") | [ ], [[ ]], case   | App state / flag |
# +----------------+-------------------+--------------------+------------------+
# | Bitwise/Binary | Integer (1 / 0)   | (( )) / $(( ))     | Bitmasks / math  |
# +----------------+-------------------+--------------------+------------------+
# | Exec Exit Code | Byte (0 to 255)   | if structure ($?)  | Process tracking |
# +----------------+-------------------+--------------------+------------------+
#
# CAUTION: Be careful to maintain this separation of concerns and obey rules for
# each type. A mathematical 1 or an error code of 1 will evaluate as "True" if
# fed into a pseudo-boolean (string) test! (for the former, that may be what you
# want, but it is unlikely that is what you want for the latter.
#
# Note: the TrueFalse function below is available to "translate" types
# and the status_color can be used to enhance visualization
#
# useful idiom:
#    printf '%s\n' "VAR is: [$(status_color "$VAR")$(TrueFalse "$VAR")${Boff}]"
#
#==============================================================================
# *  Summary of T/F tests with TrueFalse() translation --
#    testing: [$TRUE] is True
#    testing: [$FALSE] is False
#    testing: [y] is True
#    testing: [Y] is True
#    testing: [n] is False
#    testing: [N] is False
#    testing: [t] is True
#    testing: [T] is True
#    testing: [f] is False
#    testing: [F] is False
#    testing: [up] is True
#    testing: [down] is False
#    testing: [0] is True
#    testing: [1] is unset
#    testing: [z] is unset
#    testing: [''] is False
# run demonstrate_header -2 to see this (colorized) in your terminal

