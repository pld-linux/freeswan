Summary:	Free IPSEC implemetation
Summary:	Publicznie dostêpna implementacja IPSEC
Name:		freeswan
Version:	1.5
Release:	1
License:	GPL
Group:		Networking/Daemons
Group(pl):	Sieciowe/Serwery
Source0:	ftp://ftp.xs4all.nl/pub/crypto/freeswan/%{name}-%{version}.tar.gz
Patch0:		%{name}-Makefiles.patch	
Patch1:		%{name}-manlink.patch	
Patch2:		%{name}-config.patch	
Patch3:		%{name}-init.patch	
URL:		http://www.freeswan.org/
Prereq:		/sbin/chkconfig
Requires:	rc-scripts
BuildRequires:	gmp-devel
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
The basic idea of IPSEC is to provide security functions
(authentication and encryption) at the IP (Internet Protocol)
level. It will be required in IP version 6 (better known as IPng,
the next generation) and is optional for the current IP, version 4.

FreeS/WAN is a freely-distributable implementation of IPSEC protocol.

%prep
%setup  -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1

%build
OPT_FLAGS="$RPM_OPT_FLAGS"; export OPT_FLAGS
%{__make} programs

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir}/freeswan,/etc/rc.d/init.d,/var/run/pluto}

%{__make} install \
	DESTDIR="$RPM_BUILD_ROOT" 

gzip -9nf README CREDITS CHANGES BUGS \
          doc/{kernel.notes,impl.notes,examples,prob.report,standards}

%post
/sbin/chkconfig --add ipsec 
if [ -f /var/lock/subsys/ipsec ]; then
	/etc/rc.d/init.d/ipsec restart >&2
else
	echo "Run '/etc/rc.d/init.d/ipsec start' to start IPSEC services." >&2
fi
    
%preun
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/ipsec ]; then
		/etc/rc.d/init.d/ipsec stop >&2
	fi
        /sbin/chkconfig --del ipsec >&2
fi

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc *.gz doc/*.gz doc/*.html
%{_mandir}/man*/*
%attr(755,root,root) %{_sbindir}/*
%attr(754,root,root) /etc/rc.d/init.d/*
%dir %{_libdir}/ipsec
%attr(755,root,root) %{_libdir}/ipsec/*
%attr(751,root,root) %dir %{_sysconfdir}/freeswan
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/freeswan/*
