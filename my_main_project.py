#бот для создания анкеты. сначала открывается главная клавиатура, при "Создать анкету" подключаются состояния для отправки фото, возраста, описания, местоположения 

from aiogram import executor,Bot,Dispatcher,types
from aiogram.types import InlineKeyboardButton,InlineKeyboardMarkup
from aiogram.types import KeyboardButton,ReplyKeyboardMarkup,ReplyKeyboardRemove
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher  import FSMContext
from sqlite_practic import db_start, edit_profile, create_profile

async def start_bot(_):
    await db_start()

storage = MemoryStorage()
bot = Bot('')
dp = Dispatcher(bot, storage=storage)



class ProfileStatesGroup(StatesGroup):
    photo = State()
    name = State()
    age = State()
    disc = State()



def keyboard1(): 
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    b1 = KeyboardButton('Информация')
    
    
    b2 = KeyboardButton('Создать анкету')
    kb.add(b1).insert(b2)
    return kb

def keyboard2():
    kb2 = ReplyKeyboardMarkup(resize_keyboard=True)
    b11 = KeyboardButton('Отменить')
    b22= KeyboardButton('Главное меню')
    
    kb2.add(b11).add(b22)
    return kb2




@dp.message_handler(Text(equals='Отменить'), state="*")
async def cmd_cancel(message:types.Message, state:FSMContext):
    if state is None:
        return
    await state.finish()
    await message.reply('Вы прервали создание анкеты!',
                        reply_markup=keyboard1())


@dp.message_handler(commands=['start'])
async def cmd_start(message:types.Message):
    await message.answer('Привет! Твой навигатор-<b>клавиатура в нижней части экрана.</b>',
                         reply_markup=keyboard1(),
                         parse_mode='HTML')
    await create_profile(user_id=message.from_user.id)


@dp.message_handler(Text(equals='Информация'))
async def info(message:types.Message):
    await message.answer('Я Бот для создание твоей анкеты, которую сохраню в базу данных')
 
    
@dp.message_handler(Text(equals='Создать анкету'))
async def info(message:types.Message):
    await message.answer('Отлично! Для начала мне отправь свое фото',
                         reply_markup=keyboard2())
    await ProfileStatesGroup.next()

@dp.message_handler(lambda message: not message.photo, state=ProfileStatesGroup.photo)
async def not_photo(message:types.Message):
    await message.answer('Пожалуйста, отправьте фото')


@dp.message_handler(content_types=['photo'], state=ProfileStatesGroup.photo)
async def send_photo(message:types.Message, state:FSMContext):
    async with state.proxy() as data:
        data['photo'] = message.photo[0].file_id
    await message.answer('Отлично, теперь отправь свое имя')   
    await ProfileStatesGroup.next() 
    
@dp.message_handler(state=ProfileStatesGroup.name)
async def send_name(message:types.Message, state:FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await message.answer('Отлично, теперь отправь свой возраст')   
    await ProfileStatesGroup.next() 



@dp.message_handler(lambda message: not message.text.isdigit() or int(message.text) < 8 or int(message.text) >60,state=ProfileStatesGroup.age)
async def not_age(message:types.Message):
    await message.answer('Отправьте реальный возраст!')


@dp.message_handler(state=ProfileStatesGroup.age)
async def send_age(message:types.Message, state:FSMContext):
    async with state.proxy() as data:
        data['age'] = message.text
    await message.answer('Расскажите о себе')   
    await ProfileStatesGroup.next() 

@dp.message_handler(state=ProfileStatesGroup.disc)
async def send_disc(message:types.Message, state:FSMContext):
    async with state.proxy() as data:
        data['disc'] = message.text 
    await message.answer('Анкета создана!')
    await bot.send_photo(message.from_user.id,
                            photo = data['photo'],
                            caption=f"{data['name']}, {data['age']}\n{data['disc']} ") 
    await edit_profile(state,user_id=message.from_user.id)  
    await state.finish()






if __name__=='__main__':
    
    executor.start_polling(dp, skip_updates=True, on_startup=start_bot)
