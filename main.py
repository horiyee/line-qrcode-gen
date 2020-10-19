import glob
import os

import qrcode
from flask import Flask, abort, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (ImageSendMessage, MessageEvent, TextMessage,
                            TextSendMessage)

app = Flask(__name__)

# 環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)


@app.route("/")
def index():
    return 'LINE QR Code Generator by horri1520'


@app.route("/show_imgs")
def show_imaages():
    targets = glob.glob('static/images/*.png')
    return targets


@app.route("/delete_imgs")
def delete_images():
    targets = glob.glob('static/images/*.png')
    for image in targets:
        os.remove(image)
    return '{} images deleted.'.format(len(targets))


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
    message_id = event.message.id
    img = qrcode.make(event.message.text)
    img_path = 'static/images/{}.png'.format(message_id)
    img.save(img_path)
    img_url = 'https://line-qrcode-gen.herokuapp.com/{}'.format(img_path)
    line_bot_api.reply_message(
        event.reply_token,
        ImageSendMessage(
            original_content_url=img_url,
            preview_image_url=img_url,
        )
    )

    # # img_path = 'static/images/{}.png'.format(img_name)
    # img_path = Path('static/images/{}.png'.format(img_name))
    # img.save('./' + img_path)
    # img_url = 'https://line-qrcode-gen/herokuapp.com/{}'.format(img_path)
    # line_bot_api.reply_message(
    #     event.reply_token,
    #     ImageSendMessage(
    #         original_content_url=img_url,
    #         preview_image_url=img_url,
    #     )
    # )


if __name__ == "__main__":
    #    app.run()
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)
