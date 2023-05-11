pyinstaller splitter.py --hidden-import=tiktoken_ext.openai_public --hidden-import=tiktoken_ext
REM --add-binary "dll\tls-client-64.dll;tls_client/dependencies"