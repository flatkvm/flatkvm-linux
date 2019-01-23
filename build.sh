#!/bin/sh

if [ ! -e "SOURCES/linux-4.14.67.tar.xz" ]; then
	curl -L -o SOURCES/linux-4.14.67.tar.xz https://cdn.kernel.org/pub/linux/kernel/v4.x/linux-4.14.67.tar.xz
fi

rpmbuild --define "_topdir $(pwd)" -ba SPECS/flatkvm-linux.spec
