# TODO: handle ip*tables_{init,removeall} in PLD init script? (see bundled one)
Summary:	Small UPnP Daemon
Summary(pl.UTF-8):	Mały demon UPnP
Name:		miniupnpd
Version:	2.1
Release:	3
License:	BSD
Group:		Networking/Daemons
Source0:	http://miniupnp.tuxfamily.org/files/%{name}-%{version}.tar.gz
# Source0-md5:	91d0524bba6a839c05c22c9484ed9d0f
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Source3:	%{name}.conf
Patch0:		%{name}-netfilter.patch
URL:		http://miniupnp.tuxfamily.org/
BuildRequires:	iptables-devel >= 1.4.3
BuildRequires:	libmnl-devel >= 1.0.3
BuildRequires:	libnetfilter_conntrack-devel >= 1.0.2
BuildRequires:	libuuid-devel
BuildRequires:	openssl-devel
BuildRequires:	rpmbuild(macros) >= 1.228
Requires(post):	libuuid
Requires(post):	sed >= 4.0
Requires(post,preun):	/sbin/chkconfig
Requires:	iptables-libs >= 1.4.3
Requires:	libmnl >= 1.0.3
Requires:	libnetfilter_conntrack >= 1.0.2
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Small UPnP Daemon.

%description -l pl.UTF-8
Mały demon UPnP.

%prep
%setup -q
%patch0 -p1

%build
CPPFLAGS="%{rpmcppflags}" \
CFLAGS="%{rpmcflags}" \
LDFLAGS="%{rpmldflags}" \
%{__make} -f Makefile.linux -j1 \
	CC="%{__cc}"

%install
rm -rf $RPM_BUILD_ROOT

%{__make} -f Makefile.linux install \
	DESTDIR=$RPM_BUILD_ROOT \
	STRIP=:

# replace init script and config file by PLD specific ones
%{__rm} -r $RPM_BUILD_ROOT/etc/init.d
install -Dp %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install -Dp %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/%{name}
cp -p %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/%{name}

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ ! -f %{_sysconfdir}/miniupnpd/uuid ]; then
	echo "Generating UPnP uuid..."
	umask 077
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
%attr(755,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/ip6tables_init.sh
%attr(755,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/ip6tables_removeall.sh
%attr(755,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/iptables_init.sh
%attr(755,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/iptables_removeall.sh
%{_sysconfdir}/%{name}/miniupnpd_functions.sh
%{_mandir}/man8/miniupnpd.8*
