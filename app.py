import streamlit as st
from docxtpl import DocxTemplate
from datetime import datetime
import io
import time
import random

st.set_page_config(page_title="Генератор договора", layout="wide")

# Синий королевский цвет
ROYAL_BLUE = "#4169E1"

# CSS для кастомизации
custom_css = f"""
<style>
    .header-royal {{
        color: {ROYAL_BLUE};
        text-align: center;
        font-weight: bold;
        font-size: 2.5em;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(65, 105, 225, 0.3);
    }}
    .blue-divider {{
        height: 3px;
        background: linear-gradient(90deg, {ROYAL_BLUE}, transparent);
        margin: 20px 0;
    }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Заголовок РАПИД ПРАВО
st.markdown('<div class="header-royal">🏛️ РАПИД ПРАВО 🏛️</div>', unsafe_allow_html=True)
st.markdown('<div class="blue-divider"></div>', unsafe_allow_html=True)

# Заголовок приложения
st.title("📄 Генератор договора поручения")
st.markdown(f"<p style='color: {ROYAL_BLUE}; font-size: 1.1em; font-weight: 500;'>Генератор договоров для Рапид Право</p>", unsafe_allow_html=True)
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
if st.button("🚀 Сгенерировать договор", use_container_width=True, key="generate_btn"):
    # Валидация
    if not all([contract_num, date_zakl, fio, data_rod, passport, summa_val, adres, phone]):
        st.error("❌ Заполните все поля")
    else:
        try:
            # Эпичная анимация при генерации
            with st.spinner('⚡ Вызываем магию договора...'):
                time.sleep(0.5)
            
            progress_placeholder = st.empty()
            status_placeholder = st.empty()
            
            # Анимационная полоса
            progress_bar = st.progress(0)
            
            animation_steps = [
                (0.2, "⚙️ Подготовка шаблона..."),
                (0.4, "🔧 Заполнение данных..."),
                (0.6, "✨ Применение магии..."),
                (0.8, "🎯 Финальные штрихи..."),
                (1.0, "🎉 Готово!")
            ]
            
            for progress, status in animation_steps:
                progress_bar.progress(progress)
                status_placeholder.info(f"🔹 {status}")
                time.sleep(0.3)
            
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
                
                # Очищаем статус
                progress_bar.empty()
                status_placeholder.empty()
                
                # Успешное завершение
    magic_messages = [
        "🪄 Магия, договор готов к скачиванию!",
        "😅 Ну ты и ленивый, что сам не мог договор заполнить, ладно я тебе в последний раз помогаю",
        "✨ Чудо! Договор готов! (Может быть это и не чудо, но давай поверим)",
        "🎉 Viola! Договор готов к скачиванию! (Это французское слово, звучит более красиво)",
        "💫 Магия случилась! Договор готов к скачиванию, и это не шутка!",
        "🚀 Ракета запущена! Договор готов к скачиванию!",
        "🧙 Абракадабра! Договор готов к скачиванию!",
        "⚡ Бац! Договор готов к скачиванию!",
        "🌟 Звёзды сошлись! Договор готов к скачиванию!",
        "🎭 Как по волшебству! Договор готов к скачиванию!",
    ]
    st.success(random.choice(magic_messages))                st.download_button(
                    label="📥 Скачать договор",
                    data=output.getvalue(),
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )

    except Exception as e:
        pass
        except ValueError as e:
            st.error(f"❌ Ошибка в формате данных: {str(e)}")
        except Exception as e:
