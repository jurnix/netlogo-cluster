#!/bin/sh

VERSION="5.0.5"
NETLOGO="netlogo-5.0.5"
NETLOGO_TAR="$NETLOGO.tar.gz"

usage() { echo "Usage: $0 [-clean]" 1>&2; exit 1; }

clean() {
	echo "Cleaning directory"
	rm -rf $NETLOGO_TAR
	rm -rf $NETLOGO
	rm -rf netlogo
	rm -rf "extensions"
}

while getopts ":c:h" opt; do
    case "$opt" in
	c)
		clean
		exit 1
		;;
	*)
		usage
		;;
    esac
done


if [ ! -f /tmp/foo.txt ]; then
    echo "Downloading Netlogo 5.0.5..."
    wget https://ccl.northwestern.edu/netlogo/$VERSION/$NETLOGO_TAR > /dev/null
fi

echo "Untar netlogo..."
tar zxvf $NETLOGO_TAR > /dev/null

echo "Create soft link..."
ln -s $NETLOGO netlogo

echo "Move extensions to parent folder..."
mv netlogo/extensions .

echo "Install done"
echo "From now on, use setenv.sh at the start of any code session"
