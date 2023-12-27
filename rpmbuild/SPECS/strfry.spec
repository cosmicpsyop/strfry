
%global version 0.9.6
Name:           strfry
Version:        %{version}
Release:        %{?PACKAGE_NUMBER}%{?dist}
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


%global commit b6e7e4f  # Use the specific commit or tag you want

# Consider pinning the version of libsecp256k1 by archive or commit
Source0: https://github.com/bitcoin-core/secp256k1/archive/%{commit}/secp256k1-%{commit}.tar.gz
# %prep
# %setup -q -n secp256k1-%{commit}

%prep
%setup -q -T -b 0

%build
# Clone secp256k1 repository
git clone https://github.com/bitcoin-core/secp256k1.git

# Build secp256k1
cd secp256k1
./autogen.sh
./configure --enable-module-schnorrsig
make
make install

# Continue with the rest of the build steps
git submodule update --init
make setup-golpe
make clean
make -j4

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc/
mkdir -p %{buildroot}/var/lib/strfry/
mkdir -p %{buildroot}/usr/local/lib/

install -m 755 -D strfry %{buildroot}%{_bindir}/%{name}
install -m 644 -D strfry.conf %{buildroot}%{_sysconfdir}/%{name}.conf
install -m 644 -D %{_builddir}/strfry.service %{buildroot}%{_unitdir}/%{name}.service
sed -i 's|./strfry-db/|/var/lib/strfry/|g' %{buildroot}%{_sysconfdir}/%{name}.conf
# Custom build can be removed when package includes
install -m 755 -D /usr/local/lib/libsecp256k1.a %{buildroot}/usr/local/lib/libsecp256k1.a
install -m 755 -D /usr/local/lib/libsecp256k1.la %{buildroot}/usr/local/lib/libsecp256k1.la
install -m 755 -D /usr/local/lib/libsecp256k1.so %{buildroot}/usr/local/lib/libsecp256k1.so
install -m 755 -D /usr/local/lib/libsecp256k1.so.2 %{buildroot}/usr/local/lib/libsecp256k1.so.2
install -m 755 -D /usr/local/lib/libsecp256k1.so.2.1.2 %{buildroot}/usr/local/lib/libsecp256k1.so.2.1.2

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%{_bindir}/%{name}
%{_sysconfdir}/%{name}.conf
%{_unitdir}/%{name}.service
/usr/local/lib/*


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
* Fri Sep 22 2023
- Initial packaging

