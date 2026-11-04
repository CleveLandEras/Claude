#!/bin/bash
# 一条命令编出两个调试包：./build.sh
set -e
cd "$(dirname "$0")"
export JAVA_HOME="${JAVA_HOME:-$HOME/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home}"
export ANDROID_HOME="${ANDROID_HOME:-$HOME/Library/Android/sdk}"
GRADLE="${GRADLE:-$HOME/Library/Android/gradle-8.9/bin/gradle}"
"$GRADLE" -q assembleDebug "$@"
ls -1 relay/build/outputs/apk/debug/*.apk testapp/build/outputs/apk/debug/*.apk
