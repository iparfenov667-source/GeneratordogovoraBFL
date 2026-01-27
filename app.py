from flask import Flask, render_template_string, request, send_file
from docxtpl import DocxTemplate
from datetime import datetime
import io

app = Flask(__name__)

# HTML-шаблон с формой
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Генератор договора</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }
        h1 { text-align: center; color: #2c3e50; }
        label { display: block; margin-top: 15px; font-weight: bold; }
        input, textarea, select { width: 100%; padding: 10px; margin-top: 5px; box-sizing: border-box; border: 1px solid #ccc; border-radius: 4px; }
        button { display: block; width: 100%; padding: 12px; margin-top: 20px; background: #27ae60; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #219653; }
    </style>
</head>
<body>
    <h1>Генератор договора</h1>
    <form method="POST">
        <label>1) Номер договора (1765):</label>
        <input name="contractnum" placeholder="1765" required>

        <label>2) Дата договора (22.10.2025):</label>
        <input name="datezakl" placeholder="22.10.2025" required>

        <label>3) ФИО:</label>
        <input name="fio" placeholder="Парфенов Илья Алексеевич" required>

        <label>4) Дата рождения (25.05.2000):</label>
        <input name="datarod" placeholder="25.05.2000" required>

        <label>5) Паспорт (45 04 123456):</label>
        <input name="passport" placeholder="45 04 123456" required>

        <label>6) Стоимость услуг:</label>
        <select name="summa" required>
            <option value="">Выберите сумму</option>
            <option value="180000">180 000 ₽ (1 мес по 180 000 ₽)</option>
            <option value="200000">200 000 ₽ (8 мес по 25 000 ₽)</option>
            <option value="240000">240 000 ₽ (12 мес по 20 000 ₽)</option>
            <option value="270000">270 000 ₽ (18 мес по 15 000 ₽)</option>
        </select>

        <label>7) Адрес (г. Санкт-Петербург, ул. Затшига, д. 50, кв. 50):</label>
        <input name="adres" placeholder="г. Санкт-Петербург, ул. Затшига, д. 50, кв. 50" required>

        <label>8) Телефон (+7 901 943 53 21):</label>
        <input name="phone" placeholder="+79019435321" required>

        <button type="submit">Скачать .docx</button>
    </form>
</body>
</html>'''


@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/', methods=['POST'])
def generate():
    try:
        # Получаем данные из формы
        contractnum = request.form['contractnum'].replace(' ', '').strip()
        datezakl = request.form['datezakl'].strip()
        fio = request.form['fio'].strip()
        datarod = request.form['datarod'].strip()
        passport = request.form['passport'].strip()
        summa = int(request.form['summa'])
        adres = request.form['adres'].strip()
        phone = request.form['phone'].strip()

        # Тарифы с НДС (5%)
        tariffs = {
            180000: {'payment': 180000, 'months': 1, 'nds': 9000},
            200000: {'payment': 25000, 'months': 8, 'nds': 10000},
            240000: {'payment': 20000, 'months': 12, 'nds': 12000},
            270000: {'payment': 15000, 'months': 18, 'nds': 13500},
        }

        if summa not in tariffs:
            return 'Некорректная сумма', 400

        tariff = tariffs[summa]
        payment = tariff['payment']
        months = tariff['months']
        nds = tariff['nds']

        # Парсинг даты договора
        startdate = datetime.strptime(datezakl, '%d.%m.%Y')

        # Генерация дат платежей (1-й платеж — дата договора, далее 10-е число следующих месяцев)
        payment_dates = []
        for i in range(months):
            if i == 0:
                paydate = datezakl
            else:
                year = (startdate.year * 12 + startdate.month + i - 1) // 12
                month = (startdate.month + i - 1) % 12 + 1
                paydate = f'10.{month:02d}.{year}'
            payment_dates.append(paydate)

        # Формирование контекста для шаблона
        context = {
            'contract_num': contractnum,
            'date_zakl': datezakl,
            'fio': fio,
            'data_rod': datarod,
            'passport': passport,
            'summa': f'{summa:,}'.replace(',', ' '),
            'summa2': nds,
            'adres': adres,
            'phone': phone,
        }

        # Даты и суммы платежей (поддержка до 20 строк, в шаблоне задействовано до 18)
        for i in range(1, 21):
            context[f'payment_date_{i}'] = payment_dates[i - 1] if i <= months else ''
            context[f'payment_summa_{i}'] = payment if i <= months else ''

        # Загрузка и заполнение шаблона
        doc = DocxTemplate('Dogovor_BFL_RASSROChKA_ShABLON.docx')
        doc.render(context)

        # Возврат файла
        output = io.BytesIO()
        doc.save(output)
        output.seek(0)

        filename = f'{contractnum.replace("№", "")}.docx'
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return f'Ошибка: {str(e)}', 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
