#!/bin/bash
# build.sh - Mengunduh dan menyiapkan Node.js untuk Vercel

echo "📦 Downloading Node.js static binary..."
# Unduh Node.js untuk Linux x64 (Vercel menggunakan Linux)
NODE_VERSION="20.12.0"
NODE_DIR="nodejs"
NODE_BINARY_URL="https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-x64.tar.xz"

# Buat direktori untuk node
mkdir -p $NODE_DIR

# Unduh dan ekstrak
curl -L $NODE_BINARY_URL -o node.tar.xz
tar -xf node.tar.xz -C $NODE_DIR --strip-components=1

# Hapus file arsip
rm node.tar.xz

echo "✅ Node.js installed to ./${NODE_DIR}"