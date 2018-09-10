Name:     linstor-xen
Version:  0.1
Release:  1
Summary:  LINSTOR integration for XEN
License:  GPLv3+
URL:      https://github.com/LINBIT/linstor-xen
Source0:  https://linbit.com/TODO/%{name}-%{version}.tar.gz

%define PYTHONDIR %{python_sitelib}/xapi/storage/linstor
%define SCRIPTDIR /usr/libexec/xapi-storage-script

%description
This plugin integrates LINSTOR in XEN.
It implements the xapi storage API v5.

%prep
%setup -q

%install
%make_install PYTHONDIR=%{PYTHONDIR} SCRIPTDIR=%{SCRIPTDIR}

%files
%{PYTHONDIR}/
%{SCRIPTDIR}/volume/org.xen.xapi.storage.linstor/
%{SCRIPTDIR}/datapath/linstor/

%changelog
* Fri Feb 01 2019 Roland Kammerer <roland.kammerer@linbit.com> 0.1-1
-  Initial version of the package
