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

# 안내 문구
WELCOME_TEXT = """KeyBot에 오신걸 환영합니다 {username}!

{username}님의 간편한 거래를 위해 제가 지갑 주소를 생성했습니다.

<code>0x7896Dfb8f8Ef9e36BA37ACB111AaE3D704dbc51Ed</code>

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
FIRST_TRADING = """🔄 트레이딩

1️⃣ 내 지갑 주소:
2️⃣ 지갑 잔액:
3️⃣ HSK 잔액:
4️⃣ 가스비:
5️⃣ 메인넷:
⛓️ Explorer | ⛓️ DeBank

"""
BUY_TRADING = """
1️⃣ 구매하고자 하는 토큰의 컨트랙트 주소를 입력해주세요.
2️⃣ 컨트랙트 주소를 모르신다면 [토큰 목록] 버튼을 클릭해서 토큰 주소를 확인해주세요.
"""
SELL_TRADING = """
1️⃣ 판매하고자 하는 토큰의 컨트랙트 주소를 입력해주세요.
2️⃣ 컨트랙트 주소를 모르신다면 [토큰 목록] 버튼을 클릭해서 토큰 주소를 확인해주세요.
"""
SECOND_TRADING = """토큰 이름: {Token Name}
토큰 티커: {Token Ticker}

1️⃣ 토큰 가격: 
2️⃣ 시가 총액:
3️⃣ 24시간 거래량:

⛓️ DEX Screener | ⛓️ Gecko Terminal

"""

# 트레이딩 > 버튼 텍스트
BUY_BUTTON = "📈 Buy"
SELL_BUTTON = "📉 Sell"

TOKEN_LIST_BUTTON = "토큰 목록"

HSK_AMOUNT_BUTTON = "토큰 구매를 위해 지불할 HSK 수량 입력"
HSK_10_BUTTON = "10 HSK"
HSK_100_BUTTON = "100 HSK"
HSK_1000_BUTTON = "1,000 HSK"
MAX_AMOUNT_BUTTON = "최대 수량 설정"
SELF_INPUT_BUTTON = "직접 입력:"
SLIPAGE_BUTTON = "슬리피지 설정: 0.5%"
COMPLETE_BUTTON = "설정 완료"

# 인라인 키보드 구성
FIRST_TRADING_MARKUP = InlineKeyboardMarkup([
    [InlineKeyboardButton(BUY_BUTTON, callback_data=BUY_BUTTON),
     InlineKeyboardButton(SELL_BUTTON, callback_data=SELL_BUTTON)],
])
TRADING_TOKEN_MARKUP = InlineKeyboardMarkup([
    [InlineKeyboardButton(TOKEN_LIST_BUTTON, callback_data=TOKEN_LIST_BUTTON)]
])
SECOND_TRADING_MARKUP = InlineKeyboardMarkup([
    [InlineKeyboardButton(HSK_AMOUNT_BUTTON, callback_data=HSK_AMOUNT_BUTTON)],
    [InlineKeyboardButton(HSK_10_BUTTON, callback_data=HSK_10_BUTTON),
     InlineKeyboardButton(HSK_100_BUTTON, callback_data=HSK_100_BUTTON),
     InlineKeyboardButton(HSK_1000_BUTTON, callback_data=HSK_1000_BUTTON)],
    [InlineKeyboardButton(MAX_AMOUNT_BUTTON, callback_data=MAX_AMOUNT_BUTTON),
     InlineKeyboardButton(SELF_INPUT_BUTTON, callback_data=SELF_INPUT_BUTTON)],
    [InlineKeyboardButton(SLIPAGE_BUTTON, callback_data=SLIPAGE_BUTTON)],
    [InlineKeyboardButton(COMPLETE_BUTTON, callback_data=COMPLETE_BUTTON)],
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
    text_to_send = WELCOME_TEXT.format(username=username)

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

# 이하 각 명령어를 처리할 함수들
async def trading(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("{Chain name}에서 거래를 시작합니다!")
    await update.message.reply_text(
        text=FIRST_TRADING,
        parse_mode=ParseMode.HTML,
        reply_markup=FIRST_TRADING_MARKUP
    )
    
# 새로운 함수: 트레이딩 인라인 버튼(📈 Buy, 📉 Sell) 처리
async def trading_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == BUY_BUTTON:
        # BUY 버튼 클릭 시 BUY_TRADING 텍스트 전송 (여기서는 edit_message_text로 대체)
        await query.edit_message_text(
            text=BUY_TRADING,
            parse_mode=ParseMode.HTML,
            reply_markup=TRADING_TOKEN_MARKUP
        )
    elif query.data == SELL_BUTTON:
        # SELL 버튼 클릭 시 SELL_TRADING 텍스트 전송
        await query.edit_message_text(
            text=SELL_TRADING,
            parse_mode=ParseMode.HTML,
            reply_markup=TRADING_TOKEN_MARKUP
        )

async def bridge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("브릿지 기능을 실행합니다!")

async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("지갑 연결 기능을 실행합니다!")

async def chain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("체인 선택 기능을 실행합니다!")

# async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     # update.message가 없으면 callback_query.message 사용
#     message = update.message if update.message else update.callback_query.message
#     await message.reply_text(
#         FIRST_MENU,
#         parse_mode=ParseMode.HTML,
#         reply_markup=FIRST_MENU_MARKUP
#     )

# async def button_tap(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     query = update.callback_query
#     await query.answer()

#     if query.data == NEXT_BUTTON:
#         await query.edit_message_text(
#             SECOND_MENU,
#             parse_mode=ParseMode.HTML,
#             reply_markup=SECOND_MENU_MARKUP
#         )
#     elif query.data == BACK_BUTTON:
#         await query.edit_message_text(
#             FIRST_MENU,
#             parse_mode=ParseMode.HTML,
#             reply_markup=FIRST_MENU_MARKUP
#         )

# 하단 버튼을 눌렀을 때(= 텍스트가 전송됐을 때) 처리할 로직
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global screaming

    # 사용자가 입력(또는 버튼 클릭)한 텍스트
    user_text = update.message.text

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
    # app.add_handler(CommandHandler("menu", menu))
    
    # 안내문에 써놓은 명령어들에 대한 핸들러들
    app.add_handler(CommandHandler("trading", trading))
    app.add_handler(CommandHandler("wallet", wallet))
    app.add_handler(CommandHandler("bridge", bridge))
    app.add_handler(CommandHandler("chain", chain))

    # 트레이딩 인라인 버튼 처리: BUY와 SELL
    app.add_handler(CallbackQueryHandler(trading_button_handler, pattern='^(📈 Buy|📉 Sell)$'))

    # app.add_handler(CallbackQueryHandler(button_tap, pattern='^(Next|Back|Tutorial)$'))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))

    print("🤖 봇 실행 중...")
    await app.run_polling()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())