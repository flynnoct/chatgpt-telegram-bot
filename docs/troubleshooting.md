# Troubleshooting

This page is for recording the issues we met during development.

## Azure TTS installation

See https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/quickstarts/setup-platform?pivots=programming-language-python&tabs=linux.

However, if you are using Ubuntu 22.04, you will need to manually install `libssl1.1`:

```
wget http://security.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1f-1ubuntu2_amd64.deb && apt install ./libssl1.1_1.1.1f-1ubuntu2_amd64.deb
```