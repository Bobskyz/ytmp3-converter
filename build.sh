#!/bin/bash
# build.sh
# Unduh ffmpeg static build untuk Linux
curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz -o ffmpeg.tar.xz
tar -xf ffmpeg.tar.xz
mv ffmpeg-*-static/ffmpeg ./ffmpeg
chmod +x ./ffmpeg