Summary:	Small UPnP Daemon
Summary(pl.UTF-8):	Mały demon UPnP
Name:		miniupnpd
Version:	1.7
Release:	2
License:	BSD
Group:		Networking/Daemons
Source0:	http://miniupnp.tuxfamily.org/files/%{name}-%{version}.tar.gz
# Source0-md5:	5af9e8332d34a7b490d0d2ed3e674196
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Source3:	%{name}.conf
URL:		http://miniupnp.tuxfamily.org/
BuildRequires:	iptables-devel >= 1.4.3
BuildRequires:	rpmbuild(macros) >= 1.228
Requires(post):	libuuid
Requires(post):	sed >= 4.0
Requires(post,preun):	/sbin/chkconfig
Requires:	iptables-libs >= 1.4.3
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Small UPnP Daemon.

%description -l pl.UTF-8
Mały demon UPnP.

%prep
%setup -q

%build
%{__make} -f Makefile.linux -j1 \
	CC="%{__cc}" \
	CFLAGS="%{rpmcflags} -fno-strict-aliasing -Wall -D_GNU_SOURCE -DIPTABLES_143" \
	LIBS="-lip4tc -lip6tc"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sbindir},/etc/rc.d/init.d,/etc/sysconfig,%{_sysconfdir}/%{name}}
install miniupnpd $RPM_BUILD_ROOT%{_sbindir}
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/%{name}
install %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/%{name}

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ ! -f %{_sysconfdir}/miniupnpd/uuid ]; then
	echo "Generating UPnP uuid..."
	umask 066
	uuidgen > %{_sysconfdir}/miniupnpd/uuid
fi

if [ -f %{_sysconfdir}/miniupnpd/uuid ]; then
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
%doc Changelog.txt LICENSE README
%attr(755,root,root) %{_sbindir}/miniupnpd
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%dir %{_sysconfdir}/%{name}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/%{name}.conf
