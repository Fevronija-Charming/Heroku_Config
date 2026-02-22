from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
klava_privetstvije=ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="поиск по техническим харак.")],
    [KeyboardButton(text="поиск по худож. харак.")],
    [KeyboardButton(text="значение символов на платке")],
    [KeyboardButton(text="о создателе Февронии")],
    [KeyboardButton(text="учебные пособия по платкам")],
    [KeyboardButton(text="участники платочной банды")],
    [KeyboardButton(text="жалобная книга")],
    [KeyboardButton(text="выход")]],
    resize_keyboard=True,input_field_placeholder="Что хотите сделать, мой Господин?")
klava_poisk1=ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="автор"),KeyboardButton(text="название"), KeyboardButton(text="размер платка")],
    [KeyboardButton(text="материал платка"),KeyboardButton(text="материал бахромы"),KeyboardButton(text="колориты")],
    [KeyboardButton(text="выход")]],
    resize_keyboard=True,input_field_placeholder="Выберите критерий поиска")
klava_poisk2=ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="структура орнамента"),KeyboardButton(text="теменной узор"), KeyboardButton(text="узор сердцевины")],
    [KeyboardButton(text="узор сторон"),KeyboardButton(text="узор углов"),KeyboardButton(text="узор краёв")],
    [KeyboardButton(text="выход")]],
    resize_keyboard=True,input_field_placeholder="Выберите критерий поиска")
klava_kolorit=ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Жёлтый"),KeyboardButton(text="Бирюзовый"), KeyboardButton(text="Кремовый")],
    [KeyboardButton(text="Оранжевый"),KeyboardButton(text="Зелёный"),KeyboardButton(text="Белый")],
    [KeyboardButton(text="Красный"),KeyboardButton(text="Синий"),KeyboardButton(text="Чёрный")],
    [KeyboardButton(text="Розовый"),KeyboardButton(text="Голубой"),KeyboardButton(text="Серый")],
    [KeyboardButton(text="Бордовый"),KeyboardButton(text="Фиолетовый"),KeyboardButton(text="Коричневый")],
    [KeyboardButton(text="выход"),KeyboardButton(text="Лунный")]],
    resize_keyboard=True,input_field_placeholder="Выберите цвет платка")
klava_posobiy=ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Традиции ношения")],
    [KeyboardButton(text="Обзор платочных мануфактур")],
    [KeyboardButton(text="Композиция и структура узора")],
    [KeyboardButton(text="Значение основных символов на платке")],
    [KeyboardButton(text="Классификация колоритов платка")],
    [KeyboardButton(text="выход")]],
    resize_keyboard=True,input_field_placeholder="Выберите материал урока, с которым хотите ознакомится")
klava_material=ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Шерсть_Мериноса"),KeyboardButton(text="Шёлк")],
    [KeyboardButton(text="Крепдешин"),KeyboardButton(text="Вискоза")],
    [KeyboardButton(text="другое"),KeyboardButton(text="выход")]],
    resize_keyboard=True,input_field_placeholder="Желаемый материал")
klava_bahroma=ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Шерсть"),KeyboardButton(text="Шёлк")],
    [KeyboardButton(text="Нет"),KeyboardButton(text="выход")]],
    resize_keyboard=True,input_field_placeholder="Желаемый материал")
klava_admina_glav=ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="учебные пособия")],
    [KeyboardButton(text="данные по платкам")],
    [KeyboardButton(text="скормить_фото")],
    [KeyboardButton(text="значение_символов на платке")],
    [KeyboardButton(text="традиции_ношения")],
    [KeyboardButton(text="выход")]],
    resize_keyboard=True,input_field_placeholder="С каким сегментом хотите поработать?")
klava_admina_materialy=ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="ввести запись об уроке в буфер")],
    [KeyboardButton(text="проверить запись об уроке буфере")],
    [KeyboardButton(text="очистить запись об уроке")],
    [KeyboardButton(text="зарегестрировать запись в БД")],
    [KeyboardButton(text="внести исправление в запись урока")],
    [KeyboardButton(text="посмотреть запись об уроке")],
    [KeyboardButton(text="выход")]],
    resize_keyboard=True,input_field_placeholder="С каким сегментом хотите поработать?")
klava_admina_platki=ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="ввод данных"),KeyboardButton(text="посмотреть буфер")],
    [KeyboardButton(text="запись данных"),KeyboardButton(text="удаление строки")],
    [KeyboardButton(text="проверка буфера"),KeyboardButton(text="выход")]],
    resize_keyboard=True,input_field_placeholder="Что хотите сделать?")
klava_admina_uroki=ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="ввод данных"),KeyboardButton(text="посмотреть буфер")],
    [KeyboardButton(text="запись данных"),KeyboardButton(text="удаление строки")],
    [KeyboardButton(text="проверка буфера"),KeyboardButton(text="выход")]],
    resize_keyboard=True,input_field_placeholder="Что хотите сделать?")
klava_symboly=ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="КВАДРАТ")],
    [KeyboardButton(text="РОМБ")],
    [KeyboardButton(text="ВОСЬМИУГОЛЬНИК")],
    [KeyboardButton(text="КРУГ")],
    [KeyboardButton(text="ДРУГИЕ СИМВОЛЫ")],
    [KeyboardButton(text="выход")]],
    resize_keyboard=True,input_field_placeholder="Значение какого символа хотите узнать")
