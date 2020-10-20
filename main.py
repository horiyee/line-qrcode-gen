import glob
import os
import zipfile

import qrcode
from flask import Flask, abort, request, send_file
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (ImageSendMessage, MessageEvent, TextMessage,
                            TextSendMessage)

app = Flask(__name__)

# 環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

YOUR_APP_URL = 'https://line-qrcode-gen.herokuapp.com/'

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)


@app.route("/")
def index():
    return 'LINE QR Code Generator by horri1520'


@app.route("/show_imgs")
def show_images():
    images = glob.glob('static/images/*.png')
    images.sort()
    result = ''
    for image in images:
        result += YOUR_APP_URL + image + '\n'
    return '{} images detected.\n{}'.format(len(images), result)


@app.route("/delete_imgs")
def delete_images():
    images = glob.glob('static/images/*.png')
    for image in images:
        os.remove(image)
    return '{} images deleted.'.format(len(images))


@app.route("/download_imgs")
def download_images():
    images = glob.glob('static/images/*.png')
    zip_name = 'generated_qrcodes'
    zip_path = 'static/{}.zip'.format(zip_name)
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_STORED) as new_zip:
        for image in images:
            img_name = image.split('/')
            img_name = img_name[2]
            new_zip.write(image, arcname='{}/{}'.format(zip_name, img_name))
    return send_file(zip_path)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = event.message.text
    message_id = event.message.id
    try:
        img = qrcode.make(message)
        img_path = 'static/images/{}.png'.format(message_id)
        img.save(img_path)
        img_url = YOUR_APP_URL + img_path
        line_bot_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(
                    text='"{}" をQRコードに変換しました！'.format(message)
                ),
                ImageSendMessage(
                    original_content_url=img_url,
                    preview_image_url=img_url,
                )
            ]
        )
    except Exception as error:
        line_bot_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(text='エラーが発生しました。。。'),
                TextSendMessage(text='送った文章が長い場合は短くしてね！もしエラーが頻発する場合は、もっと別な文章を送ってみてね！'),
            ]
        )


if __name__ == "__main__":
    #    app.run()
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)
