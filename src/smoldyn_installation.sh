sudo wget http://www.smoldyn.org/smoldyn-2.61.tgz
sudo tar xzvf smoldyn-2.61.tgz
sudo yum install freeglut-devel
sudo yum install libtiff
sudo yum groupinstall "Development Tools"
sudo yum install cmake
cd smoldyn-2.61/cmake
sudo cmake .. -DOPTION_USE_LIBTIFF=OFF -DOPTION_USE_OPENGL=OFF
sudo make
sudo make install