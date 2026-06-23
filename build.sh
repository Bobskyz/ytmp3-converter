#!/bin/bash
set -e  # Hentikan jika ada error

echo "📦 Mengunduh Node.js static binary..."
NODE_VERSION="20.12.0"
mkdir -p nodejs bin

# Unduh dan ekstrak
curl -L "https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-x64.tar.xz" -o node.tar.xz
tar -xf node.tar.xz -C nodejs --strip-components=1
rm node.tar.xz

# Buat symlink ke ./bin agar mudah diakses
ln -sf ../nodejs/bin/node ./bin/node
chmod +x ./bin/node

echo "✅ Node.js installed to ./nodejs dan ./bin/node"