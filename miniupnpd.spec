# TODO
# - iptables or kernel headers messup:
# - th:
#   linux/iptcrdr.c:17:22: error: iptables.h: No such file or directory
#   linux/iptcrdr.c:18:41: error: linux/netfilter_ipv4/ip_nat.h: No such file or directory
#   linux/iptcrdr.c: In function 'get_redirect_rule':
# - ac:
#   netfilter/iptcrdr.c:23:36: linux/netfilter/nf_nat.h: No such file or directory
Summary:	Small UPnP Daemon
Summary(pl.UTF-8):	Mały demon UPnP
Name:		miniupnpd
Version:	1.2
Release:	0.1
License:	BSD
Group:		Applications
Source0:	http://miniupnp.tuxfamily.org/files/%{name}-%{version}.tar.gz
# Source0-md5:	48f1fa81e5c2cb1c561c29cdcf261602
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Source3:	%{name}.conf
URL:		http://miniupnp.tuxfamily.org/
BuildRequires:	iptables-devel
BuildRequires:	rpmbuild(macros) >= 1.228
Requires(post):	libuuid
Requires(post):	sed >= 4.0
Requires(post,preun):	/sbin/chkconfig
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Small UPnP Daemon.

%description -l pl.UTF-8
Mały demon UPnP.

%prep
%setup -q

%build
%{__make} -f Makefile.linux \
	CC="%{__cc}" \
	CFLAGS="%{rpmcflags} -Wall -D_GNU_SOURCE"

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
%doc README
%attr(755,root,root) %{_sbindir}/miniupnpd
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%dir %{_sysconfdir}/%{name}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/%{name}.conf
