import logging
import asyncio
import nest_asyncio

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

from dotenv import load_dotenv
import os

# .env 파일에서 환경 변수 로드
load_dotenv()

# 환경 변수 사용
botfather_token = os.getenv("BOTFATHER_TOKEN")

# 이미 실행 중인 이벤트 루프를 허용하도록 설정
nest_asyncio.apply()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 임시 변수
wallet_address = "0x7896Dfb8f8Ef9e36BA37ACB111AaE3D704dbc51Ed"
token_name = "gyuseon"
token_ticker = "GYU"
amount = 616

# 안내 문구
WELCOME_TEXT = """KeyBot에 오신걸 환영합니다 {username}!

{username}님의 간편한 거래를 위해 제가 지갑 주소를 생성했습니다.

<code>{wallet_address}</code>

─────────────────────
- /trading 기능을 이용해보세요. 해시키, 이더리움 메인넷에서 거래가 가능합니다.
- /wallet 버튼을 클릭하면 현재 지갑에 있는 모든 토큰의 달러 환산 가치, HSK 잔고, 현재 가스비 등을 확인할 수 있습니다.
- /bridge 메뉴를 통해 이더리움에 있는 자산을 해시키 체인으로 가져오세요.
- /chain 버튼을 클릭하고 트레이딩을 원하는 체인을 선택해보세요.
─────────────────────

이제 /trading 버튼을 클릭하고 KeyBot을 이용해 보세요!
"""

# 하단 버튼 구성
BOTTOM_KEYBOARD = [
    [KeyboardButton("트레이딩"), KeyboardButton("지갑연결")],
    [KeyboardButton("브릿지"), KeyboardButton("체인선택")]
]

# 전역 변수로 스크리밍 모드 저장
screaming = False

# 트레이딩 텍스트
FIRST_TRADING = """🔄 트레이딩\n
1️⃣ 내 지갑 주소:
2️⃣ 지갑 잔액:
3️⃣ HSK 잔액:
4️⃣ 가스비:
5️⃣ 메인넷:
⛓️ <a href="https://hashkey.blockscout.com/">Explorer</a> | ⛓️ <a href="https://debank.com/">DeBank</a>

"""
BUY_TRADING = """
구매하고자 하는 토큰의 컨트랙트 주소를 입력해주세요.
"""
SELL_TRADING = """
판매하고자 하는 토큰의 컨트랙트 주소를 입력해주세요.
"""
SECOND_TRADING = """토큰 이름: {token_name}
토큰 티커: {token_ticker}

1️⃣ 토큰 가격: 
2️⃣ 시가 총액:
3️⃣ 24시간 거래량:

⛓️ DEX Screener | ⛓️ Gecko Terminal

"""
SET_SLIPPAGE = "슬리피지를 설정해주세요(최대 50%):"
COMPLETE_BUY_TRADING = "0.00 HSK를 지불하고 {token_name} {amount}를 구입했습니다!"
COMPLETE_SELL_TRADING = "{token_name} {amount}를 판매하고 0.00 HSK를 획득했습니다!"

# 트레이딩 > 버튼 텍스트
BUY_BUTTON = "📈 Buy"
SELL_BUTTON = "📉 Sell"

INFO_BUY_AMOUNT_BUTTON = "🪙 토큰 구매를 위해 지불할 HSK 수량 입력"
INFO_SELL_AMOUNT_BUTTON = "🪙 토큰 판매 후 획득할 HSK 수량 입력"
HSK_10_BUTTON = "10 HSK"
HSK_100_BUTTON = "100 HSK"
HSK_1000_BUTTON = "1,000 HSK"
MAX_AMOUNT_BUTTON = "최대 수량 설정"
SET_MAX_AMOUNT_BUTTON = "최대 수량: 616 HSK"
INPUT_TRADING_AMOUNT_BUTTON = "직접 입력:"
INPUT_SLIPPAGE_BUTTON = "✅ 슬리피지 설정: 0.5%"
COMPLETE_BUTTON = "✅ 설정 완료"

# 트레이딩 인라인 키보드 구성
FIRST_TRADING_MARKUP = InlineKeyboardMarkup([
    [InlineKeyboardButton(BUY_BUTTON, callback_data=BUY_BUTTON),
     InlineKeyboardButton(SELL_BUTTON, callback_data=SELL_BUTTON)],
])
BUY_TRADING_MARKUP = InlineKeyboardMarkup([
    [InlineKeyboardButton(INFO_BUY_AMOUNT_BUTTON, callback_data=INFO_BUY_AMOUNT_BUTTON)],
    [InlineKeyboardButton(HSK_10_BUTTON, callback_data=HSK_10_BUTTON),
     InlineKeyboardButton(HSK_100_BUTTON, callback_data=HSK_100_BUTTON),
     InlineKeyboardButton(HSK_1000_BUTTON, callback_data=HSK_1000_BUTTON)],
    [InlineKeyboardButton(MAX_AMOUNT_BUTTON, callback_data=MAX_AMOUNT_BUTTON),
     InlineKeyboardButton(INPUT_TRADING_AMOUNT_BUTTON, callback_data=INPUT_TRADING_AMOUNT_BUTTON)],
    [InlineKeyboardButton(INPUT_SLIPPAGE_BUTTON, callback_data=INPUT_SLIPPAGE_BUTTON)],
    [InlineKeyboardButton(COMPLETE_BUTTON, callback_data=COMPLETE_BUTTON)],
])
SELL_TRADING_MARKUP = InlineKeyboardMarkup([
    [InlineKeyboardButton(INFO_SELL_AMOUNT_BUTTON, callback_data=INFO_SELL_AMOUNT_BUTTON)],
    [InlineKeyboardButton(HSK_10_BUTTON, callback_data=HSK_10_BUTTON),
     InlineKeyboardButton(HSK_100_BUTTON, callback_data=HSK_100_BUTTON),
     InlineKeyboardButton(HSK_1000_BUTTON, callback_data=HSK_1000_BUTTON)],
    [InlineKeyboardButton(MAX_AMOUNT_BUTTON, callback_data=MAX_AMOUNT_BUTTON),
     InlineKeyboardButton(INPUT_TRADING_AMOUNT_BUTTON, callback_data=INPUT_TRADING_AMOUNT_BUTTON)],
    [InlineKeyboardButton(INPUT_SLIPPAGE_BUTTON, callback_data=INPUT_SLIPPAGE_BUTTON)],
    [InlineKeyboardButton(COMPLETE_BUTTON, callback_data=COMPLETE_BUTTON)],
])

# 체인 텍스트
CHAIN_TEXT = "{chain_name}에서 거래를 시작합니다!"

# 체인 선택 > 버튼
HASHKEY_BUTTON = "Hashkey Chain"
ETHEREUM_BUTTON = "Ethereum"

# 체인 선택 인라인 키보드 구성
CHAIN_MARKUP = InlineKeyboardMarkup([
    [InlineKeyboardButton(HASHKEY_BUTTON, callback_data=HASHKEY_BUTTON)],
    [InlineKeyboardButton(ETHEREUM_BUTTON, callback_data=ETHEREUM_BUTTON)]
])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /start 명령어 처리:
    1) 생성된 이미지 전송
    2) 안내 문구 + 하단 4개 버튼(ReplyKeyboard) 전송
    """
    # 유저 이름 (없으면 'User'로 대체)
    username = update.effective_user.first_name or "User"
    
    # 만약 start 명령어를 그룹에서 썼을 경우 update.message가 없을 수 있으므로 체크
    if not update.message:
        return
    
    # ReplyKeyboardMarkup로 하단에 버튼을 띄울 수 있음
    reply_markup = ReplyKeyboardMarkup(
        BOTTOM_KEYBOARD,
        resize_keyboard=True,     # 사용자의 화면 크기에 맞춰 버튼 크기 조절
        one_time_keyboard=False   # True면 한 번 누르고 나면 키보드가 사라짐
    )

    # 안내 문구에 사용자 이름 삽입
    text_to_send = WELCOME_TEXT.format(username=username, wallet_address=wallet_address)

    # 이미지 + 안내 문구 전송 & 하단 메뉴 버튼 표시
    with open("./images/bot_start.png", "rb") as img:
        await update.message.reply_photo(
            photo=img,
            caption=text_to_send,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global screaming
    if not update.message:
        return

    print(f"{update.message.from_user.first_name} wrote {update.message.text}")

    if screaming and update.message.text:
        await update.message.reply_text(
            update.message.text.upper(),
            entities=update.message.entities
        )
    else:
        await update.message.copy(chat_id=update.message.chat_id)

async def trading(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 체인 이름 (없으면 'Hashkey'로 대체)
    chain_name = context.user_data.get("selected_chain", HASHKEY_BUTTON)

    # 안내 문구에 체인 이름 삽입
    text_to_send = CHAIN_TEXT.format(chain_name=chain_name)

    await update.message.reply_text(
        text=text_to_send,
        parse_mode=ParseMode.HTML
    )
    await update.message.reply_text(
        text=FIRST_TRADING,
        parse_mode=ParseMode.HTML,
        reply_markup=FIRST_TRADING_MARKUP,
        disable_web_page_preview=True
    )
    
# 트레이딩 인라인 버튼(📈 Buy, 📉 Sell) 처리
async def trading_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == BUY_BUTTON:
        # BUY 버튼 클릭 시 BUY_TRADING 텍스트 전송
        await query.edit_message_text(
            text=BUY_TRADING,
            parse_mode=ParseMode.HTML,
        )
        # "Buy/Sell 모드" 상태 기억
        context.user_data["waiting_for_buy_input"] = True

    elif query.data == SELL_BUTTON:
        # SELL 버튼 클릭 시 SELL_TRADING 텍스트 전송
        await query.edit_message_text(
            text=SELL_TRADING,
            parse_mode=ParseMode.HTML,
        )
        # "Buy/Sell 모드" 상태 기억
        context.user_data["waiting_for_sell_input"] = True

# 인라인 키보드 생성 함수 (구매 수량 선택용)
def get_trading_buy_amount_markup(selected: str, custom_input: str = None):
    HSK_10_text = f"✅ {HSK_10_BUTTON}" if selected == HSK_10_BUTTON else HSK_10_BUTTON
    HSK_100_text = f"✅ {HSK_100_BUTTON}" if selected == HSK_100_BUTTON else HSK_100_BUTTON
    HSK_1000_text = f"✅ {HSK_1000_BUTTON}" if selected == HSK_1000_BUTTON else HSK_1000_BUTTON
    max_amount_text = f"✅ {MAX_AMOUNT_BUTTON}" if selected == MAX_AMOUNT_BUTTON else MAX_AMOUNT_BUTTON
    if custom_input:
        input_trading_amount_text = f"✅ {INPUT_TRADING_AMOUNT_BUTTON} {custom_input} HSK"
    else:
        input_trading_amount_text = f"✅ {INPUT_TRADING_AMOUNT_BUTTON}" if selected == INPUT_TRADING_AMOUNT_BUTTON else INPUT_TRADING_AMOUNT_BUTTON
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(INFO_BUY_AMOUNT_BUTTON, callback_data=INFO_BUY_AMOUNT_BUTTON)],
        [InlineKeyboardButton(HSK_10_text, callback_data=HSK_10_BUTTON),
         InlineKeyboardButton(HSK_100_text, callback_data=HSK_100_BUTTON),
         InlineKeyboardButton(HSK_1000_text, callback_data=HSK_1000_BUTTON)],
        [InlineKeyboardButton(max_amount_text, callback_data=MAX_AMOUNT_BUTTON),
         InlineKeyboardButton(input_trading_amount_text, callback_data=INPUT_TRADING_AMOUNT_BUTTON)],
        [InlineKeyboardButton(INPUT_SLIPPAGE_BUTTON, callback_data=INPUT_SLIPPAGE_BUTTON)],
        [InlineKeyboardButton(COMPLETE_BUTTON, callback_data=COMPLETE_BUTTON)],
    ])

# 선택한 token amount에 체크
async def trading_buy_amount_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == INPUT_TRADING_AMOUNT_BUTTON:
        # "직접 입력:" 버튼을 누르면 새 메시지로 안내 메시지를 전송합니다.
        msg = await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="구매할 HSK 수량을 입력해주세요:",
            parse_mode=ParseMode.HTML
        )
        # 프롬프트 메시지의 ID 저장 및 플래그 설정
        context.user_data["waiting_for_trading_amount_input"] = True
        context.user_data["trading_buy_prompt_message_id"] = msg.message_id
    else:
        # 그 외 버튼 선택 시 기존 로직대로 처리
        context.user_data["trading_buy_amount"] = data
        updated_markup = get_trading_buy_amount_markup(data)
        await query.edit_message_reply_markup(reply_markup=updated_markup)

def get_trading_buy_amount_markup_with_input(user_input: str):
    HSK_10_text = f"✅ {HSK_10_BUTTON}" if user_input == HSK_10_BUTTON else HSK_10_BUTTON
    HSK_100_text = f"✅ {HSK_100_BUTTON}" if user_input == HSK_100_BUTTON else HSK_100_BUTTON
    HSK_1000_text = f"✅ {HSK_1000_BUTTON}" if user_input == HSK_1000_BUTTON else HSK_1000_BUTTON
    max_amount_text = f"✅ {SET_MAX_AMOUNT_BUTTON}" if user_input == MAX_AMOUNT_BUTTON else MAX_AMOUNT_BUTTON
    # "직접 입력:" 버튼의 텍스트를 사용자 입력값으로 대체하고 "HSK"를 붙임
    input_trading_amount_text = f"{user_input} HSK"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(INFO_BUY_AMOUNT_BUTTON, callback_data=INFO_BUY_AMOUNT_BUTTON)],
        [InlineKeyboardButton(HSK_10_text, callback_data=HSK_10_BUTTON),
         InlineKeyboardButton(HSK_100_text, callback_data=HSK_100_BUTTON),
         InlineKeyboardButton(HSK_1000_text, callback_data=HSK_1000_BUTTON)],
        [InlineKeyboardButton(max_amount_text, callback_data=MAX_AMOUNT_BUTTON),
         InlineKeyboardButton(input_trading_amount_text, callback_data=INPUT_TRADING_AMOUNT_BUTTON)],
        [InlineKeyboardButton(INPUT_SLIPPAGE_BUTTON, callback_data=INPUT_SLIPPAGE_BUTTON)],
        [InlineKeyboardButton(COMPLETE_BUTTON, callback_data=COMPLETE_BUTTON)],
    ])

async def bridge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("브릿지 기능을 실행합니다!")

async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("지갑 연결 기능을 실행합니다!")

async def chain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 디폴트 선택은 Hashkey Chain
    if "selected_chain" not in context.user_data:
        context.user_data["selected_chain"] = HASHKEY_BUTTON
    markup = get_chain_markup(context.user_data["selected_chain"])
    await update.message.reply_text(
        text="⛓️ 체인 선택",
        parse_mode=ParseMode.HTML,
        reply_markup=markup
    )

# 선택 상태에 따른 체인 선택 인라인 키보드 생성
def get_chain_markup(selected: str):
    hashkey_text = f"✅ {HASHKEY_BUTTON}" if selected == HASHKEY_BUTTON else HASHKEY_BUTTON
    ethereum_text = f"✅ {ETHEREUM_BUTTON}" if selected == ETHEREUM_BUTTON else ETHEREUM_BUTTON
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(hashkey_text, callback_data=HASHKEY_BUTTON)],
        [InlineKeyboardButton(ethereum_text, callback_data=ETHEREUM_BUTTON)]
    ])

async def chain_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data in [HASHKEY_BUTTON, ETHEREUM_BUTTON]:
        # 선택 상태 업데이트
        context.user_data["selected_chain"] = data
        updated_markup = get_chain_markup(data)
        # 인라인 키보드 업데이트 (텍스트에 ✅ 이모지 추가)
        await query.edit_message_reply_markup(reply_markup=updated_markup)

# 텍스트가 전송됐을 때 처리할 로직
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global screaming

    # 사용자가 입력(또는 버튼 클릭)한 텍스트
    user_text = update.message.text

    # 구매 수량 직접 입력 플래그 처리
    if context.user_data.get("waiting_for_trading_amount_input", False):
        # 사용자가 입력한 값을 저장 (예: "3.2")
        input_value = user_text.strip()
        context.user_data["trading_buy_amount"] = input_value
        # 사용자가 입력한 메시지 삭제 (이펙트처럼 사라지도록)
        try:
            await update.message.delete()
        except Exception as e:
            logger.error(f"메시지 삭제 실패: {e}")
        # 업데이트할 인라인 키보드 재생성:
        trading_msg_id = context.user_data.get("trading_message_id")
        if trading_msg_id:
            new_markup = get_trading_buy_amount_markup(INPUT_TRADING_AMOUNT_BUTTON, custom_input=input_value)
            try:
                await context.bot.edit_message_reply_markup(
                    chat_id=update.message.chat.id,
                    message_id=trading_msg_id,
                    reply_markup=new_markup
                )
            except Exception as e:
                logger.error(f"인라인 키보드 업데이트 실패: {e}")
        context.user_data["waiting_for_trading_amount_input"] = False
        return
    
    # 만약 "Buy 모드" 상태라면, 입력값 검증 후 SECOND_TRADING 출력
    if context.user_data.get("waiting_for_buy_input", False):
        if user_text == "test":
            if "trading_buy_amount" not in context.user_data:
                context.user_data["trading_buy_amount"] = HSK_10_BUTTON
            sent_trading = await update.message.reply_text(
                text=SECOND_TRADING,
                parse_mode=ParseMode.HTML,
                reply_markup=BUY_TRADING_MARKUP
            )
            # 메시지 ID 저장 (나중에 인라인 키보드 업데이트에 사용)
            context.user_data["trading_message_id"] = sent_trading.message_id
        else:
            await update.message.reply_text("지원하지 않는 토큰입니다.")
        context.user_data["waiting_for_buy_input"] = False
        return
    elif context.user_data.get("waiting_for_sell_input", False):
        if user_text == "test":
            sent_trading = await update.message.reply_text(
                text=SECOND_TRADING,
                parse_mode=ParseMode.HTML,
                reply_markup=SELL_TRADING_MARKUP
            )
            # 메시지 ID 저장 (나중에 인라인 키보드 업데이트에 사용)
            context.user_data["trading_message_id"] = sent_trading.message_id
        else:
            await update.message.reply_text("지원하지 않는 토큰입니다.")
        context.user_data["waiting_for_sell_input"] = False
        return
    
    # 버튼 텍스트에 따른 분기
    if user_text == "트레이딩":
        await trading(update, context)
    elif user_text == "브릿지":
        await bridge(update, context)
    elif user_text == "지갑연결":
        await wallet(update, context)
    elif user_text == "체인선택":
        await chain(update, context)
    else:
        # 그 외 일반 텍스트는 echo 로직 수행
        print(f"{update.message.from_user.first_name} wrote {user_text}")

        if screaming and user_text:
            await update.message.reply_text(
                user_text.upper(),
                entities=update.message.entities
            )
        else:
            await update.message.copy(chat_id=update.message.chat_id)


async def main():
    # 토큰을 본인의 봇 토큰으로 변경하세요.
    app = ApplicationBuilder().token(botfather_token).build()

    # 핸들러 등록
    app.add_handler(CommandHandler("start", start))
    
    # 안내문에 써놓은 명령어들에 대한 핸들러들
    app.add_handler(CommandHandler("trading", trading))
    app.add_handler(CommandHandler("wallet", wallet))
    app.add_handler(CommandHandler("bridge", bridge))
    app.add_handler(CommandHandler("chain", chain))

    # 트레이딩 인라인 버튼 처리: BUY와 SELL
    app.add_handler(CallbackQueryHandler(trading_button_handler, pattern='^(📈 Buy|📉 Sell)$'))
    # 체인 선택 콜백 처리
    app.add_handler(CallbackQueryHandler(chain_callback_handler, pattern=f'^({HASHKEY_BUTTON}|{ETHEREUM_BUTTON})$'))
    # 트레이딩 - 구매할 HSK 수량 선택 콜백 처리
    app.add_handler(CallbackQueryHandler(trading_buy_amount_callback_handler, pattern=f'^({HSK_10_BUTTON}|{HSK_100_BUTTON}|{HSK_1000_BUTTON}|{MAX_AMOUNT_BUTTON}|{INPUT_TRADING_AMOUNT_BUTTON})$'))

    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))

    print("🤖 봇 실행 중...")
    await app.run_polling()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())