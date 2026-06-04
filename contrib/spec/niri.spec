# Build a custom niri with GetCursorPos IPC command.
#
# COPR project settings:
#   - Enable "Internet access" (needed for smithay git dep and crates.io)
#   - Or use: `copr-cli edit-package-scm --name niri --webhook-rebuild on caoturkey/niri`
#
# Source: GitHub commit archive (self-contained, no vendored deps needed)

%global srcver 26.4.0
%global commit 56a5b700077de9924d61a99bffca36d83d98b417
%global shortcommit %(c=%{commit}; echo ${c:0:8})

# Keep debuginfo in binary for panic backtraces.
%global debug_package %{nil}
%global __strip /bin/true
%global rustflags_debuginfo 2

Name:           niri
Version:        %{srcver}
Release:        1.dev%{shortcommit}%{?dist}
Summary:        Scrollable-tiling Wayland compositor (custom: GetCursorPos IPC)

# https://github.com/TurkeyC/niri
URL:            https://github.com/TurkeyC/niri

# Source tarball generated from the dev branch commit.
Source0:        https://github.com/TurkeyC/niri/archive/%{commit}/niri-%{commit}.tar.gz

License:        GPL-3.0-or-later

# ── Build dependencies ──────────────────────────────────────────────
BuildRequires:  cargo-rpm-macros >= 25
BuildRequires:  pkgconfig(udev)
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(xkbcommon)
BuildRequires:  wayland-devel
BuildRequires:  pkgconfig(libinput)
BuildRequires:  pkgconfig(dbus-1)
BuildRequires:  pkgconfig(systemd)
BuildRequires:  pkgconfig(libseat)
BuildRequires:  pkgconfig(libdisplay-info)
BuildRequires:  pipewire-devel
BuildRequires:  pango-devel
BuildRequires:  cairo-gobject-devel
BuildRequires:  clang

# ── Runtime dependencies (minimum) ──────────────────────────────────
Requires:       mesa-dri-drivers
Requires:       mesa-libEGL
Requires:       libwayland-server

# No Recommends — the user picks their own shell, launcher, bar, etc.

%description
A scrollable-tiling Wayland compositor with a custom GetCursorPos
IPC command.

Custom addition:
  niri msg get-cursor-pos        → Cursor position: 1920.5, 1080.0
  niri msg get-cursor-pos --json → {"x":1920.5,"y":1080.0}

Based on niri %{srcver} <https://github.com/niri-wm/niri>.

%prep
%autosetup -n niri-%{commit} -p1

%cargo_prep

# Regenerate .cargo/config.toml: %%cargo_prep inserts offline/local-registry
# sections that prevent fetching from crates.io.  We want a minimal config
# with just the rpm profile and commit env.
cat > .cargo/config.toml << 'CARGO_EOF'
[profile.rpm]
inherits = "release"
debug = %{rustflags_debuginfo}
codegen-units = 1
strip = "none"
lto = "fat"

[env]
NIRI_BUILD_COMMIT = "%{commit}"
CARGO_EOF

%build
# Limit to 1 job to stay within COPR's 2 GB memory limit (niri is large
# and parallel rustc invocations quickly exhaust available RAM).
%{__cargo} build \
  -Z avoid-dev-deps \
  --profile rpm \
  -j2

%install
%cargo_install

install -Dm755 -t %{buildroot}%{_bindir} ./resources/niri-session
install -Dm644 -t %{buildroot}%{_datadir}/wayland-sessions ./resources/niri.desktop
install -Dm644 -t %{buildroot}%{_datadir}/xdg-desktop-portal ./resources/niri-portals.conf
install -Dm644 -t %{buildroot}%{_userunitdir} ./resources/niri.service
install -Dm644 -t %{buildroot}%{_userunitdir} ./resources/niri-shutdown.target

%files
%license LICENSE
%doc README.md
%doc resources/default-config.kdl
%doc docs/wiki
%{_bindir}/niri
%{_bindir}/niri-session
%{_datadir}/wayland-sessions/niri.desktop
%dir %{_datadir}/xdg-desktop-portal
%{_datadir}/xdg-desktop-portal/niri-portals.conf
%{_userunitdir}/niri.service
%{_userunitdir}/niri-shutdown.target

%changelog
* Thu Jun 04 2026 TurkeyC <caoturkey@example.com> - 26.4.0-1.dev%{shortcommit}
- virtual pointer: skip Overlay layer for click-through support
- Custom build adding GetCursorPos IPC command

* Wed Jun 03 2026 TurkeyC <caoturkey@example.com> - 26.4.0-1.devba33846
- Custom build adding GetCursorPos IPC command
