# Conditional builds
# _without_x509
# _with_klips
# _with_smp
# _with_oldconfig

%define x509ver		 x509patch-0.9.11

Summary:	Free IPSEC implemetation
Summary(pl):	Publicznie dostêpna implementacja IPSEC
Name:		freeswan
Version:	1.97
Release:	0.4
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
Patch6:		kernel-freeswan-bridge.patch
#Patch6:		%{name}-kernel-module.patch
#Patch7:		%{name}-make-module.patch
URL:		http://www.freeswan.org/
Prereq:		/sbin/chkconfig
Prereq:		rc-scripts
BuildRequires:	gmp-devel
BuildRequires:	kernel-source
BuildRequires:  kernel-headers
BuildRequires:	kernel-doc
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
Requires: 	gmp

%define klips 1
%{?_without_klips:%define klips 0}
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

%if %{klips}
%package -n kernel-%{_kernel_ver}-ipsec
Summary: FreeS/WAN IPSec kernel module
Summary(pl): Modu³ IPSec do j±dra
Group: System Environment/Kernel
Requires: freeswan
%endif

%if %{klips}
%description -n kernel-%{_kernel_ver}-ipsec
FreeS/WAN IPSec Kernel Module (KLIPS)

%description -l pl 
Modu³ j±dra do IPSec
%endif


%prep
%setup  -q -a2

%if %{klips}
cp -pR %{_kernelsrcdir}/ linux
%endif

%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1

%if %{klips}
%patch6 -p1
#%patch7 -p1
%endif

%{?!_without_x509:patch -p1 <%{x509ver}-%{name}-%{version}/freeswan.diff}
%{?!_without_x509:%patch5 -p1 }



%build

%if %{klips}

cd linux
if [ -f .config ]; then
    cat %{SOURCE3} >> .config	
	
else
    echo "ERROR: There is no kernel configuration available."
    echo "Configure your kernel first and add --with oldconfig"
    echo "to rpmbuild command line when trying to build with"
    echo "klips module next time."
    exit 1

#  make oldconfig_nonint 1>/dev/null 2>&1
fi
%{__make} -s include/linux/version.h
cd ..
%endif

USERCOMPILE="%{rpmcflags}" ; export USERCOMPILE
OPT_FLAGS="%{rpmcflags}"; export OPT_FLAGS
CC=%{__cc}; export CC
%{__make}   %{?!_without_klips:KERNELSRC=linux precheck insert ocf module}  programs

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

%if %{klips}
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc
install linux/net/ipsec/ipsec.o $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc/ipsec.o
%endif

bzip2 -dc %{SOURCE1} | tar xf - -C $RPM_BUILD_ROOT%{_mandir}

gzip -9nf README CREDITS CHANGES BUGS \
          doc/{kernel.notes,impl.notes,examples,prob.report,standards} 
		

%clean
rm -rf $RPM_BUILD_ROOT

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

%if %{klips}
%files -n kernel%{?_with_smp:-smp}-%{_kernel_ver}%{?kext:-%{kext}}-ipsec
%defattr(644,root,root,755)
/lib/modules/%{kverrel}/kernel/net/ipsec
%endif
