Summary:	Free IPSEC implemetation
Summary(pl):	Publicznie dost�pna implementacja IPSEC
Name:		freeswan
Version:	1.8
Release:	2
License:	GPL
Group:		Networking/Daemons
Group(cs):	S��ov�/D�moni
Group(da):	Netv�rks/D�moner
Group(de):	Netzwerkwesen/Server
Group(es):	Red/Servidores
Group(fr):	R�seau/Serveurs
Group(is):	Verkfr��i/P�kar
Group(it):	Rete/Demoni
Group(no):	Nettverks/Daemoner
Group(pl):	Sieciowe/Serwery
Group(pt):	Rede/Servidores
Group(ru):	�������/������
Group(sl):	Omre�ni/Stre�niki
Group(sv):	N�tverk/Demoner
Source0:	ftp://ftp.xs4all.nl/pub/crypto/freeswan/%{name}-%{version}.tar.gz
Source1:	http://www.mif.pg.gda.pl/homepages/ankry/man-PLD/%{name}-pl-man-pages.tar.bz2
Patch0:		%{name}-Makefiles.patch
Patch1:		%{name}-manlink.patch
Patch2:		%{name}-config.patch
Patch3:		%{name}-init.patch
URL:		http://www.freeswan.org/
Prereq:		/sbin/chkconfig
Prereq:		rc-scripts
BuildRequires:	gmp-devel
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
The basic idea of IPSEC is to provide security functions
(authentication and encryption) at the IP (Internet Protocol) level.
It will be required in IP version 6 (better known as IPng, the next
generation) and is optional for the current IP, version 4.

FreeS/WAN is a freely-distributable implementation of IPSEC protocol.

%description -l pl
Podstawowa idea IPSEC to zapewnienie funkcji bezpiecze�stwa
(autentykacji i szyfrowania) na poziomie IP. B�dzie wymagany do IP w
wersji 6 (znanego tak�e jako IPng, IP nast�pnej generacji) i jest
opcjonalny dla aktualnego IP, w wersji 4.

FreeS/WAN jest darmow� implementacj� protoko�u IPSEC.

%prep
%setup  -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1

%build
OPT_FLAGS="%{rpmcflags}"; export OPT_FLAGS
%{__make} programs

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir}/freeswan,/etc/rc.d/init.d,/var/run/pluto}

%{__make} install \
	DESTDIR="$RPM_BUILD_ROOT" 

bzip2 -dc %{SOURCE1} | tar xf - -C $RPM_BUILD_ROOT%{_mandir}

gzip -9nf README CREDITS CHANGES BUGS \
          doc/{kernel.notes,impl.notes,examples,prob.report,standards}

%clean
rm -rf $RPM_BUILD_ROOT

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

%files
%defattr(644,root,root,755)
%doc *.gz doc/*.gz doc/*.html
%{_mandir}/man*/*
%lang(pl) %{_mandir}/pl/man*/*
%attr(755,root,root) %{_sbindir}/*
%attr(754,root,root) /etc/rc.d/init.d/*
%dir %{_libdir}/ipsec
%attr(755,root,root) %{_libdir}/ipsec/*
%attr(751,root,root) %dir %{_sysconfdir}/freeswan
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/freeswan/*
