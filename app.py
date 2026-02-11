import streamlit as st
from docxtpl import DocxTemplate
from datetime import datetime
import io
import os

st.set_page_config(page_title="Генератор договора", layout="wide")
st.title("Генератор договора")

# Создание формы
col1 = st.columns(1)[0]

with col1:
    contractnum = st.text_input(
        "1) Номер договора (1765):",
        placeholder="1765",
        key="contractnum",
    )

    datezakl = st.text_input(
        "2) Дата договора (22.10.2025):",
        placeholder="22.10.2025",
        key="datezakl",
    )

    fio = st.text_input(
        "3) ФИО:",
        placeholder="Парфенов Илья Алексеевич",
        key="fio",
    )

    datarod = st.text_input(
        "4) Дата рождения (25.05.2000):",
        placeholder="25.05.2000",
        key="datarod",
    )

    passport = st.text_input(
        "5) Паспорт (45 04 123456):",
        placeholder="45 04 123456",
        key="passport",
    )

    summa = st.selectbox(
        "6) Стоимость услуг:",
        options=[
            ("Выберите сумму", 0),
            ("180 000 ₽ (1 мес по 180 000 ₽)", 180000),
            ("200 000 ₽ (8 мес по 25 000 ₽)", 200000),
            ("240 000 ₽ (12 мес по 20 000 ₽)", 240000),
            ("270 000 ₽ (18 мес по 15 000 ₽)", 270000),
        ],
        format_func=lambda x: x[0],
        key="summa",
    )[1]

    adres = st.text_input(
        "7) Адрес (г. Санкт-Петербург, ул. Затшига, д. 50, кв. 50):",
        placeholder="г. Санкт-Петербург, ул. Затшига, д. 50, кв. 50",
        key="adres",
    )

    phone = st.text_input(
        "8) Телефон (+7 901 943 53 21):",
        placeholder="+79019435321",
        key="phone",
    )

    if st.button("Скачать .docx", type="primary"):
        # Проверка всех полей
        if not all([contractnum, datezakl, fio, datarod, passport, summa, adres, phone]):
            st.error("Пожалуйста, заполните все поля!")
        else:
            try:
                contractnum = contractnum.replace(" ", "").strip()
                summa = int(summa)

                # Тарифы с НДС
                tariffs = {
                    180000: {"payment": 180000, "months": 1, "nds": 9000},
                    200000: {"payment": 25000, "months": 8, "nds": 10000},
                    240000: {"payment": 20000, "months": 12, "nds": 12000},
                    270000: {"payment": 15000, "months": 18, "nds": 13500},
                }

                if summa not in tariffs:
                    st.error("Некорректная сумма")
                else:
                    tariff = tariffs[summa]
                    payment = tariff["payment"]
                    months = tariff["months"]
                    nds = tariff["nds"]

                    # Парсинг даты договора
                    startdate = datetime.strptime(datezakl, "%d.%m.%Y")

                    # Генерация дат платежей
                    payment_dates = []
                    for i in range(months):
                        if i == 0:
                            paydate = datezakl
                        else:
                            year = (startdate.year * 12 + startdate.month + i - 1) // 12
                            month = (startdate.month + i - 1) % 12 + 1
                            paydate = f"10.{month:02d}.{year}"
                        payment_dates.append(paydate)

                    # Формирование контекста для шаблона
                    context = {
                        "contract_num": contractnum,
                        "date_zakl": datezakl,
                        "fio": fio,
                        "data_rod": datarod,
                        "passport": passport,
                        "summa": f"{summa:,}".replace(",", " "),
                        "summa2": nds,
                        "adres": adres,
                        "phone": phone,
                    }

                    # Добавляем даты и суммы платежей
                    for i in range(1, 21):
                        context[f"payment_date_{i}"] = (
                            payment_dates[i - 1] if i <= months else ""
                        )
                        context[f"payment_summa_{i}"] = payment if i <= months else ""

                    # Загрузка и заполнение шаблона
                    template_path = "Dogovor_BFL_RASSROChKA_ShABLON.docx"
                    doc = DocxTemplate(template_path)
                    doc.render(context)

                    # Возврат файла
                    output = io.BytesIO()
                    doc.save(output)
                    output.seek(0)

                    filename = f'{contractnum.replace("№", "")}.docx'
                    st.download_button(
                        label="Скачать договор",
                        data=output,
                        file_name=filename,
                        mime=(
                            "application/vnd.openxmlformats-officedocument"
                            ".wordprocessingml.document"
                        ),
                    )
                    st.success("✅ Договор готов к скачиванию!")

            except ValueError:
                st.error("Ошибка формата даты: используйте формат ДД.ММ.ГГГГ")
            except Exception as e:
                st.error(f"Ошибка: {str(e)}")





















