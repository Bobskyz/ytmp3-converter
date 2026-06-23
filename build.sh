#!/bin/bash
# build.sh

echo "📦 Mengunduh Node.js static binary..."
NODE_VERSION="20.12.0"
NODE_DIR="nodejs"
BIN_DIR="bin"

mkdir -p $NODE_DIR $BIN_DIR

curl -L "https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-x64.tar.xz" -o node.tar.xz
tar -xf node.tar.xz -C $NODE_DIR --strip-components=1
rm node.tar.xz

# Buat symlink ke ./bin agar mudah diakses
ln -sf ../$NODE_DIR/bin/node ./bin/node

# Jadikan executable
chmod +x ./bin/node
chmod +x $NODE_DIR/bin/node

echo "✅ Node.js installed to ./${NODE_DIR} dan ./bin/node"