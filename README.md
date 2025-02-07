# heb-g2p

```console
wget https://github.com/thewh1teagle/espeak-ng-static/releases/download/v1.52/espeak-ng-static-macos-universal
wget https://github.com/thewh1teagle/espeak-ng-static/releases/download/v1.52/espeak-ng-data.tar.gz
tar xf espeak-ng-data.tar.gz
export ESPEAK_DATA_PATH=$(pwd)/espeak-ng-data
chmod +x espeak-ng-static-macos-universal
./espeak-ng-static-macos-universal -x "podʔkaʔsʔt"
```