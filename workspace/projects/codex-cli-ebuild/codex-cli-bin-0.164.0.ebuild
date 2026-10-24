# Copyright 2026 Joseph Brendler
# SPDX-License-Identifier: GPL-2.0-or-later

EAPI=8

DESCRIPTION="OpenAI Codex command-line coding agent (upstream prebuilt binaries)"
HOMEPAGE="https://github.com/openai/codex https://developers.openai.com/codex"

SRC_URI="
	amd64? ( https://github.com/openai/codex/releases/download/rust-v${PV}/codex-package-x86_64-unknown-linux-musl.tar.gz -> ${P}-amd64-package.tar.gz )
	arm64? ( https://github.com/openai/codex/releases/download/rust-v${PV}/codex-package-aarch64-unknown-linux-musl.tar.gz -> ${P}-arm64-package.tar.gz )
	https://raw.githubusercontent.com/openai/codex/rust-v${PV}/LICENSE -> ${P}.LICENSE
	https://raw.githubusercontent.com/openai/codex/rust-v${PV}/NOTICE -> ${P}.NOTICE
	https://raw.githubusercontent.com/openai/codex/rust-v${PV}/codex-rs/vendor/bubblewrap/COPYING -> ${P}.bubblewrap-COPYING
"

S="${WORKDIR}"
# Known license terms; bundled dependency notice inventory remains incomplete.
LICENSE="Apache-2.0 BSD MIT LGPL-2+"
SLOT="0"
# Candidate only: add testing keywords after native Gentoo validation.
KEYWORDS=""
IUSE=""
# In particular, modifying bwrap can break Codex's embedded digest check.
RESTRICT="strip test"

RDEPEND="sys-apps/ripgrep"

QA_PREBUILT="
	usr/libexec/codex/bin/codex
	usr/libexec/codex/bin/codex-code-mode-host
	usr/libexec/codex/codex-resources/bwrap
"

src_unpack() {
	local archive
	case ${ARCH} in
		amd64) archive=${P}-amd64-package.tar.gz ;;
		arm64) archive=${P}-arm64-package.tar.gz ;;
		*) die "Unsupported architecture: ${ARCH}" ;;
	esac
	unpack "${archive}"
}

src_configure() { :; }
src_compile() { :; }

src_install() {
	# Preserve relative paths used by upstream's install-context discovery.
	# Install only the CLI, code-mode host and matching sandbox helper.
	# Voice and bundled ripgrep are deliberately excluded; see README.md.
	exeinto /usr/libexec/codex/bin
	doexe bin/codex bin/codex-code-mode-host
	exeinto /usr/libexec/codex/codex-resources
	doexe codex-resources/bwrap
	insinto /usr/libexec/codex
	doins codex-package.json
	dosym ../libexec/codex/bin/codex /usr/bin/codex

	newdoc "${DISTDIR}/${P}.LICENSE" LICENSE
	newdoc "${DISTDIR}/${P}.NOTICE" NOTICE
	dodoc "${FILESDIR}/Ratatui-MIT" \
		"${FILESDIR}/libcap-2.75-LICENSE" \
		"${FILESDIR}/libcap-2.75-COPYRIGHTS"
	newdoc "${DISTDIR}/${P}.bubblewrap-COPYING" bubblewrap-COPYING
}

pkg_postinst() {
	elog "Run 'codex --version' to verify the installed CLI."
	elog "Use 'codex' to sign in with ChatGPT, or configure API authentication."
	elog "This candidate does not install upstream's optional voice runtime."
	elog "Review sandbox and approval settings before permitting command execution."
	elog "Sandbox operation depends on kernel and host security policy."
}
