Summary:	Free IPSEC implemetation
Name:		freeswan
Version:	1.3
Release:	0
License:	GPL
Group:		Networking/Daemons
Group(pl):	Sieciowe/Serwery
Source0:	ftp://ftp.xs4all.nl/pub/crypto/freeswan/%{name}-%{version}.tar.gz
Patch0:		%{name}-Makefiles.patch	
Patch1:		%{name}-manlink.patch	
Patch2:		%{name}-config.patch	
Patch3:		%{name}-init.patch	
URL:		http://www.freeswan.org
Prereq:		/sbin/chkconfig
Requires:	rc-scripts
BuildRequires:  gmp-devel
BuildRoot:	/tmp/%{name}-%{version}-root

%description
The   basic   idea   of   IPSEC   is  to  provide  security  functions
([60]authentication  and [61]encryption) at the IP (Internet Protocol)
level.  It will be required in [62]IP version 6 (better known as IPng,
the next generation) and is optional for the current IP, version 4.

FreeS/WAN is a freely-distributable implementation of IPSEC protocol/

%prep
%setup  -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1

%build
OPT_FLAGS="$RPM_OPT_FLAGS"; export OPT_FLAGS
LDFLAGS="-s"; export LDFLAGS
make programs

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT{/etc/{freeswan,rc.d/init.d},/var/run/pluto}
make install DESTDIR="$RPM_BUILD_ROOT" 

gzip -9nf README CREDITS CHANGES BUGS \
          doc/{kernel.notes,impl.notes,examples,prob.report,standards} \
	  $RPM_BUILD_ROOT%{_mandir}/man*/*

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
%dir /usr/lib/ipsec
%attr(755,root,root) /usr/lib/ipsec/*
%attr(751,root,root) %dir /etc/freeswan
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) /etc/freeswan/*
