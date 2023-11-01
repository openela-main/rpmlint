%if 0%{?fedora} || 0%{?rhel} > 7
%bcond_without python3
%else
%bcond_with python3
%endif

%if %{with python3}
%global python %{__python3}
%global pytest %(ls -1 %{_bindir}/py.test-3* | tail -n 1)
# The flake8 packages will be removed from non-modular RHEL
#global flake8 python3-flake8
%global flake8 true
%else
%global python %{__python}
%global pytest py.test
%global flake8 flake8
%endif

Name:           rpmlint
Version:        1.10
Release:        14%{?dist}
Summary:        Tool for checking common errors in RPM packages
Group:          Development/Tools
License:        GPLv2
URL:            https://github.com/rpm-software-management/rpmlint
Source0:        https://github.com/rpm-software-management/rpmlint/archive/rpmlint-%{version}.tar.gz
Source1:        %{name}.config
Source3:        %{name}-etc.config
# EL-4 specific config
Source4:        %{name}.config.el4
# EL-5 specific config
Source5:        %{name}.config.el5
# https://github.com/rpm-software-management/rpmlint/commit/e739876
Patch0:         rpmlint-1.10-ignore-debuginfo-useless-provides.patch
# https://github.com/rpm-software-management/rpmlint/commit/b748e6fadb8e68df2aa679ccf62822ad56577b80
# https://github.com/rpm-software-management/rpmlint/commit/c1945e37e2989364c5caedc05aa429a5c2d39f4d
# https://github.com/rpm-software-management/rpmlint/commit/f267bf1c60d067436b360c68d8e956876758b268
Patch1:		rpmlint-1.10-flake-cleanups.patch
Patch2:		rpmlint-1.10-no_python2.patch
Patch3:		rpmlint-1.10-fix_test.patch
Patch4:		rpmlint-1.10-rpm_surrogate_escaped_utf8.patch
Patch5:		rpmlint-1.10-update-crypto-example.patch
BuildArch:      noarch
%if %{with python3}
%if 0%{?rhel} > 7
BuildRequires:  python3-devel
BuildRequires:  rpm-python3 >= 4.4.2.2
%else
BuildRequires:  python3-devel
BuildRequires:  rpm-python3 >= 4.4.2.2
%endif
BuildRequires:  python3-pytest
#BuildRequires:  python3-flake8-import-order
%{?__python3:Requires: %{__python3}}
Requires:       rpm-python3 >= 4.4.2.2
%else
BuildRequires:  python >= 2.6
BuildRequires:  rpm-python >= 4.4.2.2
BuildRequires:  pytest
#BuildRequires:  python2-flake8-import-order
Requires:       python >= 2.6
Requires:       rpm-python >= 4.4.2.2
%endif
BuildRequires:  sed >= 3.95
BuildRequires:  bash-completion
Requires:       perl-interpreter
%if ! 0%{?rhel}
# python-magic and python-enchant are actually optional dependencies, but
# they bring quite desirable features.  They're not available in RHEL/EPEL 5
# as of 2010-06-23 though.
%if %{with python3}
Requires:       python3-magic
Requires:       python3-enchant
%else
Requires:       python-magic
Requires:       python-enchant
%endif
%endif
Requires:       cpio
Requires:       binutils
Requires:       desktop-file-utils
Requires:       gzip
Requires:       bzip2
Requires:       xz
# Needed for man page check in FilesCheck.py
Requires:       %{_bindir}/groff

%description
rpmlint is a tool for checking common errors in RPM packages.  Binary
and source packages as well as spec files can be checked.


%prep
%setup -q -n %{name}-%{name}-%{version}
%patch0 -p1 -b .debuginfo-useless-provides
%patch1 -p1 -b .flake
%patch2 -p1 -b .no_python2
%patch3 -p1 -b .fix_test
%patch4 -p1 -b .rpm_surrogate_escaped_utf8
%patch5 -p1 -b .update_crypto_example
sed -i -e /MenuCheck/d Config.py
cp -p config config.example
install -pm 644 %{SOURCE3} config


%build
make COMPILE_PYC=1 PYTHON=%{python}


%install
touch rpmlint.pyc rpmlint.pyo # just for the %%exclude to work everywhere
make install DESTDIR=$RPM_BUILD_ROOT ETCDIR=%{_sysconfdir} MANDIR=%{_mandir} \
  LIBDIR=%{_datadir}/rpmlint BINDIR=%{_bindir} PYTHON=%{python}
install -pm 644 %{SOURCE1} $RPM_BUILD_ROOT%{_datadir}/rpmlint/config

install -pm 644 %{SOURCE4} $RPM_BUILD_ROOT%{_datadir}/rpmlint/config.el4
install -pm 644 %{SOURCE5} $RPM_BUILD_ROOT%{_datadir}/rpmlint/config.el5
pushd $RPM_BUILD_ROOT%{_bindir}
ln -s rpmlint el4-rpmlint
ln -s rpmlint el5-rpmlint
popd
rm -rf %{buildroot}%{_sysconfdir}/bash_completion.d/


%check
make check PYTHON=%{python} PYTEST=%{pytest} FLAKE8=%{flake8}


%files
%license COPYING
%doc README.md config.example
%config(noreplace) %{_sysconfdir}/rpmlint/
%{_datadir}/bash-completion/completions/
%{_bindir}/rpmdiff
%{_bindir}/el*-rpmlint
%{_bindir}/rpmlint
%{_datadir}/rpmlint/
%{_mandir}/man1/rpmdiff.1*
%{_mandir}/man1/rpmlint.1*

%changelog
* Thu Jun 04 2020 Michal Domonkos <mdomonko@redhat.com> - 1.10-14
- Update crypto warnings in config file to reflect current Fedora policy
  (RHBZ#1797545)

* Fri Jun 14 2019 Thomas Woerner <twoerner@redhat.com> - 1.10.13.2
- Handle rpm change to return surrogate-escaped utf-8 python strings
  (RHBZ#1693712)

* Thu Jun 13 2019 Thomas Woerner <twoerner@redhat.com> - 1.10.13.1
- Fix unit test: use platform-python, py.test-3, no flake8 (RHBZ#1576803)
- Update of ValidShells (RHBZ#1633698)
- Remove Python2 paths from TagsCheck.py (RHBZ#1633698)
- Enable bash-competion scripts (RHBZ#1577890)

* Thu Sep 20 2018 Tomas Orsava <torsava@redhat.com> - 1.10-13
- Require the Python interpreter directly instead of using the package name
- Related: rhbz#1619153

* Mon Jun 25 2018 Petr Viktorin <pviktori@redhat.com> - 1.10-12
- Remove the flake8 build dependency

* Tue Apr 17 2018 Tom Callaway <spot@fedoraproject.org> - 1.10-11
- disable library-without-ldconfig-postin/postun checks (F28+)

* Tue Apr 17 2018 Tom Callaway <spot@fedoraproject.org> - 1.10-10
- fix flake errors (merge upstream changes)

* Mon Apr 16 2018 Todd Zullinger <tmz@pobox.com> - 1.10-9
- Update UsrLibBinaryException config to include .build-id
- Ignore useless-provides on debuginfo provides (bz1489096)

* Sun Mar 04 2018 Till Maas <opensource@till.name> - 1.10-8
- Update URL (RH #1547150)

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.10-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Mon Jan 15 2018 Karsten Hopp <karsten@redhat.com> - 1.10-6
- fix python3 conditional

* Sun Oct 29 2017 Tom Callaway <spot@fedoraproject.org> - 1.10-5
- ignore common jargon words in spellcheck

* Sun Oct 29 2017 Tom Callaway <spot@fedoraproject.org> - 1.10-4
- fix SSL_CTX_set_cipher_list waiver
- use raw strings in config file to silence python3 deprecation warnings

* Mon Sep 11 2017 Tom Callaway <spot@fedoraproject.org> - 1.10-3
- use correct config file option for debugsource

* Fri Sep  8 2017 Tom Callaway <spot@fedoraproject.org> - 1.10-2
- update config file to reflect new licenses and to ignore devel files in debugsource packages

* Tue Sep  5 2017 Tom Callaway <spot@fedoraproject.org> - 1.10-1
- update to 1.10

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.9-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Mon Jul 17 2017 Tom Callaway <spot@fedoraproject.org> - 1.9-11
- apply upstream fix for buildid

* Thu Jul 13 2017 Petr Pisar <ppisar@redhat.com> - 1.9-10
- perl dependency renamed to perl-interpreter
  <https://fedoraproject.org/wiki/Changes/perl_Package_to_Install_Core_Modules>

* Fri Apr 07 2017 Björn Esser <besser82@fedoraproject.org> - 1.9-9
- Upstream fix for str object has no attribute decode (bz1439941)

* Thu Mar 9 2017 Charalampos Stratakis <cstratak@redhat.com> - 1.9-8
- Update Python 3.5.3 magic bytecode value

* Wed Feb  8 2017 Tom Callaway <spot@fedoraproject.org> - 1.9-7
- apply upstream fix to not demand versioned filename Provides/Obsoletes

* Thu Dec 29 2016 Adam Williamson <awilliam@redhat.com> - 1.9-6
- Update Python 3.6 magic bytecode value (github PR #7)

* Tue Dec 13 2016 Charalampos Stratakis <cstratak@redhat.com> - 1.9-5
- Rebuild for Python 3.6

* Mon Oct 24 2016 Orion Poplawski <orion@cora.nwra.com> - 1.9-4
- Use %%license
- BR python-flake8-import-order for tests

* Fri Aug 26 2016 Tom Callaway <spot@fedoraproject.org> - 1.9-3
- ignore long description lines for debuginfo packages

* Mon Jul 25 2016 Tom Callaway <spot@fedoraproject.org> - 1.9-2
- fix 403 ignore rule for github to be more complete (bz1359582)

* Wed Jul  6 2016 Tom Callaway <spot@fedoraproject.org> - 1.9-1
- update to 1.9

* Tue Jun 14 2016 Tom Callaway <spot@fedoraproject.org> - 1.8-7
- ignore explicit-lib-dependency on python subpackages with "lib"
- update license list

* Mon Apr 18 2016 Tom Callaway <spot@fedoraproject.org> - 1.8-6
- update license list
- add github.com to the filter ignore list for 403 errors (bz1326855)

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.8-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Nov 10 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.8-3
- Rebuilt for https://fedoraproject.org/wiki/Changes/python3.5

* Mon Sep 28 2015 Tom Callaway <spot@fedoraproject.org> - 1.8-2
- fix issue in config regex causing bitbucket URLs to slip through invalid-url filter

* Fri Sep 25 2015 Tom Callaway <spot@fedoraproject.org> - 1.8-1
- 1.8
- add bad crypto warning to config file
- update license list

* Fri Jul 10 2015 Tom Callaway <spot@fedoraproject.org> - 1.7-1
- 1.7
- add python conditionals

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Fri May 29 2015 Tom Callaway <spot@fedoraproject.org> - 1.6-3
- filter out failure from broken webservers
- add new licenses

* Tue Dec  9 2014 Tom Callaway <spot@fedoraproject.org> - 1.6-2
- update license list in config file

* Thu Sep  4 2014 Tom Callaway <spot@fedoraproject.org> - 1.6-1
- update to 1.6

* Wed Jun 25 2014 Tom Callaway <spot@fedoraproject.org> - 1.5-12
- add systemd to UsrLibBinaryException

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu May 29 2014 Tom Callaway <spot@fedoraproject.org> - 1.5-10
- fix python 3.4 magic number (#1102846)

* Mon May 12 2014 Tom Callaway <spot@fedoraproject.org> - 1.5-9
- update config to ignore non-readable /etc/ovirt-engine/isouploader.conf

* Mon Feb 10 2014 Tom Callaway <spot@fedoraproject.org> - 1.5-8
- filter out broken-syntax-in-scriptlet-requires (except on el4/5)
- update license list

* Sun Feb  9 2014 Ville Skyttä <ville.skytta@iki.fi> - 1.5-7
- Make default config Python 3 compatible.

* Thu Dec 12 2013 Tom Callaway <spot@fedoraproject.org> - 1.5-6
- fix unicode naming bug (bz 1036310)

* Mon Nov 11 2013 Tom Callaway <spot@fedoraproject.org> - 1.5-5
- do not modify sys.argv[0] (bz 1026333)
- fix unbound var in MenuXDGCheck.py (bz 1026328)

* Wed Oct  9 2013 Tom Callaway <spot@fedoraproject.org> - 1.5-4
- Fix handling of Exec= with an absolute path (bz991278)
- Update license list, add AGPLv3+ (bz894187)

* Tue Aug  6 2013 Thomas Woerner <twoerner@redhat.com> - 1.5-3
- Fixed URL and Source0, now using sourceforge.net

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Fri May 17 2013 Tom Callaway <spot@fedoraproject.org> - 1.5-1
- update to 1.5

* Mon Apr  1 2013 Tom Callaway <spot@fedoraproject.org> - 1.4-14
- explicitly Require: perl (bz919865)
- fix lua binary detection (bz919869)

* Wed Mar  6 2013 Tom Callaway <spot@fedoraproject.org> - 1.4-13
- update license list
- exclude non-config files that live in /etc

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Tue Nov  6 2012 Tom Callaway <spot@fedoraproject.org> - 1.4-11
- add Requires: %%{_bindir}/groff for man page checks (bz 873448)

* Thu Sep  6 2012 Tom Callaway <spot@fedoraproject.org> - 1.4-10
- fix handling of ruby RI files as text files (they are binary files)
- apply upstream fix for macro regexp

* Tue Sep  4 2012 Thomas Woerner <twoerner@redhat.com> - 1.4-9
- fix build for RHEL: no bash-completion

* Tue Aug 14 2012 Tom Callaway <spot@fedoraproject.org> - 1.4-8
- add magic number fix for python 3 (bz845972)
- update license list

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Mon Jan 23 2012 Toshio Kuratomi <toshio@fedoraproject.org> - 1.4-6
-  Patch to fix messages that contain unicode summaries
   https://bugzilla.redhat.com/show_bug.cgi?id=783912

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Thu Dec 15 2011 Tom Callaway <spot@fedoraproject.org> - 1.4-4
- Do not throw an error on .desktop files set +x. (bz 767978)

* Mon Dec  5 2011 Tom Callaway <spot@fedoraproject.org> - 1.4-3
- own %%{_datadir}/bash-completion/ (thanks Ville Skyttä)

* Mon Dec  5 2011 Tom Callaway <spot@fedoraproject.org> - 1.4-2
- add BR: bash-completion for the pc file

* Mon Dec  5 2011 Tom Callaway <spot@fedoraproject.org> - 1.4-1
- update to 1.4

* Wed Oct 12 2011 Tom Callaway <spot@fedoraproject.org> - 1.3-2
- apply upstream fix for false error on checking ghosted man pages for 
  encoding (bz745446)
- update config to reflect new licenses (bz741298)

* Tue Jul 12 2011 Tom Callaway <spot@fedoraproject.org> - 1.3-1
- update to 1.3

* Sun Apr 24 2011 Tom Callaway <spot@fedoraproject.org> - 1.2-1
- update to 1.2
- filter away files-attr-not-set for all targets except EL-4 (bz694579)

* Thu Mar  3 2011 Tom Callaway <spot@fedoraproject.org> - 1.1-3
- apply upstream fix for source url aborts (bz 680781)

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Fri Feb  4 2011 Tom Callaway <spot@fedoraproject.org> - 1.1-1
- update to 1.1

* Tue Dec  7 2010 Tom "spot" Callaway <tcallawa@redhat.com> - 1.0-3
- fix typo in changelog
- %% comment out item in changelog
- simplify el4/el5 config files (thanks to Ville Skyttä)

* Mon Dec  6 2010 Tom "spot" Callaway <tcallawa@redhat.com> - 1.0-2
- add support for el4-rpmlint, el5-rpmlint
- disable no-cleaning-of-buildroot checks for Fedora
- disable no-buildroot-tag check for Fedora
- disable no-%%clean-section check for Fedora

* Mon Nov  1 2010 Ville Skyttä <ville.skytta@iki.fi> - 1.0-1
- Update to 1.0; fixes #637956, and #639823.
- Sync Fedora license list with Wiki revision 1.85.
- Whitelist more expectedly setuid executables; fixes #646455.

* Thu Aug 19 2010 Ville Skyttä <ville.skytta@iki.fi> - 0.99-1
- Update to 0.99; fixes #623607, helps work around #537430.
- Sync Fedora license list with Wiki revision 1.80.

* Wed Aug 11 2010 David Malcolm <dmalcolm@redhat.com> - 0.98-2
- recompiling .py files against Python 2.7 (rhbz#623355)

* Wed Jun 23 2010 Ville Skyttä <ville.skytta@iki.fi> - 0.98-1
- Update to 0.98; fixes #599427 and #599516.
- Filter out all lib*-java and lib*-python explicit-lib-dependency messages.
- Sync Fedora license list with Wiki revision 1.75; fixes #600317.

* Tue May 18 2010 Ville Skyttä <ville.skytta@iki.fi> - 0.97-1
- Update to 0.97; fixes #459452, #589432.
- Filter out explicit-lib-dep messages for libvirt(-python) (Dan Kenigsberg).
- Sync Fedora license list with Wiki revision 1.73.

* Thu Apr 22 2010 Ville Skyttä <ville.skytta@iki.fi> - 0.96-1
- Update to 0.96; fixes #487974, #571375, #571386, #572090, #572097, #578390.
- Sync Fedora license list with Wiki revision 1.71.

* Sat Mar  6 2010 Ville Skyttä <ville.skytta@iki.fi> - 0.95-2
- Patch to fix non-coherent-filename regression for source packages.

* Wed Mar  3 2010 Ville Skyttä <ville.skytta@iki.fi> - 0.95-1
- Update to 0.95; fixes #564585, #567285, #568498, and #570086.

* Mon Feb  1 2010 Ville Skyttä <ville.skytta@iki.fi> - 0.94-1
- Update to 0.94; rpm >= 4.8.0 spec file check fix included upstream.
- Sync Fedora license list with Wiki revision 1.65 (#559156).

* Tue Jan 26 2010 Ville Skyttä <ville.skytta@iki.fi> - 0.93-2
- Apply upstream patch to fix spec file check with rpm >= 4.8.0.

* Mon Jan 25 2010 Ville Skyttä <ville.skytta@iki.fi> - 0.93-1
- Update to 0.93; fixes #531102 and #555284.
- Enable checks requiring network access in default config.
- Disallow kernel module packages in default config.
- Remove old X11R6 dirs from paths treated as system ones in default config.
- Sync Fedora license list with Wiki revision 1.64.
- Omit python-enchant and python-magic dependencies when built on EL.

* Mon Nov  2 2009 Ville Skyttä <ville.skytta@iki.fi> - 0.92-1
- Update to 0.92; fixes #528535, and #531102 (partially).
- Python byte compile patch applied/superseded upstream.
- Add <lua> to list of valid scriptlet shells.
- Sync Fedora license list with Wiki revision 1.53.

* Mon Sep 14 2009 Ville Skyttä <ville.skytta@iki.fi> - 0.91-1
- Update to 0.91; fixes #513811, #515185, #516492, #519694, and #521630.
- Add dependencies on gzip, bzip2, and xz.
- Sync Fedora license list with Wiki revision 1.49.
- Move pre-2008 %%changelog entries to CHANGES.package.old.

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.90-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Jun 29 2009 Ville Skyttä <ville.skytta@iki.fi> - 0.90-1
- 0.90; fixes #508683.

* Sun Jun 21 2009 Ville Skyttä <ville.skytta@iki.fi> - 0.89-1
- Update to 0.89; fixes #461610, #496735, #496737 (partially), #498107,
  #491188, and #506957.
- Sync Fedora license list with Wiki revision 1.44.
- Parse list of standard users and groups from the setup package's uidgid file.

* Thu Mar 19 2009 Ville Skyttä <ville.skytta@iki.fi> - 0.87-1
- 0.87; fixes #480664, #483196, #483199, #486748, #488146, #488930, #489118.
- Sync Fedora license list with Wiki revision 1.38.
- Configs patch included upstream.

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.85-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Tue Jan 20 2009 Ville Skyttä <ville.skytta@iki.fi>
- Sync Fedora license list with Wiki revision 1.34.
- Filter out filename-too-long-for-joliet and symlink-should-be-* warnings in
  default config.

* Mon Dec 01 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 0.85-3
- Rebuild for Python 2.6

* Thu Oct 30 2008 Ville Skyttä <ville.skytta@iki.fi> - 0.85-2
- Apply upstream patch to load all *config from /etc/rpmlint.

* Thu Oct 23 2008 Ville Skyttä <ville.skytta@iki.fi> - 0.85-1
- 0.85, fixes #355861, #450011, #455371, #456843, #461421, #461423, #461434.
- Mute some explicit-lib-dependency false positives (#458290).
- Sync Fedora license list with Wiki revision 1.19.
- Dist regex patch applied/superseded upstream.

* Fri Sep 12 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 0.84-3
- Sync Fedora license list with Wiki revision 1.09

* Sat Jul 26 2008 Ville Skyttä <ville.skytta@iki.fi> - 0.84-2
- 0.84, fixes #355861, #456304.
- Sync Fedora license list with Wiki revision "16:08, 18 July 2008".
- Rediff patches.

* Tue May 27 2008 Ville Skyttä <ville.skytta@iki.fi> - 0.83-1
- 0.83, fixes #237204, #428096, #430206, #433783, #434694, #444441.
- Fedora licensing patch applied upstream.
- Move pre-2007 changelog entries to CHANGES.package.old.
- Sync Fedora license list with Revision 0.88.

* Tue May 20 2008 Todd Zullinger <tmz@pobox.com> 
- Sync Fedora license list with Revision 0.83 (Wiki rev 131).

* Mon Mar  3 2008 Ville Skyttä <ville.skytta@iki.fi> - 0.82-3
- Sync Fedora license list with Revision 0.69 (Wiki rev 110) (#434690).
