%global qt_version 5.15.8

Summary: Qt5 - Sensors component
Name:    opt-qt5-qtsensors
Version: 5.15.8
Release: 3%{?dist}

# See LGPL_EXCEPTIONS.txt, LICENSE.GPL3, respectively, for exception details
License: LGPL-3.0-only OR GPL-3.0-only WITH Qt-GPL-exception-1.0
Url:     http://www.qt.io/
Source0: %{name}-%{version}.tar.bz2

# filter qml/plugin provides
%global __provides_exclude_from ^(%{_opt_qt5_archdatadir}/qml/.*\\.so|%{_opt_qt5_plugindir}/.*\\.so)$
%{?opt_qt5_default_filter}

BuildRequires: make
BuildRequires: opt-qt5-qtbase-devel >= %{qt_version}
BuildRequires: opt-qt5-qtbase-private-devel
BuildRequires: sensorfw-qt5-devel
BuildRequires: opt-qt5-qtdeclarative-devel
%{?_opt_qt5:Requires: %{_opt_qt5}%{?_isa} = %{_opt_qt5_version}}
Requires: opt-qt5-qtdeclarative >= %{qt_version}

%description
The Qt Sensors API provides access to sensor hardware via QML and C++
interfaces.  The Qt Sensors API also provides a motion gesture recognition
API for devices.

%package devel
Summary: Development files for %{name}
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: opt-qt5-qtbase-devel%{?_isa}
%description devel
%{summary}.

%prep
%autosetup -n %{name}-%{version}/upstream


%build
export QTDIR=%{_opt_qt5_prefix}
touch .git

%{opt_qmake_qt5} CONFIG+=sensorfw

# have to restart build several times due to bug in sb2
%make_build  -k || chmod -R ugo+r . || true
%make_build

# bug in sb2 leading to 000 permission in some generated plugins.qmltypes files
chmod -R ugo+r .

%install
make install INSTALL_ROOT=%{buildroot}

## .prl/.la file love
# nuke .prl reference(s) to %%buildroot, excessive (.la-like) libs
pushd %{buildroot}%{_opt_qt5_libdir}
for prl_file in libQt5*.prl ; do
  sed -i -e "/^QMAKE_PRL_BUILD_DIR/d" ${prl_file}
  if [ -f "$(basename ${prl_file} .prl).so" ]; then
    rm -fv "$(basename ${prl_file} .prl).la"
    sed -i -e "/^QMAKE_PRL_LIBS/d" ${prl_file}
  fi
done
popd

#Move system config file
mkdir -p %{buildroot}/opt/qt5/etc/xdg/QtProject/
mv %{buildroot}/etc/xdg/QtProject/Sensors.conf %{buildroot}/opt/qt5/etc/xdg/QtProject/Sensors.conf

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%license LICENSE.*
%{_opt_qt5_libdir}/libQt5Sensors.so.5*
%{_opt_qt5_plugindir}/sensorgestures/
%{_opt_qt5_plugindir}/sensors/
%{_opt_qt5_archdatadir}/qml/QtSensors/
%dir %{_opt_qt5_libdir}/cmake/Qt5Sensors/
%{_opt_qt5_libdir}/cmake/Qt5Sensors/Qt5Sensors_*Plugin.cmake
%{_opt_qt5_prefix}/etc/xdg/QtProject/Sensors.conf

%files devel
%{_opt_qt5_headerdir}/QtSensors/
%{_opt_qt5_libdir}/libQt5Sensors.so
%{_opt_qt5_libdir}/libQt5Sensors.prl
%{_opt_qt5_libdir}/cmake/Qt5Sensors/Qt5SensorsConfig*.cmake
%{_opt_qt5_libdir}/pkgconfig/Qt5Sensors.pc
%{_opt_qt5_archdatadir}/mkspecs/modules/qt_lib_sensors*.pri
