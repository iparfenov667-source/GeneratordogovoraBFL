import streamlit as st
from docxtpl import DocxTemplate
from datetime import datetime
import io

st.set_page_config(page_title="Генератор договора", layout="wide")

# Заголовок приложения
st.title("📄 Генератор договора поручения")
st.markdown("Генератор договоров для Рапид Право")
st.divider()

# Два столбца для формы
col1, col2 = st.columns(2)

with col1:
    # Номер договора
    contract_num = st.text_input(
        "1️⃣ Номер договора",
        placeholder="№1765",
        help="Введите номер договора (без символа №)"
    ).replace('№', '').strip()

    # Дата договора
    date_zakl = st.text_input(
        "2️⃣ Дата договора",
        placeholder="22.10.2025",
        help="Формат: ДД.МММ.ГГГГ"
    )

    # ФИО клиента
    fio = st.text_input(
        "3️⃣ ФИО клиента",
        placeholder="Парфенов Илья Алексеевич"
    )

    # Дата рождения
    data_rod = st.text_input(
        "4️⃣ Дата рождения",
        placeholder="25.05.2000"
    )

with col2:
    # Паспорт
    passport = st.text_input(
        "5️⃣ Серия и номер паспорта",
        placeholder="45 04 123456"
    )

    # Стоимость (тариф)
    summa = st.selectbox(
        "6️⃣ Стоимость (выберите тариф)",
        options=[
                        (150000, "150 000 ₽ (единоразовый платеж)"),
            (180000, "180 000 ₽ (9 мес по 20 000 ₽)"),
            (210000, "210 000 ₽ (12 мес по 17 500 ₽)"),
            (240000, "240 000 ₽ (16 мес по 15 000 ₽)"),
            (260000, "260 000 ₽ (20 мес по 13 000 ₽)")
        ],
        format_func=lambda x: x[1]
    )
    summa_val = summa[0] if summa else None

    # Адрес регистрации
    adres = st.text_input(
        "7️⃣ Адрес регистрации",
        placeholder="г. Санкт-Петербург, ул. Затшига, д. 50, кв. 50"
    )

    # Номер телефона
    phone = st.text_input(
        "8️⃣ Номер телефона",
        placeholder="+79019435321"
    )

st.divider()

# Кнопка генерации
if st.button("🚀 Сгенерировать договор", use_container_width=True):
    # Валидация
    if not all([contract_num, date_zakl, fio, data_rod, passport, summa_val, adres, phone]):
        st.error("❌ Заполните все поля")
    else:
        try:
            # Тарифы
            tariffs = {
                                150000: {"payment": 150000, "months": 1},
                180000: {"payment": 20000, "months": 9},
                210000: {"payment": 17500, "months": 12},
                240000: {"payment": 15000, "months": 16},
                260000: {"payment": 13000, "months": 20},
            }

            if summa_val not in tariffs:
                st.error("❌ Недопустимая стоимость")
            else:
                tariff = tariffs[summa_val]
                payment = tariff["payment"]
                months = tariff["months"]

                # Генерация дат платежей
                start_date = datetime.strptime(date_zakl, "%d.%m.%Y")
                payment_dates = []
                for i in range(months):
                    if i == 0:
                        pay_date = date_zakl
                    else:
                        year = start_date.year + (start_date.month + i - 1) // 12
                        month = (start_date.month + i - 1) % 12 + 1
                        pay_date = f"10.{month:02d}.{year}"
                    payment_dates.append(pay_date)

                # Контекст для шаблона
                context = {
                    "contract_num": contract_num,
                    "date_zakl": date_zakl,
                    "fio": fio,
                    "data_rod": data_rod,
                    "passport": passport,
                    "summa": f"{summa_val:,}".replace(",", " "),
                    "adres": adres,
                    "phone": phone,
                }
                for i in range(1, 21):
                    context[f"payment_date_{i}"] = payment_dates[i - 1] if i <= months else ""
                    context[f"payment_summa_{i}"] = payment if i <= months else ""

                # Генерация документа
                doc = DocxTemplate("Dogovor_BFL_RASSROChKA_ShABLON.docx")
                doc.render(context)
                output = io.BytesIO()
                doc.save(output)
                output.seek(0)

                filename = f"Договор_№{contract_num}.docx"

                st.success("✅ Договор готов!")
                st.download_button(
                    label="📥 Скачать договор",
                    data=output.getvalue(),
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )

        except ValueError as e:
            st.error(f"❌ Ошибка в формате данных: {str(e)}")
        except Exception as e:
            st.error(f"❌ Ошибка: {str(e)}")

