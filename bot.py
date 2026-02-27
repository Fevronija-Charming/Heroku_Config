from pydantic import BaseModel, Field, ValidationError
import os
from tokenize import String
from aiogram.client import bot
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())
from pydantic import parse_obj_as
from sqlalchemy.ext.asyncio import create_async_engine
import asyncio
from aiogram import Bot, Dispatcher, types, F, BaseMiddleware
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple, Union
from aiogram.filters import CommandStart, Command, or_f
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import psycopg2 as ps
import datetime, time
from colorama import *
from faststream.rabbit import RabbitBroker 
# конфигурация команд в меню привествия
from aiogram.types import BotCommand
private=[BotCommand(command="dop_poisk",description="утончённый поиск по композиции орнамента ППП"),
         BotCommand(command="glav_poisk",description="поиск по основным параметрам ППП"),
         BotCommand(command="help",description="перечень всех возможным команд бота"),
        BotCommand(command="posobija",description="учебные материалы о Павловопосадских платках"),
         BotCommand(command='admin',description='вызов функций редактирования БД'),
         BotCommand(command="description",description="информация о создателе Февронии"),
        BotCommand(command="start",description="вывод приветственного сообщения"),
        BotCommand(command="stop",description="аварийный останов бота"),
        BotCommand(command="exit",description="отмена поискового запроса, выход из анкеты")]
rezim_raboty=0
class RezimRabotyAdmina(BaseMiddleware):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
    async def __call__(self, handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],event:Message,data:Dict[str, Any]) -> None:
        text=event.text
        user_id=event.from_user.id
        global rezim_raboty
        if text == "традиции_ношения" and user_id == int(os.getenv("MYUSERID")):
            rezim_raboty=1
            await self.bot.send_message(chat_id=user_id,text="Режим записи")
            return await handler(event, data)
        elif text =="посмотреть запись об уроке" and user_id == int(os.getenv("MYUSERID")):
            rezim_raboty = 2
            await self.bot.send_message(chat_id=user_id, text= "Режим просомотра")
            return await handler(event, data)
        elif text == "внести исправление в запись урока" and user_id == int(os.getenv("MYUSERID")):
            rezim_raboty = 3
            await self.bot.send_message(chat_id=user_id, text= "Режим редактирования")
            return await handler(event, data)
        else:
            return await handler(event, data)
class AdminControl(BaseMiddleware):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
    async def __call__(self, handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],event:Message,data:Dict[str, Any]) -> None:
        text=event.text
        user_id=event.from_user.id
        global nov_id_zapisi
        global id_zapisi
        global kolvo_strok
        global upomjanutye_platki
        if text == "/admin" and user_id == int(os.getenv("MYUSERID")):
            kolvo_strok = 0
            upomjanutye_platki=[]
            await self.bot.send_message(chat_id=user_id,text="админ здравствуй")
            # создание интерфейса для sql запроса
            import psycopg2 as ps
            connection = ps.connect(host=os.getenv("DBHOST"), database=os.getenv("DBNAMEOLD"),
                                    user=os.getenv("DBUSERNAME"),
                                    password=os.getenv("DBPASSWORD"), port=os.getenv("DBPORT"))
            # создание интерфейса для sql запроса
            zapros = "SELECT * FROM ПППЛАТКИ;"
            cursor = connection.cursor()
            # отправить запрос системе управления
            cursor.execute(zapros)
            while True:
                next_row = cursor.fetchone()
                if next_row:
                    id = next_row[0]
                    upomjanutye_platki.append(next_row[1])
                    kolvo_strok = kolvo_strok + 1
                    if id>nov_id_zapisi:
                        nov_id_zapisi = id
                else:
                    break
            connection.commit()
            # закрытие соединенмя с ДБ для безопасности
            cursor.close()
            connection.close()
            id_zapisi = nov_id_zapisi+1
            await self.bot.send_message(chat_id=user_id, text=f"{'Следующий доступный номер записи: '}{id_zapisi}")
            await self.bot.send_message(chat_id=user_id, text=f"{'Всего записей:'}{kolvo_strok}")
            await self.bot.send_message(chat_id=user_id, text=f"{'Всего записей:'}{upomjanutye_platki}")
            return await handler(event,data)
        elif text != "/admin":
            return await handler(event, data)
        else:
            await self.bot.send_message(chat_id=user_id, text="чужак")
            return
#работа с базой данных
from sqlalchemy import  DateTime, String, Float, Column, Integer, func,Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
engine = create_async_engine(os.getenv("DBURL"),echo=True,max_overflow=5)
session_factory = async_sessionmaker(bind=engine,class_=AsyncSession,expire_on_commit=False)
from datamodels import Platoky,Tradicii,Banda,Symboly,Base,Otzyvy
async def create_platky():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
async def destroy_platky():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all())
signal=0
platok_infa=[]
tradicija={}
tradicija_noshenija={}
zapis_tradicija=0
upomjanutye_platki=[]
pokazatel_validacii=0
id_zapisi=100
id_tradicii=1
nov_id_zapisi=0
kolvo_strok=0
unikalnost=0
#Command_set=[start,stop,describe,admin,help,teh-poisk,hud-poisk]
# этр образ бота в программе
Bot = Bot(token=os.getenv('TOKEN'))
# это обьект для обработки сообщений
dp=Dispatcher()
#broker=RabbitBroker(url="amqp://guest:guest@localhost:5672/")
#@broker.subscriber("PLATOKY")
#async def get_platky_fromFASTAPI(data: str):
    #await Bot.send_message(chat_id=os.getenv('MYUSERID'), text='Добавлен новый платок')
    #await Bot.send_message(chat_id=os.getenv('MYUSERID'),text=data)
dp.message.middleware(AdminControl(Bot))
dp.message.middleware(RezimRabotyAdmina(Bot))
# клавы из файла классов
from klaviatury import klava_poisk1, klava_poisk2, klava_kolorit, klava_posobiy, klava_material, klava_bahroma,klava_symboly
from klaviatury import klava_admina_uroki, klava_admina_platki, klava_admina_glav,klava_admina_materialy, klava_privetstvije
from klaviatury import klava_symboly2
from fsm_states import Otzyv, Vvod_TradNosh
from templates import platok_predstav
# костыль для получения id фото в системе тг
class Vvod_Foto(StatesGroup):
    get_foto_id=State()
@dp.message((F.text.lower()=="скормить_фото"))
async def foto_avatara(message: types.Message, state: FSMContext):
    await message.answer(text="Получение id для фото")
    await state.set_state(Vvod_Foto.get_foto_id)
@dp.message(Vvod_Foto.get_foto_id, F.photo)
async def FotoSsyla(message: types.Message, state: FSMContext):
    await state.update_data(FotoAvatar=message.photo[-1].file_id)
    data=await state.get_data()
    await state.clear()
    await message.answer(text=f"{data}")
    print(data)
@dp.message((F.text.lower()=="ввести запись об уроке в буфер"))
async def opred_nomer_uroka(message: types.Message):
    await message.answer(text="Определение занятия",reply_markup=klava_posobiy)
from fsm_states import Vvod_TradNosh
@dp.message((F.text.lower()=="традиции_ношения"))
async def trad_noshen(message: types.Message, state: FSMContext):
    global rezim_raboty
    if rezim_raboty==1:
        await message.answer(text="Напиши первое название традиции ношения")
        await state.set_state(Vvod_TradNosh.nazvanijeTrd1)
    elif rezim_raboty==2:
        await message.answer(text="Вот информация о традиции ношения")
@dp.message(Vvod_TradNosh.nazvanijeTrd1, F.text)
async def nazvanije_Trad1(message: types.Message, state: FSMContext):
    await state.update_data(nazvanije_trad1=message.text)
    await message.answer(text="Введи второе название традиции ношения")
    await state.set_state(Vvod_TradNosh.nazvanijeTrd2)
@dp.message(Vvod_TradNosh.nazvanijeTrd2, F.text)
async def nazvanije_Trad2(message: types.Message, state: FSMContext):
    await state.update_data(nazvanije_trad2=message.text)
    await message.answer(text="Введи третье название традиции ношения")
    await state.set_state(Vvod_TradNosh.nazvanijeTrd3)
@dp.message(Vvod_TradNosh.nazvanijeTrd3, F.text)
async def nazvanije_Trad3(message: types.Message, state: FSMContext):
    await state.update_data(nazvanije_trad3=message.text)
    await message.answer(text="Пришли фото традиции ношения 1")
    await state.set_state(Vvod_TradNosh.FotoTrd1)
@dp.message(Vvod_TradNosh.FotoTrd1, F.photo)
async def FotoTrad1(message: types.Message, state: FSMContext):
    await state.update_data(FotoTrd1=message.photo[-1].file_id)
    await message.answer(text="Пришли фото традиции ношения 2")
    await state.set_state(Vvod_TradNosh.FotoTrd2)
@dp.message(Vvod_TradNosh.FotoTrd2, F.photo)
async def FotoTrad2(message: types.Message, state: FSMContext):
    await state.update_data(FotoTrd2=message.photo[-1].file_id)
    await message.answer(text="Пришли фото традиции ношения 3")
    await state.set_state(Vvod_TradNosh.FotoTrd3)
@dp.message(Vvod_TradNosh.FotoTrd3, F.photo)
async def FotoTrad3(message: types.Message, state: FSMContext):
    await state.update_data(FotoTrd3=message.photo[-1].file_id)
    await message.answer(text="Пришли фото традиции ношения 4")
    await state.set_state(Vvod_TradNosh.FotoTrd4)
@dp.message(Vvod_TradNosh.FotoTrd4, F.photo)
async def FotoTrad4(message: types.Message, state: FSMContext):
    await state.update_data(FotoTrd4=message.photo[-1].file_id)
    await message.answer(text="Пришли фото традиции ношения 5")
    await state.set_state(Vvod_TradNosh.FotoTrd5)
@dp.message(Vvod_TradNosh.FotoTrd5, F.photo)
async def FotoTrad5(message: types.Message, state: FSMContext):
    await state.update_data(FotoTrd5=message.photo[-1].file_id)
    await message.answer(text="Приведи этнографическое описание традиции ношения")
    await state.set_state(Vvod_TradNosh.EtnoGrafOpis)
@dp.message(Vvod_TradNosh.EtnoGrafOpis, F.text)
async def Ethoopis(message: types.Message, state: FSMContext):
        await state.update_data(EthoGrafOpis=message.text)
        await message.answer(text="Приведи описание повязывания и одевания платка на голову")
        await state.set_state(Vvod_TradNosh.TehnicOpis)
@dp.message(Vvod_TradNosh.TehnicOpis, F.text)
async def Tehnicopis(message: types.Message, state: FSMContext):
        await state.update_data(TehnicOpis=message.text)
        await message.answer(text="Пришли ссылку на видео о данной традции ношения 1")
        await state.set_state(Vvod_TradNosh.VideoSylka1)
@dp.message(Vvod_TradNosh.VideoSylka1, F.text)
async def VideoSsylka1(message: types.Message, state: FSMContext):
        await state.update_data(VideoSsylka1=message.text)
        await message.answer(text="Пришли ссылку на видео о данной традции ношения 2")
        await state.set_state(Vvod_TradNosh.VideoSylka2)
@dp.message(Vvod_TradNosh.VideoSylka2, F.text)
async def VideoSsylka2(message: types.Message, state: FSMContext):
        await state.update_data(VideoSsylka2=message.text)
        await message.answer(text="Приведи предназначение данной традиции ношения 1")
        await state.set_state(Vvod_TradNosh.Prednaz1)
@dp.message(Vvod_TradNosh.Prednaz1, F.text)
async def Prednaz1(message: types.Message, state: FSMContext):
        await state.update_data(Prednaz1=message.text)
        await message.answer(text="Приведи предназначение данной традиции ношения 2")
        await state.set_state(Vvod_TradNosh.Prednaz2)
@dp.message(Vvod_TradNosh.Prednaz2, F.text)
async def Prednaz2(message: types.Message, state: FSMContext):
        await state.update_data(Prednaz2=message.text)
        await message.answer(text="Напиши, как платок набрасывается на голову 1")
        await state.set_state(Vvod_TradNosh.Nabrasyvanije1)
@dp.message(Vvod_TradNosh.Nabrasyvanije1, F.text)
async def Narbasyvanije1(message: types.Message, state: FSMContext):
        await state.update_data(Nabrasyvanije1=message.text)
        await message.answer(text="Напиши, как платок набрасывается на голову 2")
        await state.set_state(Vvod_TradNosh.Nabrasyvanije2)
@dp.message(Vvod_TradNosh.Nabrasyvanije2, F.text)
async def Nabrasyvanije2(message: types.Message, state: FSMContext):
        await state.update_data(Nabrasyvanije2=message.text)
        await message.answer(text="Опиши, как платок крепится на голову 1")
        await state.set_state(Vvod_TradNosh.Kreplenije1)
@dp.message(Vvod_TradNosh.Kreplenije1, F.text)
async def Kreplenije1(message: types.Message, state: FSMContext):
        await state.update_data(Kreplenije1=message.text)
        await message.answer(text="Опиши, как платок крепится на голову 2")
        await state.set_state(Vvod_TradNosh.Kreplenije2)
@dp.message(Vvod_TradNosh.Kreplenije2, F.text)
async def Kreplenije2(message: types.Message, state: FSMContext):
        await state.update_data(Kreplenije2=message.text)
        await message.answer(text="Укажи этнографическую принадлежность традиции ношения")
        await state.set_state(Vvod_TradNosh.EtnoGrafPrin)
@dp.message(Vvod_TradNosh.EtnoGrafPrin, F.text)
async def Etnografopis(message: types.Message, state: FSMContext):
        await state.update_data(EthnografPrin=message.text)
        await message.answer(text="Укажи географическую принадлежность традиции ношения")
        await state.set_state(Vvod_TradNosh.GeografPrin)
@dp.message(Vvod_TradNosh.GeografPrin, F.text)
async def Georgafopis(message: types.Message, state: FSMContext):
        await state.update_data(GeografPrin=message.text)
        await message.answer(text="Сведения о традиции ношения записаны")
        global tradicija
        global zapis_tradicija
        global id_tradicii
        data=await state.get_data()
        tradicija["id_tradicii"] = id_tradicii
        tradicija["nazvanije_tradicii_1"] = data.get("nazvanije_trad1", None)
        tradicija["nazvanije_tradicii_2"] = data.get("nazvanije_trad2", None)
        tradicija["nazvanije_tradicii_3"] = data.get("nazvanije_trad3", None)
        tradicija["ssylka_foto_1"] = data.get("FotoTrd1", None)
        tradicija["ssylka_foto_2"] = data.get("FotoTrd2", None)
        tradicija["ssylka_foto_3"] = data.get("FotoTrd3", None)
        tradicija["ssylka_foto_4"] = data.get("FotoTrd4", None)
        tradicija["ssylka_foto_5"] = data.get("FotoTrd5", None)
        tradicija["etno_opis"]= data.get("EthoGrafOpis", None)
        tradicija["tehnic_opis"]= data.get("TehnicOpis", None)
        tradicija["ssylka_video_1"]= data.get("VideoSsylka1", None)
        tradicija["ssylka_video_2"]= data.get("VideoSsylka2", None)
        tradicija["prednaz_1"]=data.get("Prednaz1", None)
        tradicija["prednaz_2"] = data.get("Prednaz2", None)
        tradicija["narbasyvanije_1"]= data.get("Nabrasyvanije1", None)
        tradicija["narbasyvanije_2"]= data.get("Nabrasyvanije2", None)
        tradicija["kreplenije_1"]=data.get("Kreplenije1", None)
        tradicija["kreplenije_2"]=data.get("Kreplenije2", None)
        tradicija["etnograf_prinad"]=data.get("EthnografPrin", None)
        tradicija["geograf_prinad"]=data.get("GeografPrin", None)
        zapis_tradicija = 1
        await state.clear()
class Tradicija_Schema(BaseModel):
    id_tradicii: int
    nazvanije_tradicii_1: str = Field(min_length=5, max_length=50)
    nazvanije_tradicii_2: str = Field(min_length=5, max_length=50)
    nazvanije_tradicii_3: str= Field(min_length=5, max_length=50)
    ssylka_foto_1: str= Field(min_length=82, max_length=84)
    ssylka_foto_2: str= Field(min_length=82, max_length=84)
    ssylka_foto_3: str= Field(min_length=82, max_length=84)
    ssylka_foto_4: str= Field(min_length=82, max_length=84)
    ssylka_foto_5: str= Field(min_length=82, max_length=84)
    etno_opis: str= Field(min_length=100, max_length=1000)
    tehnic_opis: str= Field(min_length=100, max_length=1000)
    ssylka_video_1: str= Field(min_length=48, max_length=48)
    ssylka_video_2: str= Field(min_length=48, max_length=48)
    prednaz_1: str= Field(min_length=5, max_length=25)
    prednaz_2: str= Field(min_length=5, max_length=25)
    narbasyvanije_1: str= Field(min_length=5, max_length=25)
    narbasyvanije_2: str= Field(min_length=5, max_length=25)
    kreplenije_1: str= Field(min_length=5, max_length=25)
    kreplenije_2: str= Field(min_length=5, max_length=25)
    etnograf_prinad: str= Field(min_length=5, max_length=25)
    geograf_prinad: str = Field(min_length=5, max_length=500)
@dp.message((F.text.lower()=="проверка_традиции"))
async def proverka_tradicii(message: types.Message):
    await message.answer(text="Проверяем запись традиции")
    global tradicija
    global zapis_tradicija
    if zapis_tradicija == 1:
        try:
            tradicija_kontroll = Tradicija_Schema(**tradicija)
            await message.answer(text="DATA OK")
            try:
                tradicija_eksemp = Tradicii(id=tradicija_kontroll.id_tradicii,
                                            Название_традиции_1=tradicija_kontroll.nazvanije_tradicii_1,
                                            Название_традиции_2=tradicija_kontroll.nazvanije_tradicii_2,
                                            Название_традиции_3=tradicija_kontroll.nazvanije_tradicii_3,
                                            Фото_ссылка_1=tradicija_kontroll.ssylka_foto_1,
                                            Фото_ссылка_2=tradicija_kontroll.ssylka_foto_2,
                                            Фото_ссылка_3=tradicija_kontroll.ssylka_foto_3,
                                            Фото_ссылка_4=tradicija_kontroll.ssylka_foto_4,
                                            Фото_ссылка_5=tradicija_kontroll.ssylka_foto_5,
                                            Описание_этническое=tradicija_kontroll.etno_opis,
                                            Описание_техническое=tradicija_kontroll.tehnic_opis,
                                            Видео_ссылка_1=tradicija_kontroll.ssylka_video_1,
                                            Видео_ссылка_2=tradicija_kontroll.ssylka_video_2,
                                            Сфера_применения_1=tradicija_kontroll.prednaz_1,
                                            Сфера_применения_2=tradicija_kontroll.prednaz_2,
                                            Форма_платка_при_одевании_1=tradicija_kontroll.narbasyvanije_1,
                                            Форма_платка_при_одевании_2=tradicija_kontroll.narbasyvanije_2,
                                            Способ_закрепления_платка_1=tradicija_kontroll.kreplenije_1,
                                            Способ_закрепления_платка_2=tradicija_kontroll.kreplenije_2,
                                            Этническая_классификация=tradicija_kontroll.etnograf_prinad,
                                            Географическое_распространение=tradicija_kontroll.geograf_prinad)
                session = session_factory()
                session.add(tradicija_eksemp)
                await session.commit()
                await message.answer(text="DB OK")
            except:
                await emssage.answer(text="DB ERROR)")
        except:
            await emssage.answer(text="DATA ERROR)")
    else:
        await message.answer(text="Нечего проверять, сначала введите запись в буфер")
# логика основных команд по ключевым словам
@dp.message((F.text.lower() == "оставить отзыв о приложении"))
async def zapis_otzyva(message: types.Message, state: FSMContext):
    id_polzak=message.from_user.id
    await message.answer(text="Пожалуйста, представьтесь", reply_markup=ReplyKeyboardRemove())
    await message.answer(text="Напишите Ваше имя или ник")
    await state.set_state(Otzyv.AvtorOtzyva)
    await state.update_data(id_polzak=id_polzak)
@dp.message(Otzyv.AvtorOtzyva, F.text)
async def zapis_otzyva2(message: types.Message, state: FSMContext):
        await state.update_data(imja_avtr_polz=message.text)
        await message.answer(text="Дайте оценку работе платочного бота. Напишите Вашу благодарность, жалобу на неисправность в работе.")
        await message.answer(text="Предложения по развитию проекта также приветствуются.")
        await state.set_state(Otzyv.TextOtzyva)
@dp.message(Otzyv.TextOtzyva, F.text)
async def zapis_otzyva3(message: types.Message, state: FSMContext):
        tochnoje_vremja = str(datetime.datetime.now())
        vremja_format=tochnoje_vremja[:-10]
        sekundi = int(time.time())
        await state.update_data(text_otzyva=message.text)
        await message.answer(text="Спасибо за ващ отзыв, отреагируем на него в ближайшее время")
        svedenija=await state.get_data()
        otzyv_eksemp=Otzyvy(Индефикатор_Автора=svedenija.get("id_polzak",None), 
    Автор_Отзыва=svedenija.get("imja_avtr_polz",None), 
    Текст_Отзыва=svedenija.get("text_otzyva",None),
    Время_Записи_Отзыва=tochnoje_vremja,
    Секунды_Записи_Отзыва=sekundi)
        session = session_factory()
        session.add(otzyv_eksemp_eksemp)
        await session.commit()
        await message.answer(text="DB OK")
# логика основных команд по ключевым словам
@dp.message((F.text.lower() == "значение символов на платке"))
async def otrisovka_symbola1(message: types.Message):
    await message.answer(text="Выбран сегмент символов на платке", reply_markup=klava_symboly)
@dp.message((F.text.lower() == "другие символы"))
async def otrisovka_symbola2(message: types.Message):
    await message.answer(text="Вот продолжение сегмента символов на платке", reply_markup=klava_symboly2)
@dp.message(or_f((F.text=="Восьмиугольник"),(F.text=="Квадрат"),(F.text=="Ромб"),(F.text.lower()=="Круг")))
async def znachenije_symbola1(message: types.Message):
    symbol = message.text
    connection = ps.connect(host=os.getenv("DBHOST"), database=os.getenv("DBNAMEOLD"), user=os.getenv("DBUSERNAME"),
                            password=os.getenv("DBPASSWORD"), port=os.getenv("DBPORT"))
    # создание интерфейса для sql запроса
    cursor = connection.cursor()
    zapros = "SELECT * FROM Значение_Символов_Орнамента WHERE Название_Символа=%s ;"
    # отправить запрос системе управления
    cursor.execute(zapros, (symbol,))
    row = cursor.fetchone()
    if row:
        await message.answer(text="Вот сведения по значению данного символа")
        await message.answer(text=f"{row}")
    else:
        await message.answer(text="Данного символа в базе не обнаружено")
    # закрытие соединенмя с ДБ для безопасности
    cursor.close()
    connection.close()
@dp.message(or_f((Command("glav_poisk")),(F.text.lower()=="поиск по техническим харак."),(F.text.lower()=="основной")))
async def poisk1(message: types.Message):
    await message.answer(text="Поиск1",reply_markup=klava_poisk1)
    await message.delete()
    print(Back.GREEN + Fore.BLACK + Style.BRIGHT+"Поиск1")
@dp.message((F.text.lower()=="/dop_poisk"))
@dp.message((F.text.lower()=="поиск по худож. харак."))
@dp.message((F.text.lower()=="художественный поиск"))
async def poisk1(message: types.Message):
    await message.answer(text="поиск2",reply_markup=klava_poisk2)
    print("Поиск2")
@dp.message((F.text.lower()=="/help"))
@dp.message((F.text.lower()=="помощь"))
@dp.message((F.text.lower()=="/commands"))
async def poisk1(message: types.Message):
    await message.answer(text="памагити")
    print("Памагити")
@dp.message((F.text.lower()=="/admin"))
@dp.message((F.text.lower()=="админ"))
@dp.message((F.text.lower()=="developer"))
async def poisk1(message: types.Message):
    await message.answer(text="начальник пришёл",reply_markup=klava_admina_glav)
@dp.message((F.text.lower()=="данные по платкам"))
@dp.message((F.text.lower()=="/platochna_data"))
@dp.message((F.text.lower()=="platoky_data"))
async def platoki_data(message: types.Message):
    await message.answer(text="сегмент данных о платках",reply_markup=klava_admina_platki)
@dp.message((F.text.lower()=="учебные пособия"))
@dp.message((F.text.lower()=="/education_material"))
@dp.message((F.text.lower()=="studying_devices"))
async def platoki_data(message: types.Message):
    await message.answer(text="Запрошены учебные пособия",reply_markup=klava_posobiy)
@dp.message((F.text.lower()=="выход"))
@dp.message((F.text.lower()=="/exit"))
@dp.message((F.text.lower()=="сброс"))
@dp.message((F.text.lower()=="/quit"))
async def poisk1(message: types.Message):
    await message.answer(text="выход",reply_markup=klava_privetstvije)
    print("выход")
@dp.message((F.text.lower()=="/posobija"))
@dp.message((F.text.lower()=="материалы"))
@dp.message((F.text.lower()=="пособия"))
async def poisk1(message: types.Message):
    await message.answer(text="Запрошены учебные пособия",reply_markup=klava_posobiy)
@dp.message((F.text.lower()=="/description"))
@dp.message((F.text.lower()=="о создателе бота"))
async def poisk1(message: types.Message):
    await message.answer(text="информация о создателе бота")
    print("информация о создателе бота")
@dp.message((F.text.lower()=="/start"))
@dp.message((F.text.lower()=="старт"))
@dp.message((F.text.lower()=="пуск"))
async def start_command(message: types.Message):
    await message.answer(text="Наливай,поехали!!!")
    print("Uiiiiiiiiiiiiiiiiiiiii")
@dp.message((F.text.lower()=="/stop"))
@dp.message((F.text.lower()=="авария"))
async def stop(message: types.Message):
        await message.answer("Моя остановочка")
        print("Bota ripnuli")
        raise KeyboardInterrupt
 # поисковые команды для пользователя, активация через ключевые слова
@dp.message((F.text.lower() == "автор"))
@dp.message((F.text.lower()=="/poisk_autora"))
async def poisk_autora(message: types.Message):
    global signal
    await message.answer(text="Произвожу поиск автора платка", reply_markup=ReplyKeyboardRemove())
    await message.answer(text="Назови автора платка для поиска")
    signal=32
@dp.message((F.text.lower()=="/poisk_nazvanija"))
@dp.message((F.text.lower()=="название"))
async def poisk_nazvanija(message: types.Message):
    global signal
    await message.answer(text="Произвожу поиск по названию платка")
    await message.answer(text="Назови название платка для поиска")
    signal=33
@dp.message((F.text.lower()=="/poisk_koloritov"))
@dp.message((F.text.lower()=="колориты"))
async def poisk_koloritov(message: types.Message):
    global signal
    await message.answer(text="Произвожу поиск по колориту платка, то есть по цвету узора")
    await message.answer(text="Какой цвет желаете найти?",reply_markup=klava_kolorit)
    signal = 34
@dp.message((F.text.lower()=="/poisk_cvetov"))
@dp.message((F.text.lower()=="цветы"))
@dp.message((F.text.lower()=="цветов"))
async def poisk_cvetov(message: types.Message):
    global signal
    await message.answer(text="Произвожу поиск по названию цветка, изображённого на платке")
    await message.answer(text="Какой изображённый на платке цветок хотели бы найти?")
    signal = 35
@dp.message((F.text.lower()=="/poisk_materiala"))
@dp.message((F.text.lower()=="материал платка"))
async def poisk_materiala(message: types.Message):
    global signal
    await message.answer(text="Произвожу поиск по материалу платка",reply_markup=klava_material)
    await message.answer(text="Назови желаемый материал для поиска")
    signal = 36
@dp.message((F.text.lower()=="/poisk_bahromi"))
@dp.message((F.text.lower()=="материал бахромы"))
async def poisk_bahromi(message: types.Message):
    global signal
    await message.answer(text="Произвожу поиск по материалу бахромы",reply_markup=klava_bahroma)
    await message.answer(text="""Назовите материал бахромы, который необходимо найти, если необходимо найти платки без бахромы, в строке поиска напишите 'Нет' """)
    signal = 37
@dp.message((F.text.lower()=="/poisk_razmera"))
@dp.message((F.text.lower()=="размер платка"))
async def poisk_razmera(message: types.Message):
    global signal
    await message.answer(text="Произвожу поиск по размеру платка")
    await message.answer(text="Напишите интересующий Вас размер платка")
    signal = 38
@dp.message((F.text.lower()=="/poisk_struktura_uzora"))
@dp.message((F.text.lower()=="структура орнамента"))
async def struktura_uzora(message: types.Message):
    global signal
    await message.answer(text="Произвожу поиск по структуре узора платка")
    await message.answer(text="Напишите интересующую Вас структуру узора на платке")
    signal = 39
@dp.message((F.text.lower()=="/poisk_uzora_temeni"))
@dp.message((F.text.lower()=="узор темени"))
async def uzor_temeni(message: types.Message):
    global signal
    await message.answer(text="Произвожу поиск по узору на теменной области платка")
    await message.answer(text="Напишите нужный Вам узор, изображённый на теменной области платка")
    signal = 40
@dp.message((F.text.lower()=="/poisk_uzora_cerdceviny"))
@dp.message((F.text.lower()=="узор сердцевины"))
async def uzor_temeni(message: types.Message):
    global signal
    await message.answer(text="Произвожу поиск по узору на сердцевинной области платка")
    await message.answer(text="Напишите нужный Вам узор, изображённый на сердцевинной области платка")
    signal = 41
@dp.message((F.text.lower()=="/poisk_uzora_storon"))
@dp.message((F.text.lower()=="узор сторон"))
async def uzor_temeni(message: types.Message):
    global signal
    await message.answer(text="Произвожу поиск по узору на области сторон платка")
    await message.answer(text="Напишите нужный Вам узор, изображённый на области сторон платка")
    signal = 42
@dp.message((F.text.lower()=="/poisk_uzora_uglov"))
@dp.message((F.text.lower()=="узор углов"))
async def uzor_temeni(message: types.Message):
    global signal
    await message.answer(text="Произвожу поиск по узору на области углов платка")
    await message.answer(text="Напишите нужный Вам узор, изображённый на области углов платка")
    signal = 43
@dp.message((F.text.lower()=="/poisk_uzora_krajov"))
@dp.message((F.text.lower()=="узор краёв"))
async def uzor_temeni(message: types.Message):
    global signal
    await message.answer(text="Произвожу поиск по узору на области краёв платка")
    await message.answer(text="Напишите нужный Вам узор, изображённый на области краёв платка")
    signal = 44
@dp.message((F.text.lower()=="/pusto"))
async def uzor_temeni(message: types.Message):
    global signal
    await message.answer(text="шишка-пустышка")
    asyncio.sleep(5.0)
    await message.answer(text="ХЕХЕХЕХЕХЕ")
    asyncio.sleep(5.0)
    await message.answer(text="шишка-пустышка")
    asyncio.sleep(5.0)
    await message.answer(text="ХЕХЕХЕХЕХЕ")
@dp.message((F.text.lower()=="/zapis_dannyh"))
@dp.message((F.text.lower()=="запись данных"))
async def zapis(message: types.Message):
    global id_zapisi
    global platok_infa
    global unikalnost
    global pokazatel_validacii
    global upomjanutye_platki
    await message.answer(text="Проверка наличия валидации данных")
    if pokazatel_validacii == 0:
        await message.answer(text="Данные не прошли проверку, пожалуйста, проведите проверку буфера",reply_markup=klava_admina_glav)
    await message.answer(text="Проверка целостности данных")
    if len(platok_infa) < 2:
        await message.answer(text="Данные повреждены",reply_markup=klava_admina_glav)
    elif platok_infa[1] in upomjanutye_platki:
        await message.answer(text="Такой платок уже есть", reply_markup=klava_admina_glav)
        unikalnost = 0
    else:
        await message.answer(text="Это уникальный платок, проивожу запись")
        unikalnost = 1
    if pokazatel_validacii == 1 and unikalnost == 1 and len(platok_infa) == 22:
        platok_infa[0] = int(id_zapisi)
        platocny_kartez = tuple(platok_infa)
        # импорт библиотеки для pq админ
        import psycopg2 as ps
        # создание подключения
        connection = ps.connect(host=os.getenv("DBHOST"), database=os.getenv("DBNAMEOLD"), user=os.getenv("DBUSERNAME"),
                                password=os.getenv("DBPASSWORD"),port=os.getenv("DBPORT"))
        # создание интерфейса для sql запроса
        cursor = connection.cursor()
        query = '''INSERT INTO ПППЛАТКИ
                (id, Название, Автор, Колорит_1, Колорит_2, Колорит_3, Колорит_4, Колорит_5, Узор_темени, Узор_сердцевины, Узор_сторон, Узор_углов, Узор_края, Цветы_Орнамент,
                Изображенный_Цветок_1, Изображенный_Цветок_2, Изображенный_Цветок_3, Изображенный_Цветок_4, Изображенный_Цветок_5, Размер_Платка, Материал_Платка, Материал_Бахромы)
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
        # подать запрос системе управления БД
        cursor.execute(query, platocny_kartez)
        # синхронизация изменений, комит версии
        connection.commit()
        # закрытие соединенмя с ДБ для безопасности
        cursor.close()
        connection.close()
        print('Вставка выполнена, моя Госпожа!')
        await message.answer(text='Вставка выполнена, моя Госпожа!',reply_markup=klava_admina_glav)
        id_zapisi=id_zapisi+1
        platok_infa.clear()
        unikalnost=0
        pokazatel_validacii=0
        upomjanutye_platki.clear()        
@dp.message((F.text.lower()=="/prov_dannyh"))
@dp.message((F.text.lower()=="проверка буфера"))
async def validacija(message: types.Message):
    global pokazatel_validacii
    await message.answer(text="Проверяю цельность данных")
    print("Проверяю цельность данных")
    for i in range(len(platok_infa)):
        if platok_infa[i] == None or platok_infa[i] == "":
            pokazatel_validacii=0
        else:
            pokazatel_validacii=1
    if pokazatel_validacii == 0:
        await message.answer(text="Данные повреждены")
        print("Данные повреждены")
    else:
        await message.answer(text="Данные в порядке")
        print("Данные в порядке")
@dp.message((F.text.lower() =="/smotr_dannyh"))
@dp.message((F.text.lower() =="посмотреть буфер"))
async def smotr_dannyh(message: types.Message):
    global platok_infa
    await message.answer(text="Смотр Данных")
    print("Смотр Данных")
    if len(platok_infa) == 0:
        print("Буфер пуст")
        await message.answer("Нет данных для показза, Госпожа",reply_markup=klava_admina_glav)
    else:
        for i in range(len(platok_infa)):
            soobsenie=platok_infa[i]
            await message.answer(text=f"{soobsenie}")
            print(f"{soobsenie}")
        print("Вот данные, Госпожа")
        await message.answer(text="Вот данные, Госпожа",reply_markup=klava_admina_glav)
@dp.message((F.text.lower()=="/vvod_dannyh"))
@dp.message((F.text.lower()=="ввод данных"))
async def vvod_dannyh_platka(message: types.Message):
    global signal
    global platok_infa
    await message.answer(text="Ввод данных о платке. Скажи название платка")
    print("Ввод данных платка")
    dannye="id"
    platok_infa.append(dannye)
    signal=1
@dp.message((F.text.lower()!=""))
async def vvod_nazvanija_platka(message: types.Message):
    global signal
    global platok_infa
    if message and signal==1:
        dannye1 = message.text
        platok_infa.append(dannye1)
        print(dannye1)
        await message.answer(text="Записал, назови автора платка")
        signal=2
    elif message and signal==2:
        dannye2 = message.text
        platok_infa.append(dannye2)
        print(dannye2)
        await message.answer(text="Записал, назови Колорит 1")
        signal = 3
    elif message and signal == 3:
        dannye3 = message.text
        platok_infa.append(dannye3)
        print(dannye3)
        await message.answer(text="Записал, назови Колорит 2")
        signal=4
    elif message and signal == 4:
        dannye4 = message.text
        platok_infa.append(dannye4)
        print(dannye4)
        await message.answer(text="Записал, назови Колорит 3")
        signal=5
    elif message and signal == 5:
        dannye5 = message.text
        platok_infa.append(dannye5)
        print(dannye5)
        await message.answer(text="Записал, назови Колорит 4")
        signal=6
    elif message and signal == 6:
        dannye6 = message.text
        platok_infa.append(dannye6)
        print(dannye6)
        await message.answer(text="Записал, назови Колорит 5")
        signal = 7
    elif message and signal == 7:
        dannye7 = message.text
        platok_infa.append(dannye7)
        print(dannye7)
        signal = 8
        await message.answer(text="Записал, назови Узор Темени")
    elif message and signal == 8:
        dannye8 = message.text
        platok_infa.append(dannye8)
        print(dannye8)
        signal = 9
        await message.answer(text="Записал, назови Узор Сердцевины")
    elif message and signal == 9:
        dannye9 = message.text
        platok_infa.append(dannye9)
        print(dannye9)
        signal = 10
        await message.answer(text="Записал, назови Узор Сторон")
    elif message and signal == 10:
        dannye10 = message.text
        platok_infa.append(dannye10)
        print(dannye10)
        await message.answer(text="Записал, назови Узор Углов")
        signal = 11
    elif message and signal == 11:
        dannye11 = message.text
        platok_infa.append(dannye11)
        print(dannye11)
        await message.answer(text="Записал, назови Узор Краёв")
        signal = 12
    elif message and signal == 12:
        dannye12 = message.text
        platok_infa.append(dannye12)
        print(dannye12)
        await message.answer(text="Записал,опиши соотношение цветов и орнамента")
        signal = 13
    elif message and signal == 13:
        dannye13 = message.text
        platok_infa.append(dannye13)
        print(dannye13)
        await message.answer(text="Записал, назови нарисованный цветок 1")
        signal = 14
    elif message and signal == 14:
        dannye14 = message.text
        platok_infa.append(dannye14)
        print(dannye14)
        await message.answer(text="Записал, назови нарисованный цветок 2")
        signal = 15
    elif message and signal == 15:
        dannye15 = message.text
        platok_infa.append(dannye15)
        print(dannye15)
        await message.answer(text="Записал, назови нарисованный цветок 3")
        signal = 16
    elif message and signal == 16:
        dannye16 = message.text
        platok_infa.append(dannye16)
        print(dannye16)
        await message.answer(text="Записал, назови нарисованный цветок 4")
        signal = 17
    elif message and signal == 17:
        dannye17 = message.text
        platok_infa.append(dannye17)
        print(dannye17)
        await message.answer(text="Записал, назови нарисованный цветок 5")
        signal = 18
    elif message and signal == 18:
        dannye18 = message.text
        platok_infa.append(dannye18)
        print(dannye18)
        await message.answer(text="Назови размер Платка")
        signal = 19
    elif message and signal == 19:
        dannye19 = message.text
        platok_infa.append(dannye19)
        print(dannye19)
        await message.answer(text="Назови Материал Платка")
        signal = 20
    elif message and signal == 20:
        dannye20 = message.text
        platok_infa.append(dannye20)
        print(dannye20)
        await message.answer(text="Материал Бахромы")
        signal = 21
    elif message and signal == 21:
        dannye21 = message.text
        platok_infa.append(dannye21)
        print(dannye21)
        await message.answer(text="Данные о платке записаны",reply_markup=klava_admina_glav)
        signal=0
    elif message and signal == 32:
        dannye32 =message.text
        signal=0
        # создание инте
        # password=os.getenv("DBPASSWORD"), port=os.getenv("DBPORT"))
        # создание интерфейса для sql запроса
        cursor = connection.cursor()
        zapros="SELECT * FROM ПППЛАТКИ WHERE Автор = %s ORDER BY ID ASC;"
        # отправить запрос системе управления
        cursor.execute(zapros,(dannye32,))
        row = cursor.fetchone()
        if row:
            await message.answer(text="Вот сведения по платкам данного автора")
        else:
            await message.answer(text="Такого автора нет")
        # синхронизация изменений, комит версии
        connection.commit()
        # закрытие соединенмя с ДБ для безопасности
        cursor.close()
        connection.close()
        connection = ps.connect(host=os.getenv("DBHOST"), database=os.getenv("DBNAMEOLD"), user=os.getenv("DBUSERNAME"),
                                password=os.getenv("DBPASSWORD"), port=os.getenv("DBPORT"))
        # создание интерфейса для sql запроса
        cursor = connection.cursor()
        zapros = "SELECT * FROM ПППЛАТКИ WHERE Автор = %s ORDER BY ID ASC;"
        cursor.execute(zapros, (dannye32,))
        while True:
            next_row=cursor.fetchone()
            if next_row:
                platok_dannye = []
                for i in range(len(platok_predstav)):
                    platok_rjad=platok_predstav[i]+ " " + str(next_row[i]) 
                    platok_dannye.append(platok_rjad)
                await message.answer(text=f"{platok_dannye}")
            else:
                break
        # синхронизация изменений, комит версии
        connection.commit()
        # закрытие соединенмя с ДБ для безопасности
        cursor.close()
        connection.close()
    elif message and signal == 33:
        dannye33 = message.text
        signal = 0
        # создание интерфейса для sql запроса
        import psycopg2 as ps
        connection = ps.connect(host=os.getenv("DBHOST"), database=os.getenv("DBNAMEOLD"), user=os.getenv("DBUSERNAME"),
                                password=os.getenv("DBPASSWORD"), port=os.getenv("DBPORT"))
        # создание интерфейса для sql запроса
        cursor = connection.cursor()
        zapros = "SELECT * FROM ПППЛАТКИ WHERE Название = %s ORDER BY ID ASC;"
        # отправить запрос системе управления
        cursor.execute(zapros, (dannye33,))
        row = cursor.fetchone()
        if row:
            await message.answer(text="Вот сведения по названию данного платка")
        else:
            await message.answer(text="Данного названия в базе не обнаружено")
        # синхронизация изменений, комит версии
        connection.commit()
        # закрытие соединенмя с ДБ для безопасности
        cursor.close()
        connection.close()
        connection = ps.connect(host=os.getenv("DBHOST"), database=os.getenv("DBNAMEOLD"), user=os.getenv("DBUSERNAME"),
                                password=os.getenv("DBPASSWORD"), port=os.getenv("DBPORT"))
        # создание интерфейса для sql запроса
        cursor = connection.cursor()
        zapros = "SELECT * FROM ПППЛАТКИ WHERE Название = %s ORDER BY ID ASC;"
        cursor.execute(zapros, (dannye33,))
        while True:
            next_row = cursor.fetchone()
            if next_row:
                print(f"{next_row}")
                await message.answer(text=f"{next_row}")
            else:
                break
        # синхронизация изменений, комит версии
        connection.commit()
        # закрытие соединенмя с ДБ для безопасности
        cursor.close()
        connection.close()
    elif message and signal == 34:
        dannye34 = message.text
        signal = 0
        import psycopg2 as ps
        connection = ps.connect(host=os.getenv("DBHOST"), database=os.getenv("DBNAMEOLD"), user=os.getenv("DBUSERNAME"),
                                password=os.getenv("DBPASSWORD"), port=os.getenv("DBPORT"))
        # создание интерфейса для sql запроса
        cursor = connection.cursor()
        zapros = "SELECT * FROM ПППЛАТКИ WHERE Колорит_1 = %s OR Колорит_2 = %s OR Колорит_3 = %s OR Колорит_4 = %s OR Колорит_5 = %s ORDER BY ID ASC;"
        # отправить запрос системе управления
        cursor.execute(zapros, (dannye34,dannye34,dannye34,dannye34,dannye34))
        row = cursor.fetchone()
        if row:
            await message.answer(text="Вот платки данного колорита, данной цветовой схемы узора",reply_markup=ReplyKeyboardRemove())
        else:
            await message.answer(text="Таких платков данного цвета найти не удалось",reply_markup=ReplyKeyboardRemove())
        # синхронизация изменений, комит версии
        connection.commit()
        # закрытие соединенмя с ДБ для безопасности
        cursor.close()
        connection.close()
        connection = ps.connect(host=os.getenv("DBHOST"), database=os.getenv("DBNAMEOLD"), user=os.getenv("DBUSERNAME"),
                                password=os.getenv("DBPASSWORD"), port=os.getenv("DBPORT"))
        # создание интерфейса для sql запроса
        cursor = connection.cursor()
        zapros = "SELECT * FROM ПППЛАТКИ WHERE Колорит_1 = %s OR Колорит_2 = %s OR Колорит_3 = %s OR Колорит_4 = %s OR Колорит_5 = %s ORDER BY ID ASC;"
        cursor.execute(zapros, (dannye34,dannye34,dannye34,dannye34,dannye34))
        while True:
            next_row = cursor.fetchone()
            if next_row:
                print(f"{next_row}")
                await message.answer(text=f"{next_row}")
            else:
                break
        # синхронизация изменений, комит версии
        connection.commit()
        # закрытие соединенмя с ДБ для безопасности
        cursor.close()
        connection.close()
    elif message and signal == 35:
        dannye35 = message.text
        signal = 0
        import psycopg2 as ps
        connection = ps.connect(host=os.getenv("DBHOST"), database=os.getenv("DBNAMEOLD"),
                                user=os.getenv("DBUSERNAME"), password=os.getenv("DBPASSWORD"),port=os.getenv("DBPORT"))
        # создание интерфейса для sql запроса
        cursor = connection.cursor()
        zapros = "SELECT * FROM ПППЛАТКИ WHERE Изображенный_Цветок_1 = %s OR Изображенный_Цветок_2 = %s OR Изображенный_Цветок_3 = %s OR Изображенный_Цветок_4 = %s OR Изображенный_Цветок_5 = %s ORDER BY ID ASC;"
        # отправить запрос системе управления
        cursor.execute(zapros, (dannye35,dannye35,dannye35,dannye35,dannye35))
        row = cursor.fetchone()
        if row:
            await message.answer(text="Вот все названия платков, на которых встречается данный цветов")
        else:
            await message.answer(text="Не удалось найти название платков, на которых встречается упоминаемый Вами цветок")
        # синхронизация изменений, комит версии
        connection.commit()
        # закрытие соединенмя с ДБ для безопасности
        cursor.close()
        connection.close()
        connection = ps.connect(host=os.getenv("DBHOST"), database=os.getenv("DBNAMEOLD"), user=os.getenv("DBUSERNAME"),
                                password=os.getenv("DBPASSWORD"),port=os.getenv("DBPORT"))
        # создание интерфейса для sql запроса
        cursor = connection.cursor()
        zapros = "SELECT * FROM ПППЛАТКИ WHERE Изображенный_Цветок_1 = %s OR Изображенный_Цветок_2 = %s OR Изображенный_Цветок_3 = %s OR Изображенный_Цветок_4 = %s OR Изображенный_Цветок_5 = %s ORDER BY ID ASC;"
        cursor.execute(zapros, (dannye35,dannye35,dannye35,dannye35,dannye35))
        while True:
            next_row = cursor.fetchone()
            if next_row:
                print(f"{next_row}")
                await message.answer(text=f"{next_row}")
            else:
                break
        # синхронизация изменений, комит версии
        connection.commit()
        # закрытие соединенмя с ДБ для безопасности
        cursor.close()
        connection.close()
    elif message and signal == 36:
        dannye36 = message.text
        signal = 0
        # создание интерфейса для sql запроса
        import psycopg2 as ps
        connection = ps.connect(host=os.getenv("DBHOST"), database=os.getenv("DBNAMEOLD"), user=os.getenv("DBUSERNAME"),
                                password=os.getenv("DBPASSWORD"), port=os.getenv("DBPORT"))
        # создание интерфейса для sql запроса
        cursor = connection.cursor()
        zapros = "SELECT * FROM ПППЛАТКИ WHERE Материал_Платка = %s ORDER BY ID ASC;"
        # отправить запрос системе управления
        cursor.execute(zapros, (dannye36,))
        row = cursor.fetchone()
        if row:
            await message.answer(text="Вот сведения по платкам, изготовленных из данного материала",reply_markup=ReplyKeyboardRemove())
        else:
            await message.answer(text="Не нашлось платков, изготовленных из данного материала",reply_markup=ReplyKeyboardRemove())
        # синхронизация изменений, комит версии
        connection.commit()
        # закрытие соединенмя с ДБ для безопасности
        cursor.close()
        connection.close()
        connection = ps.connect(host=os.getenv("DBHOST"), database=os.getenv("DBNAMEOLD"), user=os.getenv("DBUSERNAME"),
                                password=os.getenv("DBPASSWORD"), port=os.getenv("DBPORT"))
        # создание интерфейса для sql запроса
        cursor = connection.cursor()
        zapros = "SELECT * FROM ПППЛАТКИ WHERE Материал_Платка = %s ORDER BY ID ASC;"
        cursor.execute(zapros, (dannye36,))
        while True:
            next_row = cursor.fetchone()
            if next_row:
                print(f"{next_row}")
                await message.answer(text=f"{next_row}")
            else:
                break
        # синхронизация изменений, комит версии
        connection.commit()
        # закрытие соединенмя с ДБ для безопасности
        cursor.close()
        connection.close()
    elif message and signal == 37:
        dannye37 =message.text
        signal=0
        # создание интерфейса для sql запроса
        import psycopg2 as ps
        connection = ps.connect(host=os.getenv("DBHOST"), database=os.getenv("DBNAMEOLD"), user=os.getenv("DBUSERNAME"),
                                password=os.getenv("DBPASSWORD"), port=os.getenv("DBPORT"))
        #создание интерфейса для sql запроса
        cursor = connection.cursor()
        zapros="SELECT * FROM ПППЛАТКИ WHERE Материал_Бахромы = %s ORDER BY ID ASC;"
        # отправить запрос системе управления
        cursor.execute(zapros,(dannye37,))
        row = cursor.fetchone()
        if row:
            await message.answer(text="Вот название платков с бахромой из данного материала",reply_markup=ReplyKeyboardRemove())
        else:
            await message.answer(text="Платков с бахромой из данного материала не найдено",reply_markup=ReplyKeyboardRemove())
        # синхронизация изменений, комит версии
        connection.commit()
        # закрытие соединенмя с ДБ для безопасности
        cursor.close()
        connection.close()
        connection = ps.connect(host=os.getenv("DBHOST"), database=os.getenv("DBNAMEOLD"), user=os.getenv("DBUSERNAME"),
                                password=os.getenv("DBPASSWORD"),port=os.getenv("DBPORT"))
        # создание интерфейса для sql запроса
        cursor = connection.cursor()
        zapros = "SELECT * FROM ПППЛАТКИ WHERE Материал_Бахромы = %s ORDER BY ID ASC;"
        cursor.execute(zapros, (dannye37,))
        while True:
            next_row=cursor.fetchone()
            if next_row:
                print(f"{next_row}")
                await message.answer(text=f"{next_row}")
            else:
                break
        # синхронизация изменений, комит версии
        connection.commit()
        # закрытие соединенмя с ДБ для безопасности
        cursor.close()
        connection.close()
    elif message and signal == 38:
        dannye38 =message.text
        signal=0
        # создание интерфейса для sql запроса
        import psycopg2 as ps
        connection = ps.connect(host=os.getenv("DBHOST"), database=os.getenv("DBNAMEOLD"), user=os.getenv("DBUSERNAME"),
                                password=os.getenv("DBPASSWORD"), port=os.getenv("DBPORT"))
        #создание интерфейса для sql запроса
        cursor = connection.cursor()
        zapros="SELECT * FROM ПППЛАТКИ WHERE Размер_Платка = %s ORDER BY ID ASC;"
        # отправить запрос системе управления
        cursor.execute(zapros,(dannye38,))
        row = cursor.fetchone()
        if row:
            await message.answer(text="Вот названия платков данного размера")
        else:
            await message.answer(text="Платков данного размера не найдено")
        # синхронизация изменений, комит версии
        connection.commit()
        # закрытие соединенмя с ДБ для безопасности
        cursor.close()
        connection.close()
        connection = ps.connect(host=os.getenv("DBHOST"), database=os.getenv("DBNAMEOLD"), user=os.getenv("DBUSERNAME"),
                                password=os.getenv("DBPASSWORD"), port=os.getenv("DBPORT"))
        # создание интерфейса для sql запроса
        cursor = connection.cursor()
        zapros = "SELECT * FROM ПППЛАТКИ WHERE Размер_Платка = %s ORDER BY ID ASC;"
        cursor.execute(zapros, (dannye38,))
        while True:
            next_row=cursor.fetchone()
            if next_row:
                print(f"{next_row}")
                await message.answer(text=f"{next_row}")
            else:
                break
        # синхронизация изменений, комит версии
        connection.commit()
        # закрытие соединенмя с ДБ для безопасности
        cursor.close()
        connection.close()
    elif message and signal == 39:
        dannye39 =message.text
        signal=0
        # создание интерфейса для sql запроса
        import psycopg2 as ps
        connection = ps.connect(host=os.getenv("DBHOST"), database=os.getenv("DBNAMEOLD"), user=os.getenv("DBUSERNAME"),
                                password=os.getenv("DBPASSWORD"), port=os.getenv("DBPORT"))
        #создание интерфейса для sql запроса
        cursor = connection.cursor()
        zapros="SELECT * FROM ПППЛАТКИ WHERE Цветы_Орнамент = %s ORDER BY ID ASC;"
        # отправить запрос системе управления
        cursor.execute(zapros,(dannye39,))
        row = cursor.fetchone()
        if row:
            await message.answer(text="Вот названия платков по заданной структуре орнамента на платке")
        else:
            await message.answer(text="Платков с данной структурой орнамента не обнаружено")
        # синхронизация изменений, комит версии
        connection.commit()
        # закрытие соединенмя с ДБ для безопасности
        cursor.close()
        connection.close()
        connection = ps.connect(host=os.getenv("DBHOST"), database=os.getenv("DBNAMEOLD"), user=os.getenv("DBUSERNAME"),
                                password=os.getenv("DBPASSWORD"), port=os.getenv("DBPORT"))
        # создание интерфейса для sql запроса
        cursor = connection.cursor()
        zapros = "SELECT * FROM ПППЛАТКИ WHERE Цветы_Орнамент = %s ORDER BY ID ASC;"
        cursor.execute(zapros, (dannye39,))
        while True:
            next_row=cursor.fetchone()
            if next_row:
                print(f"{next_row}")
                await message.answer(text=f"{next_row}")
            else:
                break
        # синхронизация изменений, комит версии
        connection.commit()
        # закрытие соединенмя с ДБ для безопасности
        cursor.close()
        connection.close()
    elif message and signal == 40:
        dannye40 =message.text
        signal=0
        # создание интерфейса для sql запроса
        import psycopg2 as ps
        connection = ps.connect(host=os.getenv("DBHOST"), database=os.getenv("DBNAMEOLD"), user=os.getenv("DBUSERNAME"),
                                password=os.getenv("DBPASSWORD"), port=os.getenv("DBPORT"))
        #создание интерфейса для sql запроса
        cursor = connection.cursor()
        zapros="SELECT * FROM ПППЛАТКИ WHERE Узор_темени = %s ORDER BY ID ASC;"
        # отправить запрос системе управления
        cursor.execute(zapros,(dannye40,))
        row = cursor.fetchone()
        if row:
            await message.answer(text="Вот названия платков с данным рисунком на теменной области")
        else:
            await message.answer(text="Платков с данным рисунком на теменной области не обнаружено")
        # синхронизация изменений, комит версии
        connection.commit()
        # закрытие соединенмя с ДБ для безопасности
        cursor.close()
        connection.close()
        connection = ps.connect(host=os.getenv("DBHOST"), database=os.getenv("DBNAMEOLD"), user=os.getenv("DBUSERNAME"),
                                password=os.getenv("DBPASSWORD"), port=os.getenv("DBPORT"))
        cursor = connection.cursor()
        zapros = "SELECT * FROM ПППЛАТКИ WHERE Узор_темени = %s ORDER BY ID ASC;"
        cursor.execute(zapros, (dannye40,))
        while True:
        # создание интерфейса для sql запроса
            next_row=cursor.fetchone()
            if next_row:
                print(f"{next_row}")
                await message.answer(text=f"{next_row}")
            else:
                break
        # синхронизация изменений, комит версии
        connection.commit()
        # закрытие соединенмя с ДБ для безопасности
        cursor.close()
        connection.close()
    elif message and signal == 41:
        dannye40 =message.text
        signal=0
        # создание интерфейса для sql запроса
        import psycopg2 as ps
        connection = ps.connect(host=os.getenv("DBHOST"), database=os.getenv("DBNAMEOLD"), user=os.getenv("DBUSERNAME"),
                                password=os.getenv("DBPASSWORD"), port=os.getenv("DBPORT"))
        #создание интерфейса для sql запроса
        cursor = connection.cursor()
        zapros="SELECT * FROM ПППЛАТКИ WHERE Узор_сердцевины = %s ORDER BY ID ASC;"
        # отправить запрос системе управления
        cursor.execute(zapros,(dannye40,))
        row = cursor.fetchone()
        if row:
            await message.answer(text="Вот названия платков с данным рисунком на сердцевинной области")
        else:
            await message.answer(text="Платков с данным рисунком на сердцевинной области не обнаружено")
        # синхронизация изменений, комит версии
        connection.commit()
        # закрытие соединенмя с ДБ для безопасности
        cursor.close()
        connection.close()
        connection = ps.connect(host=os.getenv("DBHOST"), database=os.getenv("DBNAMEOLD"), user=os.getenv("DBUSERNAME"),
                                password=os.getenv("DBPASSWORD"), port=os.getenv("DBPORT"))
        # 123 создание интерфейса для sql запроса
        cursor = connection.cursor()
        zapros = "SELECT * FROM ПППЛАТКИ WHERE Узор_сердцевины = %s ORDER BY ID ASC;"
        cursor.execute(zapros, (dannye40,))
        while True:
            next_row=cursor.fetchone()
            if next_row:
                print(f"{next_row}")
                await message.answer(text=f"{next_row}")
            else:
                break
    elif message and signal == 41:
        dannye41 = message.text
        signal = 0
        # создание интерфейса для sql запроса
        import psycopg2 as ps
        connection = ps.connect(host=os.getenv("DBHOST"), database=os.getenv("DBNAMEOLD"), user=os.getenv("DBUSERNAME"),
                                password=os.getenv("DBPASSWORD"), port=os.getenv("DBPORT"))
        # создание интерфейса для sql запроса
        cursor = connection.cursor()
        zapros = "SELECT * FROM ПППЛАТКИ WHERE Узор_сторон = %s ORDER BY ID ASC;"
        # отправить запрос системе управления
        cursor.execute(zapros, (dannye41,))
        row = cursor.fetchone()
        if row:
            await message.answer(text="Вот названия платков с данным рисунком на области сторон")
        else:
            await message.answer(text="Платков с данным рисунком на области сторон не обнаружено")
        # синхронизация изменений, комит версии
        connection.commit()
        # закрытие соединенмя с ДБ для безопасности
        cursor.close()
        connection.close()
        connection = ps.connect(host=os.getenv("DBHOST"), database=os.getenv("DBNAMEOLD"), user=os.getenv("DBUSERNAME"),
                                password=os.getenv("DBPASSWORD"), port=os.getenv("DBPORT"))
        # создание интерфейса для sql запроса
        cursor = connection.cursor()
        zapros = "SELECT * FROM ПППЛАТКИ WHERE Узор_сторон = %s ORDER BY ID ASC;"
        cursor.execute(zapros, (dannye41,))
        while True:
            next_row = cursor.fetchone()
            if next_row:
                print(f"{next_row}")
                await message.answer(text=f"{next_row}")
            else:
                break
        # синхронизация изменений, комит версии
        connection.commit()
        # закрытие соединенмя с ДБ для безопасности
        cursor.close()
        connection.close()
    elif message and signal == 42:
        dannye42 = message.text
        signal = 0
        # создание интерфейса для sql запроса
        import psycopg2 as ps
        connection = ps.connect(host=os.getenv("DBHOST"), database=os.getenv("DBNAMEOLD"), user=os.getenv("DBUSERNAME"),
                                password=os.getenv("DBPASSWORD"), port=os.getenv("DBPORT"))
        # создание интерфейса для sql запроса
        cursor = connection.cursor()
        zapros = "SELECT * FROM ПППЛАТКИ WHERE Узор_углов = %s ORDER BY ID ASC;"
        # отправить запрос системе управления
        cursor.execute(zapros, (dannye42,))
        row = cursor.fetchone()
        if row:
            await message.answer(text="Вот названия платков с данным рисунком области углов платка")
        else:
            await message.answer(text="Платков с данным рисунком на области углов платка не обнаружено")
        # синхронизация изменений, комит версии
        connection.commit()
        # закрытие соединенмя с ДБ для безопасности
        cursor.close()
        connection.close()
        connection = ps.connect(host=os.getenv("DBHOST"), database=os.getenv("DBNAMEOLD"), user=os.getenv("DBUSERNAME"),
                                password=os.getenv("DBPASSWORD"), port=os.getenv("DBPORT"))
        # создание интерфейса для sql запроса
        cursor = connection.cursor()
        zapros = "SELECT * FROM ПППЛАТКИ WHERE Узор_углов = %s ORDER BY ID ASC;"
        cursor.execute(zapros, (dannye42,))
        while True:
            next_row = cursor.fetchone()
            if next_row:
                print(f"{next_row}")
                await message.answer(text=f"{next_row}")
            else:
                break
        # синхронизация изменений, комит версии
        connection.commit()
        # закрытие соединенмя с ДБ для безопасности
        cursor.close()
        connection.close()
    elif message and signal == 44:
        dannye43 = message.text
        signal = 0
        # создание интерфейса для sql запроса
        import psycopg2 as ps
        connection = ps.connect(host=os.getenv("DBHOST"), database=os.getenv("DBNAMEOLD"), user=os.getenv("DBUSERNAME"),
                                password=os.getenv("DBPASSWORD"), port=os.getenv("DBPORT"))
        # создание интерфейса для sql запроса
        cursor = connection.cursor()
        zapros = "SELECT * FROM ПППЛАТКИ WHERE Узор_края = %s ORDER BY ID ASC;"
        # отправить запрос системе управления
        cursor.execute(zapros, (dannye43,))
        row = cursor.fetchone()
        if row:
            await message.answer(text="Вот названия платков с данным рисунком области края платка")
        else:
            await message.answer(text="Платков с данным рисунком на области углов платка не обнаружено")
        # синхронизация изменений, комит версии
        connection.commit()
        # закрытие соединенмя с ДБ для безопасности
        cursor.close()
        connection.close()
        connection = ps.connect(host=os.getenv("DBHOST"), database=os.getenv("DBNAMEOLD"), user=os.getenv("DBUSERNAME"),
                                password=os.getenv("DBPASSWORD"), port=os.getenv("DBPORT"))
        # создание интерфейса для sql запроса
        cursor = connection.cursor()
        zapros = "SELECT * FROM ПППЛАТКИ WHERE Узор_края = %s ORDER BY ID ASC;"
        cursor.execute(zapros, (dannye43,))
        while True:
            next_row = cursor.fetchone()
            if next_row:
                print(f"{next_row}")
                await message.answer(text=f"{next_row}")
            else:
                break
        # синхронизация изменений, комит версии
        connection.commit()
        # закрытие соединенмя с ДБ для безопасности
        cursor.close()
        connection.close()
async def kostily_BD(bot:Bot):
    # создать ДБ
    import psycopg2 as ps
    from psycopg2.errors import DuplicateDatabase as Oshibka
    from psycopg2 import sql
    connection = None
    try:
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        print(Back.GREEN + Fore.BLACK + Style.BRIGHT + 'Создать базу Данных')
        databasename = os.getenv('DATABASENAME')
        connection = ps.connect(host=os.getenv("DBHOST"), database=os.getenv("DBNAMEOLD"), user=os.getenv("DBUSERNAME"),
                                password=os.getenv("DBPASSWORD"), port=os.getenv("DBPORT"))
        connection.autocommit = True
        cursor = connection.cursor()
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(databasename)))
        cursor.close()
        print(Back.LIGHTGREEN_EX + Fore.BLACK + Style.BRIGHT + 'БД успешно создана, моя Госпожа')
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        await Bot.send_message(chat_id=os.getenv('MYUSERID'), text="Готова, мой Господин!")
        await bot.send_photo(chat_id=os.getenv('MYUSERID'), photo=os.getenv('AVATARPHOTOID'))
        #await bot.send_message(chat_id=os.getenv('MYUSERID'), text='БД успешно создана, моя Госпожа')
        #await bot.send_message(chat_id=os.getenv('MYUSERID'), text='БД запущена, моя Госпожа!!!')
    except Oshibka:
        print(Back.LIGHTYELLOW_EX + Fore.BLACK + Style.BRIGHT + 'Такая БД уже есть, моя Госпожа!!!')
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        await bot.send_message(chat_id=os.getenv('MYUSERID'), text='БД уже есть, моя Госпожа!!!')
        await bot.send_message(chat_id=os.getenv('MYUSERID'), text='БД запущена, моя Госпожа!!!',reply_markup=klava_privetstvije)
        await bot.send_photo(chat_id=os.getenv('MYUSERID'),photo=os.getenv('AVATARPHOTOID'))
    finally:
        if connection:
            connection.close()
async def on_startup(bot:Bot):
    await Bot.send_message(chat_id=os.getenv('MYUSERID'), text="Готова, мой Господин!",reply_markup=klava_privetstvije)
    await bot.send_photo(chat_id=os.getenv('MYUSERID'), photo=os.getenv('AVATARPHOTOID'))
    #await kostily_BD(Bot)
    await create_platky()
#БЕЗ ЗАЙЦА
#async def main():
    #async with broker:
        #await broker.start()
        #init(autoreset=True)
        #dp.startup.register(on_startup)
        #await Bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
        #await Bot.delete_webhook(drop_pending_updates=True)
        #await dp.start_polling(Bot)
async def main():    
        init(autoreset=True)
        dp.startup.register(on_startup)
        await Bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
        await Bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(Bot)
if __name__ == "__main__":
    #aasyncio.run(uvicorn.run("bot:app", reload=True, port=8000))
    asyncio.run(main())
    #asyncio.create_task(main())
    #asyncio.create_task()
    #asyncio.create_task(main())
#pip install -r .\\.venv\requirements.txt
#C:\Users\Fevronija\PycharmProjects\PuhovikovyBot\.venv\Scripts\python.exe C:\Users\Fevronija\PycharmProjects\PuhovikovyBot\.venv\bot.py