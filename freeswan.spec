# Conditional builds
# _without_x509
# _with_smp
# _with_oldconfig

%define x509ver		 x509patch-0.9.11

Summary:	Free IPSEC implemetation
Summary(pl):	Publicznie dostêpna implementacja IPSEC
Name:		freeswan
Version:	1.97
Release:	1
License:	GPL
Group:		Networking/Daemons
Source0:	ftp://ftp.xs4all.nl/pub/crypto/%{name}/%{name}-%{version}.tar.gz
Source1:	http://www.mif.pg.gda.pl/homepages/ankry/man-PLD/%{name}-pl-man-pages.tar.bz2
Source2:	http://www.strongsec.com/%{name}/%{x509ver}-%{name}-%{version}.tar.gz
Source3:	%{name}-kernel.config
Patch0:		%{name}-Makefile.patch
Patch1:		%{name}-manlink.patch
Patch2:		%{name}-config.patch
Patch3:		%{name}-init.patch
Patch4:		%{name}-keygen.patch
Patch5:		x509-config.patch
URL:		http://www.freeswan.org/
Prereq:		/sbin/chkconfig
Prereq:		rc-scripts
BuildRequires:	gmp-devel
BuildRequires:	kernel-source
BuildRequires:  kernel-headers
BuildRequires:	kernel-doc
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
Requires: 	gmp

%define x509 1
%{?_without_x509:%define x509 0}

%description
The basic idea of IPSEC is to provide security functions
(authentication and encryption) at the IP (Internet Protocol) level.
It will be required in IP version 6 (better known as IPng, the next
generation) and is optional for the current IP, version 4.

FreeS/WAN is a freely-distributable implementation of IPSEC protocol.
FreeS/WAN utilities%{?!_without_x509: compiled with X.509 certificate support}.

%description -l pl
Podstawowa idea IPSEC to zapewnienie funkcji bezpieczeñstwa
(autentykacji i szyfrowania) na poziomie IP. Bêdzie wymagany do IP w
wersji 6 (znanego tak¿e jako IPng, IP nastêpnej generacji) i jest
opcjonalny dla aktualnego IP, w wersji 4.

FreeS/WAN jest darmow± implementacj± protoko³u IPSEC.

%prep
%setup  -q -a2

%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1

%{?!_without_x509:patch -p1 <%{x509ver}-%{name}-%{version}/freeswan.diff}
%{?!_without_x509:%patch5 -p1 }

%build

USERCOMPILE="%{rpmcflags}" ; export USERCOMPILE
OPT_FLAGS="%{rpmcflags}"; export OPT_FLAGS
CC=%{__cc}; export CC
%{__make} programs

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir}/ipsec,/etc/rc.d/init.d,/var/run/pluto}

%{__make} install \
	DESTDIR="$RPM_BUILD_ROOT"

%if %{x509}
 install -d  $RPM_BUILD_ROOT%{_sysconfdir}/ipsec.d
 for i in crls cacerts private; do
  install -d  $RPM_BUILD_ROOT%{_sysconfdir}/ipsec.d/$i
done
for i in CHANGES README; do
  install  %{x509ver}-%{name}-%{version}/$i $i.x509 ;	
	gzip -9nf $i.x509 ;

done
%endif

bzip2 -dc %{SOURCE1} | tar xf - -C $RPM_BUILD_ROOT%{_mandir}

gzip -9nf README CREDITS CHANGES BUGS \
          doc/{kernel.notes,impl.notes,examples,prob.report,standards} 
		


%post
# generate RSA private key... if, and only if, /etc/ipsec/ipsec.secrets does
# not already exist
if [ ! -f %{_sysconfdir}/ipsec/ipsec.secrets ];
then
    echo generate RSA private key...
    /usr/sbin/ipsec newhostkey --output %{_sysconfdir}/ipsec/ipsec.secrets
    chmod 600 %{_sysconfdir}/ipsec/ipsec.secrets
fi

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
%{?!_without_x509:%doc CHANGES.x509.gz README.x509.gz}
%{_mandir}/man*/*
%lang(pl) %{_mandir}/pl/man*/*
%attr(755,root,root) %{_sbindir}/*
%attr(754,root,root) /etc/rc.d/init.d/*
%dir %{_libdir}/ipsec
%attr(755,root,root) %{_libdir}/ipsec/*
%attr(751,root,root) %dir %{_sysconfdir}/ipsec
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/ipsec/*
%if %{x509}
%attr(0700,root,root) %dir %{_sysconfdir}/ipsec.d
%attr(0700,root,root) %dir %{_sysconfdir}/ipsec.d/crls
%attr(0700,root,root) %dir %{_sysconfdir}/ipsec.d/cacerts
%attr(0700,root,root) %dir %{_sysconfdir}/ipsec.d/private
%endif
