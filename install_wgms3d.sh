
[ ! -d wgms3d ] && git clone https://github.com/mabl/wgms3d.git
cd wgms3d || exit
./configure 
make 
make install

