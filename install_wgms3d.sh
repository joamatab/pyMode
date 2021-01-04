
[ ! -d wgms3d ] && git clone https://github.com/mabl/wgms3d.git
cd wgms3d || exit
./configure --with-arpack --with-superlu
make 
sudo make install

