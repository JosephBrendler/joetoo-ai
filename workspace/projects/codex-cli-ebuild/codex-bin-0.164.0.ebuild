# Copyright 2026 Joseph Brendler
# SPDX-License-Identifier: GPL-2.0-or-later

EAPI=8

DESCRIPTION="OpenAI Codex command-line coding agent (upstream prebuilt binary)"
HOMEPAGE="https://github.com/openai/codex https://developers.openai.com/codex"

# Candidate: verify that BOTH release asset paths and the LICENSE URL resolve.
# Keep the download filenames distinct across architectures.
SRC_URI="
    amd64? ( https://github.com/openai/codex/releases/download/rust-v${PV}/codex-x86_64-unknown-linux-musl.tar.gz -> ${P}-amd64.tar.gz )
    arm64? ( https://github.com/openai/codex/releases/download/rust-v${PV}/codex-aarch64-unknown-linux-musl.tar.gz -> ${P}-arm64.tar.gz )
    https://raw.githubusercontent.com/openai/codex/rust-v${PV}/LICENSE -> ${P}.LICENSE
"

S="${WORKDIR}"
LICENSE="Apache-2.0"
SLOT="0"
# Intentional: do not claim tested stable or testing keywords before verification.
KEYWORDS=""
IUSE=""
RESTRICT="test strip"

# The shipped executable is statically linked for musl, but requires a
# supported Linux kernel and may use additional runtime sandbox helpers.
# Do not promise that Codex's sandbox works on every hardened configuration.

src_unpack() {
    local archive
    case ${ARCH} in
        amd64) archive=${P}-amd64.tar.gz ;;
        arm64) archive=${P}-arm64.tar.gz ;;
        *) die "Unsupported architecture: ${ARCH}" ;;
    esac
    unpack "${archive}"
    cp "${DISTDIR}/${P}.LICENSE" "${WORKDIR}/LICENSE" || die
}

src_install() {
    local binary
    case ${ARCH} in
        amd64) binary=codex-x86_64-unknown-linux-musl ;;
        arm64) binary=codex-aarch64-unknown-linux-musl ;;
        *) die "Unsupported architecture: ${ARCH}" ;;
    esac
    [[ -f ${binary} ]] || die "Missing expected binary: ${binary}"
    newbin "${binary}" codex
    dodoc LICENSE
}

pkg_postinst() {
    elog "Run 'codex --version' to verify the installed CLI."
    elog "Use 'codex' to sign in with ChatGPT, or configure API authentication."
    elog "Start within an explicitly authorized joetoo-ai workspace."
    elog "Review sandbox and approval settings before permitting command execution."
    elog "Do not grant this agent access to joetoo or joetoo-upstream."
}
