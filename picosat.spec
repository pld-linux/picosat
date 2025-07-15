Summary:	A SAT solver
Name:		picosat
Version:	965
Release:	1
License:	MIT
Group:		Applications
Source0:	http://fmv.jku.at/picosat/%{name}-%{version}.tar.gz
# Source0-md5:	d37c236d5c60b03d888d137c2fa4285f
Source1:	%{name}.1
Source2:	%{name}.trace.1
Source3:	picomus.1
Patch0:		%{name}-trace.patch
URL:		http://fmv.jku.at/picosat/
BuildRequires:	R
Requires:	%{name}-libs = %{version}-%{release}
Requires:	bzip2
Requires:	gzip
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
PicoSAT solves the SAT problem, which is the classical NP complete
problem of searching for a satisfying assignment of a propositional
formula in conjunctive normal form (CNF). PicoSAT can generate proofs
and cores in memory by compressing the proof trace. It supports the
proof format of TraceCheck.

%package -n R-picosat
Summary:	A SAT solver library for R
Group:		Libraries

%description -n R-picosat
The PicoSAT library, which contains routines that solve the SAT
problem. The library has a simple API which is similar to that of
previous solvers by the same authors.

This version of the library is built for use with R projects.

%package libs
Summary:	A SAT solver library
Group:		Libraries

%description libs
The PicoSAT library, which contains routines that solve the SAT
problem. The library has a simple API which is similar to that of
previous solvers by the same authors.

%package devel
Summary:	Development files for PicoSAT
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}
Requires:	R-%{name} = %{version}-%{release}

%description devel
Headers and other development files for PicoSAT.

%prep
%setup -q
%patch -P0

%build
# The configure script is NOT autoconf-generated and chooses its own CFLAGS,
# so we mimic its effects instead of using it.

# Build the version with R support
sed -e "s/@CC@/gcc/" \
	-e "s|@CFLAGS@|$RPM_OPT_FLAGS -D_GNU_SOURCE=1 -DNDEBUG -DRCODE -I%{_includedir}/R|" \
	-e "s|-Xlinker libpicosat.so|-Xlinker libpicosat.so.0 $RPM_LD_FLAGS -L%{_libdir}/R/lib -lR|" \
	-e "s/libpicosat/libpicosat-R/g" \
	-e "s/-lpicosat/-lpicosat-R/g" \
	-e "s/@TARGETS@/libpicosat-R.so/" \
  makefile.in > makefile
%{__make}

# Build the version with trace support
sed -e "s/@CC@/gcc/" \
	-e "s|@CFLAGS@|$RPM_OPT_FLAGS -D_GNU_SOURCE=1 -DNDEBUG -DTRACE|" \
	-e "s|-Xlinker libpicosat.so|-Xlinker libpicosat.so.0 $RPM_LD_FLAGS|" \
	-e "s/libpicosat/libpicosat-trace/g" \
	-e "s/-lpicosat/-lpicosat-trace/g" \
	-e "s/@TARGETS@/libpicosat-trace.so picosat picomus/" \
  makefile.in > makefile
%{__make}
mv picosat picosat.trace

# Build the fast version.
# Note that picomus needs trace support, so we don't rebuild it.
rm -f *.o *.s config.h
sed -e "s/@CC@/gcc/" \
	-e "s|@CFLAGS@|$RPM_OPT_FLAGS -D_GNU_SOURCE=1 -DNDEBUG|" \
	-e "s|-Xlinker libpicosat.so|-Xlinker libpicosat.so.0 $RPM_LD_FLAGS|" \
	-e "s/@TARGETS@/libpicosat.so picosat picomcs picogcnf/" \
  makefile.in > makefile
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
# Install the header file
install -d $RPM_BUILD_ROOT%{_includedir}
cp -p picosat.h $RPM_BUILD_ROOT%{_includedir}

# Install the libraries
install -d $RPM_BUILD_ROOT%{_libdir}
install -p libpicosat-R.so \
  $RPM_BUILD_ROOT%{_libdir}/libpicosat-R.so.0.0.%{version}
ln -s libpicosat-R.so.0.0.%{version} $RPM_BUILD_ROOT%{_libdir}/libpicosat-R.so.0
ln -s libpicosat-R.so.0 $RPM_BUILD_ROOT%{_libdir}/libpicosat-R.so
install -p libpicosat-trace.so \
  $RPM_BUILD_ROOT%{_libdir}/libpicosat-trace.so.0.0.%{version}
ln -s libpicosat-trace.so.0.0.%{version} $RPM_BUILD_ROOT%{_libdir}/libpicosat-trace.so.0
ln -s libpicosat-trace.so.0 $RPM_BUILD_ROOT%{_libdir}/libpicosat-trace.so
install -p libpicosat.so \
  $RPM_BUILD_ROOT%{_libdir}/libpicosat.so.0.0.%{version}
ln -s libpicosat.so.0.0.%{version} $RPM_BUILD_ROOT%{_libdir}/libpicosat.so.0
ln -s libpicosat.so.0 $RPM_BUILD_ROOT%{_libdir}/libpicosat.so

# Install the binaries
install -d $RPM_BUILD_ROOT%{_bindir}
install -p picosat picosat.trace picomus picomcs picogcnf \
  $RPM_BUILD_ROOT%{_bindir}

# Install the man pages
install -d $RPM_BUILD_ROOT%{_mandir}/man1
cp -p %{SOURCE1} %{SOURCE2} %{SOURCE3} $RPM_BUILD_ROOT%{_mandir}/man1

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%post	-n R-picosat -p /sbin/ldconfig
%postun	-n R-picosat -p /sbin/ldconfig

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/picogcnf
%attr(755,root,root) %{_bindir}/picomcs
%attr(755,root,root) %{_bindir}/picomus
%attr(755,root,root) %{_bindir}/picosat
%attr(755,root,root) %{_bindir}/picosat.trace
%{_mandir}/man1/picomus.1*
%{_mandir}/man1/picosat.1*
%{_mandir}/man1/picosat.trace.1

%files libs
%defattr(644,root,root,755)
%doc NEWS LICENSE
%ghost %{_libdir}/libpicosat.so.0
%attr(755,root,root) %{_libdir}/libpicosat.so.*.*.*
%ghost %{_libdir}/libpicosat-trace.so.0
%attr(755,root,root) %{_libdir}/libpicosat-trace.so.*.*.*

%files devel
%defattr(644,root,root,755)
%{_includedir}/picosat.h
%{_libdir}/libpicosat.so
%{_libdir}/libpicosat-trace.so
%{_libdir}/libpicosat-R.so

%files -n R-picosat
%defattr(644,root,root,755)
%doc NEWS LICENSE
%attr(755,root,root) %{_libdir}/libpicosat-R.so.*.*.*
%ghost %{_libdir}/libpicosat-R.so.0
