from sqlalchemy import DateTime, String, Float, Column, Integer, func, Text, BIGINT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
class Base(DeclarativeBase):
    pass
class Platoky(Base):
    __tablename__="ПППЛАТКИ"
    id: Mapped[int]=mapped_column(primary_key=True, autoincrement=True, nullable=False)
    Название: Mapped[str]=mapped_column(String(128), nullable=False)
    Автор: Mapped[str]=mapped_column(String(128), nullable=False)
    Колорит_1: Mapped[str]=mapped_column(String(128), nullable=False)
    Колорит_2: Mapped[str] = mapped_column(String(128), nullable=False)
    Колорит_3: Mapped[str] = mapped_column(String(128), nullable=False)
    Колорит_4: Mapped[str] = mapped_column(String(128), nullable=False)
    Колорит_5: Mapped[str] = mapped_column(String(128), nullable=False)
    Узор_темени: Mapped[str] = mapped_column(String(128), nullable=False)
    Узор_сердцевины: Mapped[str] = mapped_column(String(128), nullable=False)
    Узор_сторон: Mapped[str] = mapped_column(String(128), nullable=False)
    Узор_углов: Mapped[str] = mapped_column(String(128), nullable=False)
    Узор_края: Mapped[str] = mapped_column(String(128), nullable=False)
    Цветы_Орнамент: Mapped[str] = mapped_column(String(128), nullable=False)
    Изображенный_Цветок_1: Mapped[str] = mapped_column(String(128), nullable=False)
    Изображенный_Цветок_2: Mapped[str] = mapped_column(String(128), nullable=False)
    Изображенный_Цветок_3: Mapped[str] = mapped_column(String(128), nullable=False)
    Изображенный_Цветок_4: Mapped[str] = mapped_column(String(128), nullable=False)
    Изображенный_Цветок_5: Mapped[str] = mapped_column(String(128), nullable=False)
    Размер_Платка: Mapped[str]=mapped_column(String(128), nullable=False)
    Материал_Платка: Mapped[str]=mapped_column(String(128), nullable=False)
    Материал_Бахромы: Mapped[str]=mapped_column(String(128), nullable=False)
    # для проверки '''INSERT INTO ПППЛАТКИ (id, Название, Автор, Колорит_1, Колорит_2, Колорит_3,
    # Колорит_4, Колорит_5, Узор_темени, Узор_сердцевины, Узор_сторон, Узор_углов, Узор_края,
    # Цветы_Орнамент, Изображенный_Цветок_1, Изображенный_Цветок_2, Изображенный_Цветок_3,
    # Изображенный_Цветок_4, Изображенный_Цветок_5, Размер_Платка, Материал_Платка, Материал_Бахромы)'''
class Tradicii(Base):
    __tablename__="ТРАДИЦИИ_НОШЕНИЯ"
    id: Mapped[int]=mapped_column(primary_key=True, nullable=False)
    Название_традиции_1: Mapped[str]=mapped_column(String(128), nullable=False)
    Название_традиции_2: Mapped[str]=mapped_column(String(128), nullable=False)
    Название_традиции_3: Mapped[str]=mapped_column(String(128), nullable=False)
    Фото_ссылка_1: Mapped[str] = mapped_column(String(128), nullable=False)
    Фото_ссылка_2: Mapped[str] = mapped_column(String(128), nullable=False)
    Фото_ссылка_3: Mapped[str] = mapped_column(String(128), nullable=False)
    Фото_ссылка_4: Mapped[str] = mapped_column(String(128), nullable=False)
    Фото_ссылка_5: Mapped[str] = mapped_column(String(128), nullable=False)
    Описание_этническое: Mapped[str] = mapped_column(Text, nullable=False)
    Описание_техническое: Mapped[str] = mapped_column(Text, nullable=False)
    Видео_ссылка_1: Mapped[str] = mapped_column(String(128), nullable=False)
    Видео_ссылка_2: Mapped[str] = mapped_column(String(128), nullable=False)
    Сфера_применения_1: Mapped[str] = mapped_column(String(128), nullable=False)
    Сфера_применения_2: Mapped[str] = mapped_column(String(128), nullable=False)
    Форма_платка_при_одевании_1: Mapped[str] = mapped_column(String(128), nullable=False)
    Форма_платка_при_одевании_2: Mapped[str] = mapped_column(String(128), nullable=False)
    Способ_закрепления_платка_1: Mapped[str] = mapped_column(String(128), nullable=False)
    Способ_закрепления_платка_2: Mapped[str] = mapped_column(String(128), nullable=False)
    Этническая_классификация: Mapped[str] = mapped_column(String(128), nullable=False)
    Географическое_распространение: Mapped[str] = mapped_column(Text, nullable=False)
class Banda(Base):
    __tablename__="Платочная_Банда"
    id: Mapped[int]=mapped_column(primary_key=True, autoincrement=True, nullable=False)
    Гражданское_Имя: Mapped[str]=mapped_column(String(128), nullable=False)
    Творческий_Псевдоним: Mapped[str]=mapped_column(String(128), nullable=False)
    Описание_Творческой_Деятельности: Mapped[str]=mapped_column(Text, nullable=False)
    Связь_Творчества_С_Павлопосадскими_Платками: Mapped[str] = mapped_column(Text, nullable=False)
    Ссылка_На_Инстаграм: Mapped[str] = mapped_column(String(128), nullable=False)
    Ссылка_На_ВК: Mapped[str] = mapped_column(String(128), nullable=False)
    Ссылка_На_Ютуб: Mapped[str] = mapped_column(String(128), nullable=False)
    Ссылка_На_Фейсбук: Mapped[str] = mapped_column(String(128), nullable=False)
    Ссылка_На_Телеграм: Mapped[str] = mapped_column(String(128), nullable=False)
    Ссылка_На_Одноклассники: Mapped[str] = mapped_column(String(128), nullable=False)
    Ссылка_На_Яндекс_Дзен: Mapped[str] = mapped_column(String(128), nullable=False)
    Ссылка_На_Сайт: Mapped[str] = mapped_column(String(128), nullable=False)
    Адрес_Деятельности: Mapped[str] = mapped_column(String(128), nullable=False)
class Symboly(Base):
    __tablename__="Значение_Символов_Орнамента"
    id: Mapped[int]=mapped_column(primary_key=True, autoincrement=True, nullable=False)
    Название_Символа: Mapped[str]=mapped_column(String(32), nullable=False)
    Значение_Символа: Mapped[str]=mapped_column(Text, nullable=False)
    Встречается_На_Платках: Mapped[str]=mapped_column(Text, nullable=False)
    Ассоциативная_Иллюстрация_1: Mapped[str] = mapped_column(String(128), nullable=False)
    Ассоциативная_Иллюстрация_2: Mapped[str] = mapped_column(String(128), nullable=False)
    Символ_На_Платке_1: Mapped[str] = mapped_column(String(128), nullable=False)
    Символ_На_Платке_2: Mapped[str] = mapped_column(String(128), nullable=False)
    Символ_На_Платке_3: Mapped[str] = mapped_column(String(128), nullable=False)
    Символ_На_Платке_4: Mapped[str] = mapped_column(String(128), nullable=False)
    Символ_На_Платке_5: Mapped[str] = mapped_column(String(128), nullable=False)
class Otzyvy(Base):
    __tablename__ = "Книга_Отзывов"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, nullable=False)
    Индефикатор_Автора: Mapped[BIGINT] = mapped_column(BIGINT,nullable=False)
    Автор_Отзыва: Mapped[str] = mapped_column(String(128), nullable=False)
    Текст_Отзыва: Mapped[str]=mapped_column(Text, nullable=False)
    Время_Записи_Отзыва: Mapped[str] = mapped_column(nullable=False)
    Секунды_Записи_Отзыва: Mapped[int] = mapped_column(nullable=False)