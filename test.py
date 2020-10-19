import qrcode

img = qrcode.make('line-qrcode-gen')
img.save('./logo.png')