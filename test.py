import qrcode

img = qrcode.make('event.message.text')
img_path = 'result.png'
img.save('./' + img_path)
