#!/bin/sh

[ ! -d arpack-ng ] && git clone https://github.com/opencollab/arpack-ng.git
cd arpack-ng || exit
sh bootstrap
./configure
make
make check
make install

