#!/bin/sh

python install.py
[ ! -d wgms3d ] && git clone https://github.com/mabl/wgms3d.git
cd wgms3d || exit
CPPFLAGS="-O3 -march=native"
./configure --with-mpi --with-petsc --with-slepc
make 
make install

