# Conditional builds
%bcond_with	NAT		# with NAT-Traversal
%bcond_without	x509		# without x509 support
%bcond_without	dist_kernel	# without sources of distribution kernel
%bcond_without	modules		# build only library+programs, no kernel modules
#
%define x509ver		x509-1.4.8
%define nat_tr_ver	0.6
%define _25x_ver	20030825
Summary:	Free IPSEC implemetation
Summary(pl):	Publicznie dostêpna implementacja IPSEC
Name:		freeswan
Version:	2.04
%define	_rel	0.1
Release:	%{_rel}
License:	GPL
Group:		Networking/Daemons
Source0:	ftp://ftp.xs4all.nl/pub/crypto/freeswan/%{name}-%{version}.tar.gz
# Source0-md5:	37a15f760ca43317fe7c5d6e6859689c
Source1:	http://www.mif.pg.gda.pl/homepages/ankry/man-PLD/%{name}-pl-man-pages.tar.bz2
# Source1-md5:	6bd0b509015a2795cfb895aaab0bbc55
Source2:	http://www.strongsec.com/freeswan/%{x509ver}-%{name}-%{version}.tar.gz
# Source2-md5:	d5ff93ed3dc33afcc3ab5d00ca11008b
Source3:	http://open-source.arkoon.net/freeswan/NAT-Traversal-%{nat_tr_ver}.tar.gz
# Source3-md5:	6858a8535aa2611769d17e86e6735db2
Patch0:		%{name}-showhostkey.patch
Patch1:		%{name}-init.patch
Patch2:		%{name}-paths.patch
Patch3:		%{name}-confread.patch
URL:		http://www.freeswan.org/
BuildRequires:	gmp-devel
BuildRequires:	rpmbuild(macros) >= 1.118
Requires:	rc-scripts
%{?with_dist_kernel:%{?with_modules:BuildRequires:	kernel-doc}}
%{?with_dist_kernel:%{?with_modules:BuildRequires:	kernel-headers}}
%{?with_dist_kernel:%{?with_modules:BuildRequires:	kernel-source}}
Requires(post,preun):	/sbin/chkconfig
Requires:	gawk
Requires:	gmp
# XFree86 is required to use usefull lndir
%{?with_dist_kernel:%{?with_modules:BuildRequires:	XFree86}}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This package contains FreeS/WAN daemon and utilities. FreeS/WAN is a
free implementation of the IPsec protocol for Linux. It allows to
build secure tunnels through untrusted networks. The basic idea of
IPsec is to provide security functions (authentication and encryption)
at the IP (Internet Protocol) level.

%description -l pl
Ten pakiet zawiera demona i narzêdzia FreeS/WAN. FreeS/WAN jest woln±
implementacj± protoko³u IPsec dla Linuksa. Umo¿liwia zestawianie
bezpiecznych tuneli przez niezaufane sieci. Podstawowa idea IPsec to
zapewnienie funkcji bezpieczeñstwa (autentykacji i szyfrowania) na
poziomie IP.

%package -n kernel-net-ipsec
Summary:	Kernel module for Linux IPSEC
Summary(pl):	Modu³ j±dra dla IPSEC
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires:	modutils >= 2.4.6-4
Requires(post,postun):	/sbin/depmod
Requires:	%{name} = %{version}
Conflicts:	kernel <= 2.4.20-9

%description -n kernel-net-ipsec
Kernel module for FreeS/WAN.

%description -n kernel-net-ipsec -l pl
Modu³ j±dra wykorzystywany przez FreeS/WAN.

%package -n kernel-smp-net-ipsec
Summary:	SMP kernel module for Linux IPSEC
Summary(pl):	Modu³ j±dra SMP dla IPSEC
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires:	modutils >= 2.4.6-4
Requires(post,postun):	/sbin/depmod
Requires:	%{name} = %{version}
Conflicts:	kernel-smp <= 2.4.20-9

%description -n kernel-smp-net-ipsec
SMP kernel module for FreeS/WAN.

%description -n kernel-smp-net-ipsec -l pl
Modu³ j±dra SMP wykorzystywany przez FreeS/WAN.

%prep
%setup -q -a2 -a3
%patch0 -p1
%patch1 -p1
%{?with_x509:patch -p1 -s <%{x509ver}-%{name}-%{version}/freeswan.diff}
%patch3 -p1
%{?with_NAT:patch -p1 -s <NAT-Traversal-%{nat_tr_ver}/NAT-Traversal-%{nat_tr_ver}-freeswan-2.00-x509-1.3.5.diff}

%build
%define	_kver	`echo "%{_kernel_ver}" |awk -F. '{print $2}'`

%if %{with modules}
install -d kernelsrc
lndir -silent %{_kernelsrcdir} kernelsrc
mv kernelsrc/.config kernelsrc/.config.old
cp kernelsrc/.config.old kernelsrc/.config

%if %{with dist_kernel}
rm -rf kernelsrc/include/asm
cd kernelsrc
patch -R -p1 <../linux/net/Makefile.fs2_%{_kver}.patch
patch -R -p1 <../linux/net/Config.in.fs2_%{_kver}.patch
patch -R -p1 <../linux/net/ipv4/af_inet.c.fs2_%{_kver}.patch
patch -R -p1 <../linux/Documentation/Configure.help.fs2_%{_kver}.patch
cd ..
rm -rf kernelsrc/{crypto,include/{freeswan,zlib,crypto},lib/{zlib,libfreeswan},net/ipsec}
rm kernelsrc/include/{freeswan,pfkey,pfkeyv2}.h
cp kernelsrc/config-up kernelsrc/.config
%endif

echo "CONFIG_IPSEC=m" >> kernelsrc/.config
echo "CONFIG_IPSEC_IPIP=y" >> kernelsrc/.config
echo "CONFIG_IPSEC_AH=y" >> kernelsrc/.config
echo "CONFIG_IPSEC_AUTH_HMAC_MD5=y" >> kernelsrc/.config
echo "CONFIG_IPSEC_AUTH_HMAC_SHA1=y" >> kernelsrc/.config
echo "CONFIG_IPSEC_ESP=y" >> kernelsrc/.config
echo "CONFIG_IPSEC_ENC_3DES=y" >> kernelsrc/.config
echo "CONFIG_IPSEC_IPCOMP=y" >> kernelsrc/.config
echo "CONFIG_IPSEC_DEBUG=y" >> kernelsrc/.config
%endif

USERCOMPILE="%{rpmcflags}" ; export USERCOMPILE
OPT_FLAGS="%{rpmcflags}"; export OPT_FLAGS
CC="%{__cc}"; export CC


%if %{with modules}
%{__make} precheck verset kpatch ocf confcheck module \
	BIND9STATICLIBDIR=%{_libdir} \
	FINALCONFDIR=%{_sysconfdir}/ipsec \
	FINALCONFFILE=%{_sysconfdir}/ipsec/ipsec.conf \
	INC_USRLOCAL=/usr \
	INC_MANDIR=share/man \
	FINALRCDIR=%{_sysconfdir}/rc.d/init.d \
	FINALLIBEXECDIR=%{_libdir}/ipsec \
	KERNELSRC="`pwd`/kernelsrc"

install linux/net/ipsec/ipsec.o .

%if %{with smp}
rm -rf kernelsrc
install -d kernelsrc
lndir -silent /usr/src/linux kernelsrc
mv kernelsrc/.config kernelsrc/.config.old
cp kernelsrc/.config.old kernelsrc/.config

%if %{with dist_kernel}
rm -rf kernelsrc/include/asm
cd kernelsrc
patch -R -p1 <../linux/net/Makefile.fs2_%{_kver}.patch
patch -R -p1 <../linux/net/Config.in.fs2_%{_kver}.patch
patch -R -p1 <../linux/net/ipv4/af_inet.c.fs2_%{_kver}.patch
patch -R -p1 <../linux/Documentation/Configure.help.fs2_%{_kver}.patch
cd ..
rm -rf kernelsrc/{crypto,include/{freeswan,zlib,crypto},lib/{zlib,libfreeswan},net/ipsec}
rm kernelsrc/include/{freeswan,pfkey,pfkeyv2}.h
cp kernelsrc/config-smp kernelsrc/.config
%endif

echo "CONFIG_IPSEC=m" >> kernelsrc/.config
echo "CONFIG_IPSEC_IPIP=y" >> kernelsrc/.config
echo "CONFIG_IPSEC_AH=y" >> kernelsrc/.config
echo "CONFIG_IPSEC_AUTH_HMAC_MD5=y" >> kernelsrc/.config
echo "CONFIG_IPSEC_AUTH_HMAC_SHA1=y" >> kernelsrc/.config
echo "CONFIG_IPSEC_ESP=y" >> kernelsrc/.config
echo "CONFIG_IPSEC_ENC_3DES=y" >> kernelsrc/.config
echo "CONFIG_IPSEC_IPCOMP=y" >> kernelsrc/.config
echo "CONFIG_IPSEC_DEBUG=y" >> kernelsrc/.config
%{__make} precheck verset kpatch ocf confcheck module \
	BIND9STATICLIBDIR=%{_libdir} \
	FINALCONFDIR=%{_sysconfdir}/ipsec \
	FINALCONFFILE=%{_sysconfdir}/ipsec/ipsec.conf \
	INC_USRLOCAL=/usr \
	INC_MANDIR=share/man \
	FINALRCDIR=%{_sysconfdir}/rc.d/init.d \
	FINALLIBEXECDIR=%{_libdir}/ipsec \
	KERNELSRC="`pwd`/kernelsrc"
%endif

%endif

%{__make} programs \
	BIND9STATICLIBDIR=%{_libdir} \
	FINALCONFDIR=%{_sysconfdir}/ipsec \
	FINALCONFFILE=%{_sysconfdir}/ipsec/ipsec.conf \
	INC_USRLOCAL=/usr \
	INC_MANDIR=share/man \
	FINALRCDIR=%{_sysconfdir}/rc.d/init.d \
	FINALLIBEXECDIR=%{_libdir}/ipsec \
	KERNELSRC="`pwd`/kernelsrc"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir}/ipsec,/etc/rc.d/init.d,/var/run/pluto}

%{__make} install \
	BIND9STATICLIBDIR=%{_libdir} \
	DESTDIR="$RPM_BUILD_ROOT" \
	FINALCONFDIR=%{_sysconfdir}/ipsec \
	FINALCONFFILE=%{_sysconfdir}/ipsec/ipsec.conf \
	FINALRCDIR=%{_sysconfdir}/rc.d/init.d \
	FINALLIBEXECDIR=%{_libdir}/ipsec \
	FINALEXAMPLECONFDIR=/usr/share/doc/%{name}-%{version} \
	INC_USRLOCAL=/usr \
	INC_MANDIR=share/man


%if %{with x509}
install -d  $RPM_BUILD_ROOT%{_sysconfdir}/ipsec/ipsec.d
for i in crls cacerts private policies; do
	install -d  $RPM_BUILD_ROOT%{_sysconfdir}/ipsec/ipsec.d/$i
done
for i in CHANGES README; do
	install  %{x509ver}-%{name}-%{version}/$i $i.x509 ;
done
%endif

bzip2 -dc %{SOURCE1} | tar xf - -C $RPM_BUILD_ROOT%{_mandir}

%if %{with modules}
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc
install ipsec.o $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc

%if %{with smp}
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/misc
install linux/net/ipsec/ipsec.o $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/misc
%endif

%endif

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

%post	-n kernel-net-ipsec
%depmod %{_kernel_ver}

%postun -n kernel-net-ipsec
%depmod %{_kernel_ver}

%post	-n kernel-smp-net-ipsec
%depmod %{_kernel_ver}

%postun -n kernel-smp-net-ipsec
%depmod %{_kernel_ver}

%files
%defattr(644,root,root,755)
%doc README CREDITS CHANGES BUGS
%doc doc/{kernel.notes,impl.notes,examples,prob.report,std} doc/*.html
%{?with_NAT:%doc NAT-Traversal-%{nat_tr_ver}/README.NAT-Traversal}
%{?with_x509:%doc CHANGES.x509 README.x509}
%{_mandir}/man*/*
%lang(pl) %{_mandir}/pl/man*/*
%attr(755,root,root) %{_sbindir}/*
%attr(754,root,root) /etc/rc.d/init.d/*
%dir %{_libdir}/ipsec
%attr(755,root,root) %{_libdir}/ipsec/*
%attr(751,root,root) %dir %{_sysconfdir}/ipsec
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/ipsec/ipsec.conf
%if %{with x509}
%attr(700,root,root) %dir %{_sysconfdir}/ipsec/ipsec.d
%attr(700,root,root) %dir %{_sysconfdir}/ipsec/ipsec.d/certs
%attr(700,root,root) %dir %{_sysconfdir}/ipsec/ipsec.d/crls
%attr(700,root,root) %dir %{_sysconfdir}/ipsec/ipsec.d/cacerts
%attr(700,root,root) %dir %{_sysconfdir}/ipsec/ipsec.d/private
%attr(700,root,root) %dir %{_sysconfdir}/ipsec/ipsec.d/policies
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/ipsec/ipsec.d/policies/*
%endif

%if %{with modules}
%files -n kernel-net-ipsec
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/ipsec*
%if %{with smp}
%files -n kernel-smp-net-ipsec
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/misc/ipsec*
%endif
%endif
