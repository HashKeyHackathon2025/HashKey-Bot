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
wallet_address = "0x3ff0908E1891BE439658ca15387C000D5c7921C1"
wallet_HSK_balance = 0.0
token_address = "0xba946A82D6c13A9DE94551feFDc1E05F92c6aF8d"
token_name = "Test Wrapped HSK"
token_ticker = "WHSK"
token_price = 1.0
token_market_cap = "120,000,000"
token_24h_volume = "40,000,237"
send_token_amount = 1.0
gas_fee = 0.00
token_balance = 10
token_amount = 0
wallet_tx_hash = "0x656710Bd0B06D5D6836816c961CF984BeCa4f554"
weth_balance = 20.0
weth_amount = 10.0
bridge_tx_hash = "0x8bddb64ec9bfcd9a8538b939c944d3ffdb5be058ad82d710f10fbbdebe8e2c50"

# 안내 문구
WELCOME_TEXT = """Welcome to KeyBot {username}!

I've created a wallet address for your convenient trading:\n
<code>{wallet_address}</code>

First, register your EOA with the
/register function.

────────────────
- /trading Try using this feature. You can trade on Hashkey and Ethereum mainnet.
- /wallet Click this button to check the dollar value of all tokens in your current wallet, HSK balance, current gas fees, and more.
- /bridge Bring your assets from Ethereum to the Hashkey chain through this menu.
- /chain Click this button and choose the chain you want to trade on.
────────────────

Now click the /trading button and try using KeyBot!
"""

# 하단 버튼 구성
BOTTOM_KEYBOARD = [
    [KeyboardButton("Trading"), KeyboardButton("Wallet Settings")],
    [KeyboardButton("Bridge"), KeyboardButton("Chain Selection")]
]

# 전역 변수로 스크리밍 모드 저장
screaming = False

# 트레이딩 텍스트
TRADING_TEXT = "Starting trading on {chain_name}!"
FIRST_TRADING = """🔄 Trading\n
1️⃣ My wallet address: """ + wallet_address + """
2️⃣ Wallet balance: """ + str(token_balance) + """ HSK
3️⃣ HSK balance: """ + str(token_balance) + """ HSK
4️⃣ Gas fee: """ + str(gas_fee) + """ HSK (&lt; 0.1 Gwei)
5️⃣ Mainnet: <a href="https://global.hashkey.com/en-US/">Hashkey Chain</a>\n
⛓️ <a href="https://hashkey.blockscout.com/">Explorer</a> | ⛓️ <a href="https://debank.com/">DeBank</a>

"""
BUY_TRADING = """
Please enter the contract address of the token you want to purchase.
"""
SELL_TRADING = """
Please enter the contract address of the token you want to sell.
"""
SECOND_TRADING = """Token Name: """ + token_name + """
Token Ticker: """ + token_ticker + """

1️⃣ Token Price: """ + str(token_price) + """ HSK
2️⃣ Market Cap: """ + token_market_cap + """ HSK
3️⃣ 24-hour Trading Volume: """ + token_24h_volume + """ HSK

⛓️ DEX Screener | ⛓️ Gecko Terminal

"""
SET_SLIPPAGE = "Please set slippage (maximum 50%):"
COMPLETE_BUY_TRADING = "Purchased {amount} {token_name} by paying {trading_buy_amount} HSK!"
COMPLETE_SELL_TRADING = "Sold {amount} {token_name} and received {trading_sell_amount} HSK!"

# 트레이딩 > 버튼 텍스트
BUY_BUTTON = "📈 Buy"
SELL_BUTTON = "📉 Sell"

INFO_BUY_AMOUNT_BUTTON = "🪙 Token purchase amount (HSK) input"
INFO_SELL_AMOUNT_BUTTON = "🪙 Amount of HSK to receive after selling tokens"
HSK_10_BUTTON = "10 HSK"
HSK_100_BUTTON = "100 HSK"
HSK_1000_BUTTON = "1,000 HSK"
MAX_AMOUNT_BUTTON = "Set maximum amount"
SET_MAX_AMOUNT_BUTTON = "Maximum amount: " + str(token_balance) + " HSK"
INPUT_TRADING_AMOUNT_BUTTON = "Manual entry:"
INPUT_SLIPPAGE_BUTTON = "✅ Slippage setting: 0.5%"
COMPLETE_TRADING_BUTTON = "✅ Trading Setup Complete"

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
    [InlineKeyboardButton(COMPLETE_TRADING_BUTTON, callback_data=COMPLETE_TRADING_BUTTON)],
])
SELL_TRADING_MARKUP = InlineKeyboardMarkup([
    [InlineKeyboardButton(INFO_SELL_AMOUNT_BUTTON, callback_data=INFO_SELL_AMOUNT_BUTTON)],
    [InlineKeyboardButton(HSK_10_BUTTON, callback_data=HSK_10_BUTTON),
     InlineKeyboardButton(HSK_100_BUTTON, callback_data=HSK_100_BUTTON),
     InlineKeyboardButton(HSK_1000_BUTTON, callback_data=HSK_1000_BUTTON)],
    [InlineKeyboardButton(MAX_AMOUNT_BUTTON, callback_data=MAX_AMOUNT_BUTTON),
     InlineKeyboardButton(INPUT_TRADING_AMOUNT_BUTTON, callback_data=INPUT_TRADING_AMOUNT_BUTTON)],
    [InlineKeyboardButton(INPUT_SLIPPAGE_BUTTON, callback_data=INPUT_SLIPPAGE_BUTTON)],
    [InlineKeyboardButton(COMPLETE_TRADING_BUTTON, callback_data=COMPLETE_TRADING_BUTTON)],
])

# 체인 선택 > 버튼
HASHKEY_BUTTON = "Hashkey Chain"
ETHEREUM_BUTTON = "Ethereum"

# 체인 선택 인라인 키보드 구성
CHAIN_MARKUP = InlineKeyboardMarkup([
    [InlineKeyboardButton(HASHKEY_BUTTON, callback_data=HASHKEY_BUTTON)],
    [InlineKeyboardButton(ETHEREUM_BUTTON, callback_data=ETHEREUM_BUTTON)]
])

# 지갑 설정 텍스트
WALLET_TEXT = """👛 Wallet Settings\n
1️⃣ Wallet Address: <code>""" + str(wallet_address) + """</code>
2️⃣ HSK balance: """ + str(wallet_HSK_balance) + """\n
⛓️ <a href="https://hashkey.blockscout.com/">Connect Explorer</a>
⛓️ <a href="https://debank.com/">Connect DeBank</a>

"""
SEND_TOKEN = """🔄 Claim Token
Transfer HSK from the wallet created by KeyBot to another wallet.
"""
COMPLETE_SEND_TOKEN = """Transferred {token_amount} HSK to {wallet_address}!\n
Transaction Hash:
{tx_hash}
"""

# 지갑 설정 > 버튼
SEND_TOKEN_BUTTON = "🔄 Claim Token"

INFO_WALLET_ADDRESS_BUTTON = "1️⃣ Enter wallet address to transfer HSK"
INPUT_WALLET_ADDRESS_BUTTON = "Please enter your wallet address::"
INFO_SEND_PER_BUTTON = "2️⃣ Select the amount of HSK to send"
HSK_25PER_BUTTON = "25%"
HSK_50PER_BUTTON = "50%"
HSK_75PER_BUTTON = "75%"
HSK_100PER_BUTTON = "100%"
INPUT_HSK_PER_BUTTON = "Manual entry:"
COMPLETE_SEND_TOKEN_BUTTON = "✅ Token Setup Complete"

# 지갑 설정 인라인 키보드 구성
WALLET_MARKUP = InlineKeyboardMarkup([
    [InlineKeyboardButton(SEND_TOKEN_BUTTON, callback_data=SEND_TOKEN_BUTTON)]
])
SEND_TOKEN_MARKUP = InlineKeyboardMarkup([
    [InlineKeyboardButton(INFO_WALLET_ADDRESS_BUTTON, callback_data=INFO_WALLET_ADDRESS_BUTTON)],
    [InlineKeyboardButton(INPUT_WALLET_ADDRESS_BUTTON, callback_data=INPUT_WALLET_ADDRESS_BUTTON)],
    [InlineKeyboardButton(INFO_SEND_PER_BUTTON, callback_data=INFO_SEND_PER_BUTTON)],
    [InlineKeyboardButton(HSK_25PER_BUTTON, callback_data=HSK_25PER_BUTTON),
     InlineKeyboardButton(HSK_50PER_BUTTON, callback_data=HSK_50PER_BUTTON),
     InlineKeyboardButton(HSK_75PER_BUTTON, callback_data=HSK_75PER_BUTTON)],
    [InlineKeyboardButton(HSK_100PER_BUTTON, callback_data=HSK_100PER_BUTTON),
     InlineKeyboardButton(INPUT_HSK_PER_BUTTON, callback_data=INPUT_HSK_PER_BUTTON)],
    [InlineKeyboardButton(COMPLETE_SEND_TOKEN_BUTTON, callback_data=COMPLETE_SEND_TOKEN_BUTTON)]
])

# 브릿지 텍스트
BRIDGE_TEXT = "🔄 Transfer your assets from Ethereum mainnet to Hashkey chain mainnet."
COMPLETE_BRIDGE = """
{weth_amount} WETH has been transferred from Ethereum mainnet to Hashkey mainnet!\n

Transaction Hash:
{bridge_tx_hash}
"""

# 브릿지 > 버튼
INFO_FROM_MAINNET_BUTTON = "1️⃣ Select source network"
SET_FROM_MAINNET_BUTTON = "✅ Ethereum"
INFO_TO_MAINNET_BUTTON = "2️⃣ Set up destination mainnet"
SET_TO_MAINNET_BUTTON = "✅ Hashkey Chain"
INFO_SELECT_ASSET_BUTTON = "3️⃣ Select asset"
SET_ASSET_BUTTON = "✅ WETH"
INFO_ASSET_BALANCE_BUTTON = str(weth_balance) + " WETH available"
WETH_25PER_BUTTON = " 25% "
WETH_50PER_BUTTON = " 50% "
WETH_75PER_BUTTON = " 75% "
WETH_100PER_BUTTON = " 100% "
INPUT_WETH_PER_BUTTON = " Manual entry: "
COMPLETE_BRIDGE_BUTTON = "✅ Bridge Setup Complete"

# 브릿지 설정 인라인 키보드 구성
BRIDGE_MARKUP = InlineKeyboardMarkup([
    [InlineKeyboardButton(INFO_FROM_MAINNET_BUTTON, callback_data=INFO_FROM_MAINNET_BUTTON)],
    [InlineKeyboardButton(SET_FROM_MAINNET_BUTTON, callback_data=SET_FROM_MAINNET_BUTTON)],
    [InlineKeyboardButton(INFO_TO_MAINNET_BUTTON, callback_data=INFO_TO_MAINNET_BUTTON)],
    [InlineKeyboardButton(SET_TO_MAINNET_BUTTON, callback_data=SET_TO_MAINNET_BUTTON)],
    [InlineKeyboardButton(INFO_SELECT_ASSET_BUTTON, callback_data=INFO_SELECT_ASSET_BUTTON)],
    [InlineKeyboardButton(SET_ASSET_BUTTON, callback_data=SET_ASSET_BUTTON)],
    [InlineKeyboardButton(INFO_ASSET_BALANCE_BUTTON, callback_data=INFO_ASSET_BALANCE_BUTTON)],
    [InlineKeyboardButton(WETH_25PER_BUTTON, callback_data=WETH_25PER_BUTTON),
     InlineKeyboardButton(WETH_50PER_BUTTON, callback_data=WETH_50PER_BUTTON),
     InlineKeyboardButton(WETH_75PER_BUTTON, callback_data=WETH_75PER_BUTTON)],
    [InlineKeyboardButton(WETH_100PER_BUTTON, callback_data=WETH_100PER_BUTTON),
     InlineKeyboardButton(INPUT_WETH_PER_BUTTON, callback_data=INPUT_WETH_PER_BUTTON)],
    [InlineKeyboardButton(COMPLETE_BRIDGE_BUTTON, callback_data=COMPLETE_BRIDGE_BUTTON)]
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

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 등록할 지갑 주소를 입력하라는 프롬프트 메시지 전송
    await update.message.reply_text("Please enter your wallet address to register:")
    # 이후 사용자의 입력을 기다리기 위한 플래그 설정
    context.user_data["waiting_for_register"] = True

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
    text_to_send = TRADING_TEXT.format(chain_name=chain_name)

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

    context.user_data["trading_slippage"] = 0.5
    
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
def get_trading_buy_amount_markup(selected: str, custom_input: str = None, custom_slippage: str = None):
    HSK_10_text = f"✅ {HSK_10_BUTTON}" if selected == HSK_10_BUTTON else HSK_10_BUTTON
    HSK_100_text = f"✅ {HSK_100_BUTTON}" if selected == HSK_100_BUTTON else HSK_100_BUTTON
    HSK_1000_text = f"✅ {HSK_1000_BUTTON}" if selected == HSK_1000_BUTTON else HSK_1000_BUTTON
    max_amount_text = f"✅ {SET_MAX_AMOUNT_BUTTON}" if selected == MAX_AMOUNT_BUTTON else MAX_AMOUNT_BUTTON
    if custom_input:
        input_trading_amount_text = f"✅ {INPUT_TRADING_AMOUNT_BUTTON} {custom_input} HSK"
    else:
        input_trading_amount_text = f"✅ {INPUT_TRADING_AMOUNT_BUTTON}" if selected == INPUT_TRADING_AMOUNT_BUTTON else INPUT_TRADING_AMOUNT_BUTTON
    if custom_slippage:
        slippage_text = f"✅ 슬리피지 설정: {custom_slippage}%"
    else:
        slippage_text = INPUT_SLIPPAGE_BUTTON
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(INFO_BUY_AMOUNT_BUTTON, callback_data=INFO_BUY_AMOUNT_BUTTON)],
        [InlineKeyboardButton(HSK_10_text, callback_data=HSK_10_BUTTON),
         InlineKeyboardButton(HSK_100_text, callback_data=HSK_100_BUTTON),
         InlineKeyboardButton(HSK_1000_text, callback_data=HSK_1000_BUTTON)],
        [InlineKeyboardButton(max_amount_text, callback_data=MAX_AMOUNT_BUTTON),
         InlineKeyboardButton(input_trading_amount_text, callback_data=INPUT_TRADING_AMOUNT_BUTTON)],
        [InlineKeyboardButton(slippage_text, callback_data=INPUT_SLIPPAGE_BUTTON)],
        [InlineKeyboardButton(COMPLETE_TRADING_BUTTON, callback_data=COMPLETE_TRADING_BUTTON)],
    ])

# 선택한 token amount에 체크
async def trading_buy_amount_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == INPUT_TRADING_AMOUNT_BUTTON:
        # "직접 입력:" 버튼 선택 시, 새 메시지로 프롬프트 전송
        msg = await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="Please enter the amount of HSK to buy:",
            parse_mode=ParseMode.HTML
        )
        context.user_data["waiting_for_trading_amount_input"] = True
        context.user_data["trading_buy_prompt_message_id"] = msg.message_id
    elif data == INPUT_SLIPPAGE_BUTTON:
        # 슬리피지 입력 처리
        msg = await context.bot.send_message(
            chat_id=query.message.chat.id,
            text=SET_SLIPPAGE,
            parse_mode=ParseMode.HTML
        )
        context.user_data["waiting_for_slippage_input"] = True
        context.user_data["slippage_prompt_message_id"] = msg.message_id
    elif data in [HSK_10_BUTTON, HSK_100_BUTTON, HSK_1000_BUTTON, MAX_AMOUNT_BUTTON]:
        if data == HSK_10_BUTTON:
            numeric_value = 10
        elif data == HSK_100_BUTTON:
            numeric_value = 100
        elif data == HSK_1000_BUTTON:
            numeric_value = 1000
        elif data == MAX_AMOUNT_BUTTON:
            numeric_value = token_balance  # 미리 정의된 balance 변수 사용
        # 단일 변수에 숫자값 저장
        context.user_data["trading_buy_amount"] = str(numeric_value)
        updated_markup = get_trading_buy_amount_markup(data)
        await query.edit_message_reply_markup(reply_markup=updated_markup)
    else:
        # 기타 경우는 별도 처리 (필요하면)
        pass

async def complete_buy_trading_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    # COMPLETE_BUY_TRADING 텍스트에 token_name과 amount 값을 대입하여 출력합니다.
    complete_text = COMPLETE_BUY_TRADING.format(trading_buy_amount=context.user_data["trading_buy_amount"],token_name=token_name, amount=9.8)
    await context.bot.send_message(
        chat_id=query.message.chat.id,
        text=complete_text,
        parse_mode=ParseMode.HTML
    )

async def bridge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sent_msg = await update.message.reply_text(
        text=BRIDGE_TEXT,
        parse_mode=ParseMode.HTML,
        reply_markup=BRIDGE_MARKUP
    )
    # 메시지 ID를 저장 (이후 지갑 주소 입력 업데이트에 사용)
    context.user_data["bridge_message_id"] = sent_msg.message_id

# 인라인 키보드 생성 함수 (전송할 지갑주소 세팅, HSK 수량 선택용)
def get_bridge_markup(selected: str, custom_input: str = None):
    WETH_25per_text = f"✅ {WETH_25PER_BUTTON}" if selected == WETH_25PER_BUTTON else WETH_25PER_BUTTON
    WETH_50per_text = f"✅ {WETH_50PER_BUTTON}" if selected == WETH_50PER_BUTTON else WETH_50PER_BUTTON
    WETH_75per_text = f"✅ {WETH_75PER_BUTTON}" if selected == WETH_75PER_BUTTON else WETH_75PER_BUTTON
    WETH_100per_text = f"✅ {WETH_100PER_BUTTON}" if selected == WETH_100PER_BUTTON else WETH_100PER_BUTTON
    if custom_input:
        input_WETH_per_text = f"✅ {INPUT_WETH_PER_BUTTON} {custom_input}"
    else:
        input_WETH_per_text = f"✅ {INPUT_WETH_PER_BUTTON}" if selected == INPUT_WETH_PER_BUTTON else INPUT_WETH_PER_BUTTON
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(INFO_FROM_MAINNET_BUTTON, callback_data=INFO_FROM_MAINNET_BUTTON)],
        [InlineKeyboardButton(SET_FROM_MAINNET_BUTTON, callback_data=SET_FROM_MAINNET_BUTTON)],
        [InlineKeyboardButton(INFO_TO_MAINNET_BUTTON, callback_data=INFO_TO_MAINNET_BUTTON)],
        [InlineKeyboardButton(SET_TO_MAINNET_BUTTON, callback_data=SET_TO_MAINNET_BUTTON)],
        [InlineKeyboardButton(INFO_SELECT_ASSET_BUTTON, callback_data=INFO_SELECT_ASSET_BUTTON)],
        [InlineKeyboardButton(SET_ASSET_BUTTON, callback_data=SET_ASSET_BUTTON)],
        [InlineKeyboardButton(INFO_ASSET_BALANCE_BUTTON, callback_data=INFO_ASSET_BALANCE_BUTTON)],
        [InlineKeyboardButton(WETH_25per_text, callback_data=WETH_25PER_BUTTON),
         InlineKeyboardButton(WETH_50per_text, callback_data=WETH_50PER_BUTTON),
         InlineKeyboardButton(WETH_75per_text, callback_data=WETH_75PER_BUTTON)],
        [InlineKeyboardButton(WETH_100per_text, callback_data=WETH_100PER_BUTTON),
        InlineKeyboardButton(input_WETH_per_text, callback_data=INPUT_WETH_PER_BUTTON)],
        [InlineKeyboardButton(COMPLETE_BRIDGE_BUTTON, callback_data=COMPLETE_BRIDGE_BUTTON)]
    ])

# 선택한 token per에 체크
async def bridge_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == INPUT_WETH_PER_BUTTON:
        # "직접 입력:" 버튼 선택 시, 새 메시지로 프롬프트 전송
        msg = await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="Please enter the amount of WETH to convert to Hashkey Chain:",
            parse_mode=ParseMode.HTML
        )
        context.user_data["waiting_for_bridge_input"] = True
        context.user_data["bridge_prompt_message_id"] = msg.message_id
    elif data in [WETH_25PER_BUTTON, WETH_50PER_BUTTON, WETH_75PER_BUTTON, WETH_100PER_BUTTON]:
        if data == WETH_25PER_BUTTON:
            numeric_value = 25
        elif data == WETH_50PER_BUTTON:
            numeric_value = 50
        elif data == WETH_75PER_BUTTON:
            numeric_value = 75
        elif data == WETH_100PER_BUTTON:
            numeric_value = 100
        # 단일 변수에 숫자값 저장
        context.user_data["bridge_per"] = str(numeric_value)
        updated_bridge_markup = get_bridge_markup(data)
        await query.edit_message_reply_markup(reply_markup=updated_bridge_markup)
    else:
        # 기타 경우는 별도 처리 (필요하면)
        pass

async def complete_bridge_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    # COMPLETE_BRIDGE 텍스트에 wallet_address, token_amount, tx_hash 값을 대입하여 출력합니다.
    complete_text = COMPLETE_BRIDGE.format(weth_amount=weth_amount,bridge_tx_hash=bridge_tx_hash)
    await context.bot.send_message(
        chat_id=query.message.chat.id,
        text=complete_text,
        parse_mode=ParseMode.HTML
    )

async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        text=WALLET_TEXT,
        parse_mode=ParseMode.HTML,
        reply_markup=WALLET_MARKUP,
        disable_web_page_preview=True
    )

async def send_token_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    # SEND_TOKEN 메시지 전송
    sent_msg = await context.bot.send_message(
        chat_id=query.message.chat.id,
        text=SEND_TOKEN,
        parse_mode=ParseMode.HTML,
        reply_markup=SEND_TOKEN_MARKUP
    )
    # 메시지 ID를 저장 (이후 지갑 주소 입력 업데이트에 사용)
    context.user_data["send_token_message_id"] = sent_msg.message_id
    context.user_data["send_token_per"] = 25

# 인라인 키보드 생성 함수 (전송할 지갑주소 세팅, HSK 수량 선택용)
def get_wallet_and_token_per_markup(selected: str, custom_input: str = None, custom_wallet: str = None):
    HSK_25per_text = f"✅ {HSK_25PER_BUTTON}" if selected == HSK_25PER_BUTTON else HSK_25PER_BUTTON
    HSK_50per_text = f"✅ {HSK_50PER_BUTTON}" if selected == HSK_50PER_BUTTON else HSK_50PER_BUTTON
    HSK_75per_text = f"✅ {HSK_75PER_BUTTON}" if selected == HSK_75PER_BUTTON else HSK_75PER_BUTTON
    HSK_100per_text = f"✅ {HSK_100PER_BUTTON}" if selected == HSK_100PER_BUTTON else HSK_100PER_BUTTON
    if custom_input:
        input_HSK_per_text = f"✅ {INPUT_HSK_PER_BUTTON} {custom_input} HSK"
    else:
        input_HSK_per_text = f"✅ {INPUT_HSK_PER_BUTTON}" if selected == INPUT_HSK_PER_BUTTON else INPUT_HSK_PER_BUTTON
    if custom_wallet:
        input_wallet_address_text = f"✅ {custom_wallet}"
    else:
        input_wallet_address_text = f"✅ {INPUT_WALLET_ADDRESS_BUTTON}" if selected == INPUT_WALLET_ADDRESS_BUTTON else INPUT_WALLET_ADDRESS_BUTTON
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(INFO_WALLET_ADDRESS_BUTTON, callback_data=INFO_WALLET_ADDRESS_BUTTON)],
        [InlineKeyboardButton(input_wallet_address_text, callback_data=INPUT_WALLET_ADDRESS_BUTTON)],
        [InlineKeyboardButton(INFO_SEND_PER_BUTTON, callback_data=INFO_SEND_PER_BUTTON)],
        [InlineKeyboardButton(HSK_25per_text, callback_data=HSK_25PER_BUTTON),
         InlineKeyboardButton(HSK_50per_text, callback_data=HSK_50PER_BUTTON),
         InlineKeyboardButton(HSK_75per_text, callback_data=HSK_75PER_BUTTON)],
        [InlineKeyboardButton(HSK_100per_text, callback_data=HSK_100PER_BUTTON),
         InlineKeyboardButton(input_HSK_per_text, callback_data=INPUT_HSK_PER_BUTTON)],
        [InlineKeyboardButton(COMPLETE_SEND_TOKEN_BUTTON, callback_data=COMPLETE_SEND_TOKEN_BUTTON)]
    ])

# 선택한 token per에 체크
async def send_wallet_and_token_per_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == INPUT_HSK_PER_BUTTON:
        # "직접 입력:" 버튼 선택 시, 새 메시지로 프롬프트 전송
        msg = await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="Please enter the amount of HSK to transfer:",
            parse_mode=ParseMode.HTML
        )
        context.user_data["waiting_for_send_token_amount_input"] = True
        context.user_data["send_token_prompt_message_id"] = msg.message_id
    elif data == INPUT_WALLET_ADDRESS_BUTTON:
        # 지갑 주소 입력 처리
        msg = await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="Please enter the wallet address that will receive HSK from KeyBot wallet:",
            parse_mode=ParseMode.HTML
        )
        context.user_data["waiting_for_wallet_address_input"] = True
        context.user_data["wallet_address_prompt_message_id"] = msg.message_id
    elif data in [HSK_25PER_BUTTON, HSK_50PER_BUTTON, HSK_75PER_BUTTON, HSK_100PER_BUTTON]:
        if data == HSK_25PER_BUTTON:
            numeric_value = 25
        elif data == HSK_50PER_BUTTON:
            numeric_value = 50
        elif data == HSK_75PER_BUTTON:
            numeric_value = 75
        elif data == HSK_100PER_BUTTON:
            numeric_value = 100
        # 단일 변수에 숫자값 저장
        context.user_data["send_token_per"] = str(numeric_value)
        updated_markup = get_wallet_and_token_per_markup(data, custom_wallet=context.user_data.get("send_wallet_address"))
        await query.edit_message_reply_markup(reply_markup=updated_markup)
    else:
        # 기타 경우는 별도 처리 (필요하면)
        pass

async def complete_send_token_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    # COMPLETE_SEND_TOKEN 텍스트에 wallet_address, token_amount, tx_hash 값을 대입하여 출력합니다.
    complete_text = COMPLETE_SEND_TOKEN.format(wallet_address=context.user_data["send_wallet_address"],token_amount=context.user_data["send_token_per"], tx_hash=wallet_tx_hash)
    await context.bot.send_message(
        chat_id=query.message.chat.id,
        text=complete_text,
        parse_mode=ParseMode.HTML
    )

async def chain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 디폴트 선택은 Hashkey Chain
    if "selected_chain" not in context.user_data:
        context.user_data["selected_chain"] = HASHKEY_BUTTON
    markup = get_chain_markup(context.user_data["selected_chain"])
    await update.message.reply_text(
        text="⛓️ Chain Selection",
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

    # 지갑 등록 입력 처리
    if context.user_data.get("waiting_for_register", False):
        context.user_data["user_EOA"] = update.message.text.strip()
        context.user_data["waiting_for_register"] = False
        await update.message.reply_text("Your wallet address has been registered!")
        return

    # 브릿지 수량 직접 입력 처리
    if context.user_data.get("waiting_for_bridge_input", False):
        context.user_data["WETH_amount"] = user_text  # 슬리피지 값 저장 (예: "1.0")
        try:
            await update.message.delete()
        except Exception as e:
            logger.error(f"메시지 삭제 실패: {e}")
        bridge_msg_id = context.user_data.get("bridge_message_id")
        if bridge_msg_id:
            new_markup = get_bridge_markup(
                INPUT_WETH_PER_BUTTON,
                custom_input=context.user_data.get("WETH_amount"),
            )
            try:
                await context.bot.edit_message_reply_markup(
                    chat_id=update.message.chat.id,
                    message_id=bridge_msg_id,
                    reply_markup=new_markup
                )
            except Exception as e:
                logger.error(f"인라인 키보드 업데이트 실패: {e}")
        context.user_data["waiting_for_bridge_input"] = False
        return
    
    # 트레이딩 구매 수량 직접 입력 처리
    if context.user_data.get("waiting_for_trading_amount_input", False):
        # 직접 입력한 값을 저장 (단일 변수로 관리)
        context.user_data["trading_buy_amount"] = user_text  # 예: "3.2"
        try:
            await update.message.delete()
        except Exception as e:
            logger.error(f"메시지 삭제 실패: {e}")
        trading_msg_id = context.user_data.get("trading_message_id")
        if trading_msg_id:
            new_markup = get_trading_buy_amount_markup(
                "",
                custom_input=user_text,
                custom_slippage=""
            )
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

    # 슬리피지 직접 입력 처리
    if context.user_data.get("waiting_for_slippage_input", False):
        context.user_data["trading_slippage"] = user_text  # 슬리피지 값 저장 (예: "1.0")
        try:
            await update.message.delete()
        except Exception as e:
            logger.error(f"메시지 삭제 실패: {e}")
        trading_msg_id = context.user_data.get("trading_message_id")
        if trading_msg_id:
            new_markup = get_trading_buy_amount_markup(
                MAX_AMOUNT_BUTTON,
                custom_input="",
                custom_slippage=user_text
            )
            try:
                await context.bot.edit_message_reply_markup(
                    chat_id=update.message.chat.id,
                    message_id=trading_msg_id,
                    reply_markup=new_markup
                )
            except Exception as e:
                logger.error(f"인라인 키보드 업데이트 실패: {e}")
        context.user_data["waiting_for_slippage_input"] = False
        return
    
    # 지갑 주소 직접 입력 처리
    if context.user_data.get("waiting_for_wallet_address_input", False):
        context.user_data["send_wallet_address"] = user_text  # 지갑 주소 값 저장 (예: "0x00000")
        try:
            await update.message.delete()
        except Exception as e:
            logger.error(f"메시지 삭제 실패: {e}")
        send_token_msg_id = context.user_data.get("send_token_message_id")
        if send_token_msg_id:
            new_markup = get_wallet_and_token_per_markup(
                "",
                "",
                custom_wallet=user_text
            )
            try:
                await context.bot.edit_message_reply_markup(
                    chat_id=update.message.chat.id,
                    message_id=send_token_msg_id,
                    reply_markup=new_markup
                )
            except Exception as e:
                logger.error(f"인라인 키보드 업데이트 실패: {e}")
        context.user_data["waiting_for_wallet_address_input"] = False
        return
    
    # 전송 토큰 비율 직접 입력 처리
    if context.user_data.get("waiting_for_send_token_amount_input", False):
        context.user_data["send_token_per"] = user_text
        try:
            await update.message.delete()
        except Exception as e:
            logger.error(f"메시지 삭제 실패: {e}")
        send_token_msg_id = context.user_data.get("send_token_message_id")
        if send_token_msg_id:
            new_markup = get_wallet_and_token_per_markup(
                INPUT_HSK_PER_BUTTON,
                custom_input=user_text,
                custom_wallet=context.user_data.get("send_wallet_address")
            )
            try:
                await context.bot.edit_message_reply_markup(
                    chat_id=update.message.chat.id,
                    message_id=send_token_msg_id,
                    reply_markup=new_markup
                )
            except Exception as e:
                logger.error(f"인라인 키보드 업데이트 실패: {e}")
        context.user_data["waiting_for_send_token_amount_input"] = False
        return
    
    # 만약 "Buy 모드" 상태라면, 입력값 검증 후 SECOND_TRADING 출력
    if context.user_data.get("waiting_for_buy_input", False):
        if user_text == token_address:
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
            await update.message.reply_text("This token is not supported.")
        context.user_data["waiting_for_buy_input"] = False
        return
    elif context.user_data.get("waiting_for_sell_input", False):
        if user_text == token_address:
            sent_trading = await update.message.reply_text(
                text=SECOND_TRADING,
                parse_mode=ParseMode.HTML,
                reply_markup=SELL_TRADING_MARKUP
            )
            # 메시지 ID 저장 (나중에 인라인 키보드 업데이트에 사용)
            context.user_data["trading_message_id"] = sent_trading.message_id
        else:
            await update.message.reply_text("This token is not supported.")
        context.user_data["waiting_for_sell_input"] = False
        return
    
    # 버튼 텍스트에 따른 분기
    if user_text == "Trading":
        await trading(update, context)
    elif user_text == "Bridge":
        await bridge(update, context)
    elif user_text == "Wallet Settings":
        await wallet(update, context)
    elif user_text == "Chain Selection":
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
    app.add_handler(CommandHandler("register", register))
    app.add_handler(CommandHandler("trading", trading))
    app.add_handler(CommandHandler("wallet", wallet))
    app.add_handler(CommandHandler("bridge", bridge))
    app.add_handler(CommandHandler("chain", chain))

    ########### 지갑연결 ##############
    # 토큰 전송 - 전송할 지갑 주소, HSK 비율 선택 콜백 처리
    app.add_handler(CallbackQueryHandler(send_wallet_and_token_per_callback_handler, pattern=f'^({HSK_25PER_BUTTON}|{HSK_50PER_BUTTON}|{HSK_75PER_BUTTON}|{HSK_100PER_BUTTON}|{INPUT_HSK_PER_BUTTON}|{INPUT_WALLET_ADDRESS_BUTTON})$'))
    # 지갑연결 - 토큰 전송
    app.add_handler(CallbackQueryHandler(send_token_handler, pattern=f'^{SEND_TOKEN_BUTTON}$'))
    # COMPLETE_SEND_TOKEN_BUTTON 처리: 버튼을 누르면 COMPLETE_SEND_TOKEN 출력
    app.add_handler(CallbackQueryHandler(complete_send_token_handler, pattern=f'^{COMPLETE_SEND_TOKEN_BUTTON}$'))

    ########### 브릿지 ##############
    # 브릿지 선택 콜백 처리
    app.add_handler(CallbackQueryHandler(bridge_callback_handler, pattern=f'^({WETH_25PER_BUTTON}|{WETH_50PER_BUTTON}|{WETH_75PER_BUTTON}|{WETH_100PER_BUTTON}|{INPUT_WETH_PER_BUTTON})$'))
    # 브릿지
    app.add_handler(CallbackQueryHandler(complete_bridge_handler, pattern=f'^{COMPLETE_BRIDGE_BUTTON}$'))

    ########### 체인선택 ##############
    # 체인 선택 콜백 처리
    app.add_handler(CallbackQueryHandler(chain_callback_handler, pattern=f'^({HASHKEY_BUTTON}|{ETHEREUM_BUTTON})$'))

    ########### 트레이딩 ##############
    # 트레이딩 인라인 버튼 처리: BUY와 SELL
    app.add_handler(CallbackQueryHandler(trading_button_handler, pattern='^(📈 Buy|📉 Sell)$'))
    # 트레이딩 - 구매할 HSK 수량 선택 콜백 처리
    app.add_handler(CallbackQueryHandler(trading_buy_amount_callback_handler, pattern=f'^({HSK_10_BUTTON}|{HSK_100_BUTTON}|{HSK_1000_BUTTON}|{MAX_AMOUNT_BUTTON}|{INPUT_TRADING_AMOUNT_BUTTON}|{INPUT_SLIPPAGE_BUTTON})$'))
    # COMPLETE_TRADING_BUTTON 처리: 버튼을 누르면 COMPLETE_BUY_TRADING 출력
    app.add_handler(CallbackQueryHandler(complete_buy_trading_handler, pattern=f'^{COMPLETE_TRADING_BUTTON}$'))

    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))

    print("🤖 Bot running ...")
    await app.run_polling()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())