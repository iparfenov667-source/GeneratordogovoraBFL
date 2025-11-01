from flask import Flask, render_template_string, request, send_file
from docxtpl import DocxTemplate
from datetime import datetime
import io
import re

app = Flask(__name__)

# HTML-шаблон с формой
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>Генератор договоров «Рапид Право»</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }
    h1 { text-align: center; color: #2c3e50; }
    label { display: block; margin-top: 15px; font-weight: bold; }
    input, textarea { width: 100%; padding: 10px; margin-top: 5px; box-sizing: border-box; border: 1px solid #ccc; border-radius: 4px; }
    button { display: block; width: 100%; padding: 12px; margin-top: 20px; background: #27ae60; color: white; border: none; border-radius: 4px; cursor: pointer; }
    button:hover { background: #219653; }
  </style>
</head>
<body>
  <h1>📄 Генератор договора поручения</h1>
  <form method="POST">
    <label>1) Номер договора (например, №1765)</label>
    <input name="contract_num" placeholder="№1765" required>

    <label>2) Дата договора (например, 22.10.2025)</label>
    <input name="date_zakl" placeholder="22.10.2025" required>

    <label>3) ФИО клиента</label>
    <input name="fio" placeholder="Парфенов Илья Алексеевич" required>

    <label>4) Дата рождения</label>
    <input name="data_rod" placeholder="25.05.2000" required>

    <label>5) Серия и номер паспорта</label>
    <input name="passport" placeholder="45 04 123456" required>

    <label>6) Стоимость (выберите тариф)</label>
    <select name="summa" required>
      <option value="">— Выберите —</option>
      <option value="180000">180 000 ₽ (9 мес по 20 000 ₽)</option>
      <option value="210000">210 000 ₽ (12 мес по 17 500 ₽)</option>
      <option value="240000">240 000 ₽ (16 мес по 15 000 ₽)</option>
      <option value="260000">260 000 ₽ (20 мес по 13 000 ₽)</option>
    </select>

    <label>7) Адрес регистрации</label>
    <input name="adres" placeholder="г. Санкт-Петербург, ул. Затшига, д. 50, кв. 50" required>

    <label>8) Номер телефона</label>
    <input name="phone" placeholder="+79019435321" required>

    <button type="submit">Сгенерировать договор (.docx)</button>
  </form>
</body>
</html>
'''

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/', methods=['POST'])
def generate():
    try:
        # Получаем данные из формы
        contract_num = request.form['contract_num'].replace('№', '').strip()
        date_zakl = request.form['date_zakl']
        fio = request.form['fio']
        data_rod = request.form['data_rod']
        passport = request.form['passport']
        summa = int(request.form['summa'])
        adres = request.form['adres']
        phone = request.form['phone']

        # Тарифы
        tariffs = {
            180000: {"payment": 20000, "months": 9},
            210000: {"payment": 17500, "months": 12},
            240000: {"payment": 15000, "months": 16},
            260000: {"payment": 13000, "months": 20},
        }

        if summa not in tariffs:
            return "❌ Недопустимая стоимость", 400

        tariff = tariffs[summa]
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
            "summa": f"{summa:,}".replace(",", " "),
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
        return send_file(
            output,
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return f"❌ Ошибка: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
