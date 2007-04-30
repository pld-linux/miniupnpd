#
%define pre RC4
Summary:	Small UPnP Daemon
Name:		miniupnpd
Version:	1.0
Release:	0.%{pre}.1
License:	BSD
Group:		Applications
Source0:	http://miniupnp.free.fr/files/%{name}-%{version}-RC4.tar.gz
# Source0-md5:	de6fd266bf15c4f6781895d19c8efbca
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Source3:	%{name}.conf
URL:		http://miniupnp.free.fr/
BuildRequires:	iptables-devel
BuildRequires:	rpmbuild(macros) >= 1.228
Requires(post):	libuuid
Requires(post,preun):	/sbin/chkconfig
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description

%prep
%setup -q -n %{name}-%{version}-%{pre}

%build
%{__make} -f Makefile.linux

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/{%{_sbindir},%{_sysconfdir}/rc.d/init.d,%{_sysconfdir}/sysconfig,%{_sysconfdir}/%{name}}

install miniupnpd $RPM_BUILD_ROOT/%{_sbindir}
install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{name}
install %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ ! -f %{_sysconfdir}/miniupnpd/uuid ] ; then
	echo "Generating UPnP uuid..."
	umask 066
	uuidgen > %{_sysconfdir}/miniupnpd/uuid
fi

if [ -f %{_sysconfdir}/miniupnpd/uuid ] ; then
	UUID=`cat %{_sysconfdir}/miniupnpd/uuid`
	if [ -n "$UUID" ] ; then
		echo "Updating UUID in miniupnpd config file..."
   	%{__sed} -i -e "s/^uuid=[-0-9a-f]*/uuid=`cat %{_sysconfdir}/miniupnpd/uuid`/" %{_sysconfdir}/miniupnpd/miniupnpd.conf
	fi
fi

/sbin/chkconfig --add %{name}
%service %{name} restart

%preun
if [ "$1" = "0" ]; then
	%service -q %{name} stop
	/sbin/chkconfig --del %{name}
fi

%files
%defattr(644,root,root,755)
%doc README
%attr(755,root,root) %{_sbindir}/miniupnpd
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%dir %{_sysconfdir}/%{name}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/%{name}.conf
