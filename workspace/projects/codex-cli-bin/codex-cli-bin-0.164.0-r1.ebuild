# Copyright 2026 Joseph Brendler
# Distributed under the terms of the GNU General Public License v2

EAPI=8

DESCRIPTION="OpenAI Codex command-line coding agent (upstream prebuilt binaries)"
HOMEPAGE="https://github.com/openai/codex https://developers.openai.com/codex"

SRC_URI="
	amd64? ( https://github.com/openai/codex/releases/download/rust-v${PV}/codex-package-x86_64-unknown-linux-musl.tar.gz
		 -> ${P}-amd64-package.tar.gz )
	arm64? ( https://github.com/openai/codex/releases/download/rust-v${PV}/codex-package-aarch64-unknown-linux-musl.tar.gz
		 -> ${P}-arm64-package.tar.gz )
	https://raw.githubusercontent.com/openai/codex/rust-v${PV}/LICENSE -> ${P}.LICENSE
	https://raw.githubusercontent.com/openai/codex/rust-v${PV}/NOTICE -> ${P}.NOTICE
	https://raw.githubusercontent.com/openai/codex/rust-v${PV}/codex-rs/vendor/bubblewrap/COPYING \
		 -> ${P}.bubblewrap-COPYING
"

S="${WORKDIR}"
# known license terms; bundled dependency notice inventory remains incomplete
LICENSE="Apache-2.0 BSD MIT LGPL-2+"
SLOT="0"

# Note: add testing keywords after native Gentoo validation
KEYWORDS=""
#IUSE=""   # pkgcheck scan dislikes empty globals

# Note: modifying bwrap can break Codex's embedded digest check
RESTRICT="strip test"

# upstream arm64 rg is GNU-linked even in the musl-named package
RDEPEND="
	arm64? (
		>=sys-libs/glibc-2.18
		sys-devel/gcc
	)
"

QA_PREBUILT="
	usr/libexec/codex/bin/codex
	usr/libexec/codex/bin/codex-code-mode-host
	usr/libexec/codex/codex-resources/bwrap
	usr/libexec/codex/codex-path/rg
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
	# preserve relative paths used by upstream's install-context discovery
	# retain every resource required for daemon package preparation
	# only voice is excluded; see DAEMON-FIX.md
	exeinto /usr/libexec/codex/bin
	doexe bin/codex bin/codex-code-mode-host
	exeinto /usr/libexec/codex/codex-path
	doexe codex-path/rg
	exeinto /usr/libexec/codex/codex-resources
	doexe codex-resources/bwrap
	insinto /usr/libexec/codex
	doins codex-package.json
	dosym ../libexec/codex/bin/codex /usr/bin/codex

	newdoc "${DISTDIR}/${P}.LICENSE" LICENSE
	newdoc "${DISTDIR}/${P}.NOTICE" NOTICE
	dodoc "${FILESDIR}/Ratatui-MIT" \
		"${FILESDIR}/libcap-2.75-LICENSE" \
		"${FILESDIR}/libcap-2.75-COPYRIGHTS" \
		"${FILESDIR}/ripgrep-15.2.0-COPYING" \
		"${FILESDIR}/ripgrep-15.2.0-LICENSE-MIT" \
		"${FILESDIR}/ripgrep-15.2.0-UNLICENSE"
	newdoc "${DISTDIR}/${P}.bubblewrap-COPYING" bubblewrap-COPYING
}

pkg_postinst() {
	elog "Run 'codex --version' to verify the installed CLI."
	elog "Use 'codex' to sign in with ChatGPT, or configure API authentication."
	elog "This ebuild does not install upstream's optional voice runtime."
	elog "Review sandbox and approval settings before permitting command execution."
	elog "Sandbox operation depends on kernel and host security policy."
}
