Name:           zed
Version:        1.16.1
Release:        0
%global debug_package %{nil}
Summary:        High-performance, multiplayer code editor
License:        GPL-3.0-only AND Apache-2.0
URL:            https://zed.dev/
Source0:        zed-linux-x86_64.tar.gz
Source1:        zed-launcher
Source2:        LICENSE-GPL
Source3:        LICENSE-APACHE
BuildRequires:  desktop-file-utils
BuildRequires:  hicolor-icon-theme
Requires:       bash
Requires:       hicolor-icon-theme
ExclusiveArch:  x86_64

# The upstream tarball bundles private copies of a handful of X11/GLib
# libraries next to the binaries and loads them through a $ORIGIN-relative
# RPATH; they must not be advertised as system-wide library Provides.
%global __provides_exclude_from ^%{_libexecdir}/zed/lib/.*\\.so.*$

%description
Zed is a high-performance, multiplayer code editor with built-in
collaboration, AI-assisted editing, and a GPU-accelerated renderer. This
package repackages the upstream prebuilt Linux binary release for the
signed Lyra OS OBS repositories and points Zed's own auto-updater at
Zypper instead of its bundled updater.

%prep
%setup -q -c -T
tar -xzf %{SOURCE0}
cp %{SOURCE2} %{SOURCE3} .

%build
# Prebuilt upstream binary release; there is no compilation step.

%install
mkdir -p %{buildroot}%{_libexecdir}/zed
cp -a zed.app/bin zed.app/lib zed.app/libexec %{buildroot}%{_libexecdir}/zed/
strip -s %{buildroot}%{_libexecdir}/zed/bin/zed
strip -s %{buildroot}%{_libexecdir}/zed/libexec/zed-editor
chmod 0755 %{buildroot}%{_libexecdir}/zed/lib/*.so*

install -D -m 0644 zed.app/share/applications/dev.zed.Zed.desktop \
    %{buildroot}%{_datadir}/applications/dev.zed.Zed.desktop
mkdir -p %{buildroot}%{_datadir}/icons/hicolor
cp -a zed.app/share/icons/hicolor/. %{buildroot}%{_datadir}/icons/hicolor/

install -D -m 0755 %{SOURCE1} %{buildroot}%{_bindir}/zed

desktop-file-validate %{buildroot}%{_datadir}/applications/dev.zed.Zed.desktop

%check
grep -q 'ZED_UPDATE_EXPLANATION' %{buildroot}%{_bindir}/zed
test -x %{buildroot}%{_bindir}/zed
test -x %{buildroot}%{_libexecdir}/zed/bin/zed
test -x %{buildroot}%{_libexecdir}/zed/libexec/zed-editor
grep -qxF 'Exec=zed %U' %{buildroot}%{_datadir}/applications/dev.zed.Zed.desktop
bash -n %{buildroot}%{_bindir}/zed

%files
%license LICENSE-GPL LICENSE-APACHE zed.app/licenses.md
%{_bindir}/zed
%{_libexecdir}/zed/
%{_datadir}/applications/dev.zed.Zed.desktop
%{_datadir}/icons/hicolor/*/apps/*

%changelog
