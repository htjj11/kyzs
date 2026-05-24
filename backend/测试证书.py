import ssl

ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ctx.load_cert_chain(
    certfile='cert_2.pem',              # 改用服务器证书，不用完整链
    keyfile='10.68.202.238_RSA.key'
)