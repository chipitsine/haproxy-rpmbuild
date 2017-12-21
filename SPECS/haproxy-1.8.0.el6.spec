%define haproxy_user    haproxy
%define haproxy_group   %{haproxy_user}
%define haproxy_home    %{_localstatedir}/lib/haproxy
%define haproxy_confdir %{_sysconfdir}/haproxy
%define haproxy_datadir %{_datadir}/haproxy

Summary:        HA-Proxy is a TCP/HTTP reverse proxy for high availability environments
Name:           haproxy
Version:        1.8.0
Release:        1%{?dist}
License:        GPL
Group:          System Environment/Daemons
URL:            http://www.haproxy.org/
Source0:        http://www.haproxy.org/download/1.8/src/%{name}-%{version}.tar.gz
Source1:        https://raw.githubusercontent.com/AxisNL/haproxy-rpmbuild/master/SOURCES/%{name}.cfg
Source2:        https://raw.githubusercontent.com/AxisNL/haproxy-rpmbuild/master/SOURCES/%{name}.logrotate

BuildRoot:      %{_tmppath}/%{name}-%{version}-root
BuildRequires:  pcre-devel
Requires:       /sbin/chkconfig, /sbin/service

%description
This version of HAProxy is a build from the official haproxy sources, see https://haproxy.hongens.nl.

HA-Proxy is a TCP/HTTP reverse proxy which is particularly suited for high
availability environments. Indeed, it can:
- route HTTP requests depending on statically assigned cookies
- spread the load among several servers while assuring server persistence
  through the use of HTTP cookies
- switch to backup servers in the event a main one fails
- accept connections to special ports dedicated to service monitoring
- stop accepting connections without breaking existing ones
- add/modify/delete HTTP headers both ways
- block requests matching a particular pattern

It needs very little resource. Its event-driven architecture allows it to easily
handle thousands of simultaneous connections on hundreds of instances without
risking the system's stability.

%prep
%setup -q

# We don't want any perl dependecies in this RPM:
%define __perl_requires /bin/true

%build
%{__make} USE_PCRE=1 DEBUG="" ARCH=%{_target_cpu} TARGET=linux26

%install
[ "%{buildroot}" != "/" ] && %{__rm} -rf %{buildroot}

%{__install} -d %{buildroot}%{_sbindir}
%{__install} -d %{buildroot}%{_sysconfdir}/rc.d/init.d
%{__install} -d %{buildroot}%{_sysconfdir}/%{name}
%{__install} -d %{buildroot}%{_mandir}/man1/
%{__install} -p -D -m 0644 %{SOURCE1} %{buildroot}%{haproxy_confdir}/%{name}.cfg
%{__install} -p -D -m 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
%{__install} -s %{name} %{buildroot}%{_sbindir}/
%{__install} -c -m 755 examples/%{name}.init %{buildroot}%{_sysconfdir}/rc.d/init.d/%{name}
%{__install} -c -m 755 doc/%{name}.1 %{buildroot}%{_mandir}/man1/

%clean
[ "%{buildroot}" != "/" ] && %{__rm} -rf %{buildroot}

%post
/sbin/chkconfig --add %{name}

%preun
if [ $1 = 0 ]; then
  /sbin/service %{name} stop >/dev/null 2>&1 || :
  /sbin/chkconfig --del %{name}
fi

%postun
if [ "$1" -ge "1" ]; then
  /sbin/service %{name} condrestart >/dev/null 2>&1 || :
fi

%files
%defattr(-,root,root)
%doc CHANGELOG README doc/architecture.txt doc/configuration.txt doc/intro.txt doc/management.txt doc/proxy-protocol.txt
%doc %{_mandir}/man1/%{name}.1*
%attr(0755,root,root) %{_sbindir}/%{name}
%dir %{_sysconfdir}/%{name}
%config(noreplace) %{haproxy_confdir}/%{name}.cfg
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%attr(0755,root,root) %config %{_sysconfdir}/rc.d/init.d/%{name}
