#
# This is a variant of kata's configuration for the Linux kernel,
# adding support for virtio-vga and ac97.
#

Name:           flatkvm-linux
Version:        4.14.67.1
Release:        1
License:        GPL-2.0
Summary:        The Linux kernel optimized for flatkvm
Group:          System/Kernel
Url:            http://www.kernel.org/
Source0:        https://cdn.kernel.org/pub/linux/kernel/v4.x/linux-4.14.67.tar.xz
Source1:        x86_64-flatkvm-config

%define kversion %{version}-%{release}.flatkvm

BuildRequires:  bash >= 2.03
BuildRequires:  bc
BuildRequires:  binutils-devel

%if 0%{?rhel_version}
BuildRequires:  elfutils-devel
%endif

%if 0%{?suse_version}
BuildRequires:  libelf-devel
BuildRequires: fdupes
%endif

%if 0%{?fedora} || 0%{?centos_version}
BuildRequires:  pkgconfig(libelf)
%endif

BuildRequires:  make >= 3.78
BuildRequires:  openssl-devel
BuildRequires:  flex
BuildRequires:  bison

# don't strip .ko files!
%global __os_install_post %{nil}
%define debug_package %{nil}
%define __strip /bin/true

# Patches

%description
The Linux kernel.

%package debug
Summary: Debug components for the %{name} package
Group:   System/Kernel

%description debug
Debug components for the flatkvm-linux package.
This package includes the kernel config and the kernel map.

%prep
%setup -q -n linux-4.14.67
#%setup -q -T -D -n linux-4.14.67 -a 1

# Patches

%build

BuildKernel() {
    local kernelArch="x86_64"
    ExtraVer="-%{release}.flatkvm"

    perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = ${ExtraVer}/" Makefile

    make -s mrproper

    # Runtime .config selection based on kernelArch
    rm -f .config
    cp $RPM_SOURCE_DIR/x86_64-flatkvm-config .config

    %if 0%{?fedora}
    #Fedora uses gcc 8, build is failing due to warnings.
    export CFLAGS="-Wno-error=restrict"
    export EXTRA_CFLAGS="-Wno-format-truncation -Wno-cast-function-type -Wno-error=restrict -Wno-error"
    %endif

    make -s ARCH=$kernelArch oldconfig > /dev/null
    make -s CONFIG_DEBUG_SECTION_MISMATCH=y %{?_smp_mflags} ARCH=$kernelArch %{?sparse_mflags} || exit 1
}

BuildKernel

%install

InstallKernel() {
    compressedImage="arch/x86_64/boot/bzImage"
    rawImage="vmlinux"
    KernelVer=%{kversion}
    KernelDir=%{buildroot}/usr/share/flatkvm

    mkdir   -p ${KernelDir}

    if [ -n "$compressedImage" ]; then
        cp "$compressedImage" ${KernelDir}/vmlinuz-$KernelVer
        chmod 755 ${KernelDir}/vmlinuz-$KernelVer
        ln -sf vmlinuz-$KernelVer ${KernelDir}/vmlinuz.flatkvm
    fi

    cp $rawImage ${KernelDir}/vmlinux-$KernelVer
    chmod 755 ${KernelDir}/vmlinux-$KernelVer
    ln -sf vmlinux-$KernelVer ${KernelDir}/vmlinux.flatkvm

    cp .config "${KernelDir}/config-${KernelVer}"
    cp System.map "${KernelDir}/System.map-${KernelVer}"

    rm -f %{buildroot}/usr/lib/modules/$KernelVer/build
    rm -f %{buildroot}/usr/lib/modules/$KernelVer/source
}

InstallKernel

rm -rf %{buildroot}/usr/lib/firmware

%if 0%{?suse_version}
%fdupes -s %{buildroot}
%endif

%files
%dir /usr/share/flatkvm
/usr/share/flatkvm/vmlinux-%{kversion}
/usr/share/flatkvm/vmlinux.flatkvm

%ifnarch ppc64le
/usr/share/flatkvm/vmlinuz-%{kversion}
/usr/share/flatkvm/vmlinuz.flatkvm
%endif

%files debug
%defattr(-,root,root,-)
/usr/share/flatkvm/config-%{kversion}
/usr/share/flatkvm/System.map-%{kversion}
