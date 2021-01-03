
[ ! -d superlu ] && git clone https://github.com/xiaoyeli/superlu.git
cd superlu || exit
mkdir build ; cd build
cmake ..
make 
sudo make install
