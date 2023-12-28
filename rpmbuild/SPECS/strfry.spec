
%global version 0.9.6
Name:           strfry
Version:        %{version}
Release:        1
#Release:        1%{?dist}
Summary:        strfry relay service

License:        GPLv3
URL:            https://hoytech.com/
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  systemd
%{?fc38:BuildRequires: systemd-rpm-macros}
%{?fc39:BuildRequires: systemd-rpm-macros}
BuildRequires:  autogen
BuildRequires:  git
BuildRequires:  g++
BuildRequires:  make
BuildRequires:  rpm-build
BuildRequires:  pkg-config
BuildRequires:  libtool
BuildRequires:  ca-certificates
BuildRequires:  openssl-devel
BuildRequires:  libzstd-devel
BuildRequires:  lmdb-devel
BuildRequires:  zlib-devel
BuildRequires:  flatbuffers-devel
BuildRequires:  flatbuffers-compiler
BuildRequires:  perl-YAML
BuildRequires:  perl-Template-Toolkit
BuildRequires:  perl-Regexp-Grammars


%define debug_package %{nil}

%description
strfry is a relay for the nostr protocol
%define version_number  %{version}
%define releasever  %{release}
%global name strfry
%global __mangle_shebangs_exclude_from /usr/bin/env


%prep
# %setup -q -T -b 0
git clone -b fedora-pkg-build-test https://github.com/cosmicpsyop/strfry.git
#git clone https://github.com/cosmicpsyop/strfry.git

# XXX - remove when fixed
# build and manage secp256k1 with schnorrsig
git clone https://github.com/bitcoin-core/secp256k1.git
cd secp256k1
./autogen.sh
./configure --enable-module-schnorrsig
make
make install
mkdir -p %{buildroot}/usr/local/lib/
# make DESTDIR=%{buildroot} install
# rm -rf %{buildroot}/usr/local/inlcude
cd ..
# XXX - remove when fixed

%build
# build steps
cd strfry
git submodule update --init
make setup-golpe
make -j4

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc/
mkdir -p %{buildroot}/usr/bin/
mkdir -p %{buildroot}/var/lib/strfry/
mkdir -p %{buildroot}/usr/local/lib/
mkdir -p %{buildroot}/usr/lib/systemd/system/

install -m 755 -D strfry/strfry %{buildroot}%{_bindir}/%{name}
install -m 644 -D strfry/strfry.conf %{buildroot}%{_sysconfdir}/%{name}.conf
sed -i 's|./strfry-db/|/var/lib/strfry/|g' %{buildroot}%{_sysconfdir}/%{name}.conf
install -m 644 -D strfry/rpmbuild/strfry.service %{buildroot}%{_unitdir}/%{name}.service
 
%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%{_bindir}/%{name}
%{_sysconfdir}/%{name}.conf
%{_unitdir}/%{name}.service

# XXX - remove when fixed
/usr/local/lib/libsecp256k1.so.2
/usr/local/lib/libsecp256k1.so
/usr/local/lib/libsecp256k1.so.2.1.2
# XXX - remove when fixed


%ghost %{_localstatedir}/log/%{name}.log
%dir /var/lib/%{name}/

%pre

#systemctl stop strfry || true

if [ $1 == 2 ];then  
    if [[ ! -d /var/lib/strfry/backup ]]; then
	# make backup	
	:
    fi
fi


%post -p /bin/bash

#install

#upgrade

%systemd_post %{name}.service

if ! getent group strfry >/dev/null 2>&1; then
    addgroup --system --quiet strfry
fi
if ! getent passwd strfry >/dev/null 2>&1; then
    adduser --system --quiet --ingroup strfry		\
	    --no-create-home --home /nonexistent	\
	    strfry
fi

if [ $1 == 1 ] ; then
    chown strfry:strfry /etc/strfry.conf
    chown strfry:strfry /var/lib/strfry

    systemctl daemon-reload
    systemctl enable strfry.service
    systemctl start strfry || echo "strfry is not started"
fi

%preun


if [ $1 == 0 ]; then
   systemctl stop strfry
   systemctl disable strfry
fi

if [ $1 == 1 ]; then
   systemctl stop strfry
fi

#systemctl stop strfry || echo "strfry was not started"

%systemd_preun %{name}.service

%postun

%systemd_postun_with_restart %{name}.service

if [ $1 == 0 ]; then
    rm -rf /etc/strfry.conf
fi

if [ $1 == 0 ] && [ -d /run/systemd/system ] ; then
    systemctl --system daemon-reload >/dev/null || true
fi


#systemctl stop strfry || echo "strfry was not started"

%changelog
* Fri Sep 22 2023 Doug HoyTech <doug@hoytech.com> - 0.9.6-1
- Initial packaging
